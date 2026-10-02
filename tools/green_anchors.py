"""Grünflächen-Anker aus OpenStreetMap-Extrakten (PBF) vorberechnen – ohne externe Abhängigkeiten.

Aufruf:
    python3 tools/green_anchors.py --regions data/regions.json --out data/green
    python3 tools/green_anchors.py --pbf datei.osm.pbf --name Test --out /tmp/green   # einzelne Datei

Ergebnis: Kacheln data/green/<y>_<x>.json (Raster 0,05° × 0,08°, wie in app.js) mit Ankern
[lon, lat, wert, flächen-index] und Flächen [id, name]; dazu data/green/index.json.
Die Anker-Logik entspricht anchorsFrom() in app.js: Punkte in Grünflächen ab 1 ha, Uferpunkte an
Gewässern ab 2 ha, Punkte entlang von Flüssen und Kanälen.
"""
import argparse
import json
import math
import os
import struct
import sys
import time
import urllib.request
import zlib

TILE_LAT, TILE_LON = 0.05, 0.08
GREEN_LEISURE = {"park", "garden", "nature_reserve", "recreation_ground"}
GREEN_LANDUSE = {"forest", "allotments", "recreation_ground", "village_green", "meadow"}
GREEN_NATURAL = {"wood", "heath"}
LINE_WATERWAY = {"river", "canal"}


# ---------- Protobuf / PBF ----------
def varint(b, p):
    r = s = 0
    while True:
        x = b[p]
        p += 1
        r |= (x & 0x7F) << s
        if x < 0x80:
            return r, p
        s += 7


def zz(n):
    return (n >> 1) ^ -(n & 1)


def packed(b, start, end):
    out, p = [], start
    while p < end:
        r = s = 0
        while True:
            x = b[p]
            p += 1
            r |= (x & 0x7F) << s
            if x < 0x80:
                break
            s += 7
        out.append(r)
    return out


def fields(b, start=0, end=None):
    """Iteriert (feld, wiretyp, wert_oder_(start, ende))."""
    p, end = start, len(b) if end is None else end
    while p < end:
        key, p = varint(b, p)
        f, wt = key >> 3, key & 7
        if wt == 0:
            v, p = varint(b, p)
            yield f, 0, v
        elif wt == 2:
            n, p = varint(b, p)
            yield f, 2, (p, p + n)
            p += n
        elif wt == 1:
            p += 8
        elif wt == 5:
            p += 4
        else:
            raise ValueError("wiretype %d" % wt)


def blocks(path):
    """Liefert (typ, daten) je Blob einer PBF-Datei."""
    with open(path, "rb") as fh:
        while True:
            hl = fh.read(4)
            if len(hl) < 4:
                return
            hb = fh.read(struct.unpack(">I", hl)[0])
            typ, size = "", 0
            for f, wt, v in fields(hb):
                if f == 1:
                    typ = hb[v[0]:v[1]].decode()
                elif f == 3:
                    size = v
            blob = fh.read(size)
            raw = None
            for f, wt, v in fields(blob):
                if f == 1:
                    raw = blob[v[0]:v[1]]
                elif f == 3:
                    raw = zlib.decompress(blob[v[0]:v[1]])
            yield typ, raw


def header_bbox(path):
    for typ, d in blocks(path):
        if typ == "OSMHeader":
            for f, wt, v in fields(d):
                if f == 1:
                    bb = {}
                    for g, w2, val in fields(d, *v):
                        bb[g] = zz(val) * 1e-9
                    if len(bb) == 4:
                        return {"w": bb[1], "e": bb[2], "n": bb[3], "s": bb[4]}
        return None


def primitive_block(d):
    st, groups, gran, lat_off, lon_off = [], [], 100, 0, 0
    for f, wt, v in fields(d):
        if f == 1:
            st = [d[a:b].decode("utf-8", "replace") for g, w2, (a, b) in fields(d, *v) if g == 1]
        elif f == 2:
            groups.append(v)
        elif f == 17:
            gran = v
        elif f == 19:
            lat_off = v
        elif f == 20:
            lon_off = v
    return st, groups, gran, lat_off, lon_off


def tags_of(keys, vals, st):
    return {st[k]: st[v] for k, v in zip(keys, vals)}


def scan(path, want_relations=False, want_ways=None, want_nodes=None):
    """Ein Durchlauf; liefert je nach Wunsch Relationen, Wege (want_ways = Filter(id, tags)) oder
    Knotenkoordinaten (für die Menge want_nodes)."""
    rels, ways, coords = [], [], {}
    for typ, d in blocks(path):
        if typ != "OSMData":
            continue
        st, groups, gran, lat_off, lon_off = primitive_block(d)
        for ga, gb in groups:
            for f, wt, v in fields(d, ga, gb):
                if f == 2 and want_nodes is not None:
                    ids = lats = lons = None
                    for g, w2, (a, b) in fields(d, *v):
                        if g == 1:
                            ids = packed(d, a, b)
                        elif g == 8:
                            lats = packed(d, a, b)
                        elif g == 9:
                            lons = packed(d, a, b)
                    if not ids:
                        continue
                    i = la = lo = 0
                    for k in range(len(ids)):
                        i += zz(ids[k])
                        la += zz(lats[k])
                        lo += zz(lons[k])
                        if i in want_nodes:
                            coords[i] = ((lon_off + gran * lo) * 1e-9, (lat_off + gran * la) * 1e-9)
                elif f == 3 and want_ways:
                    wid, keys, vals, ref_span = 0, [], [], None
                    for g, w2, val in fields(d, *v):
                        if g == 1:
                            wid = val
                        elif g == 2:
                            keys = packed(d, *val)
                        elif g == 3:
                            vals = packed(d, *val)
                        elif g == 8:
                            ref_span = val
                    t = tags_of(keys, vals, st)
                    if not want_ways(wid, t) or not ref_span:
                        continue
                    refs, r = [], 0
                    for x in packed(d, *ref_span):
                        r += zz(x)
                        refs.append(r)
                    ways.append((wid, t, refs))
                elif f == 4 and want_relations:
                    rid, keys, vals, roles, mem, types = 0, [], [], [], [], []
                    for g, w2, val in fields(d, *v):
                        if g == 1:
                            rid = val
                        elif g == 2:
                            keys = packed(d, *val)
                        elif g == 3:
                            vals = packed(d, *val)
                        elif g == 8:
                            roles = packed(d, *val)
                        elif g == 9:
                            r = 0
                            for x in packed(d, *val):
                                r += zz(x)
                                mem.append(r)
                        elif g == 10:
                            types = packed(d, *val)
                    rels.append((rid, tags_of(keys, vals, st), [(m, t, st[ro]) for m, t, ro in zip(mem, types, roles)]))
    return rels, ways, coords


# ---------- Klassifizierung ----------
def kind_of(t, line_ok):
    if t.get("access") in ("private", "no"):
        return None
    if line_ok and t.get("waterway") in LINE_WATERWAY:
        return "line"
    if t.get("natural") == "water":
        return "water"
    if t.get("leisure") in GREEN_LEISURE or t.get("landuse") in GREEN_LANDUSE or t.get("natural") in GREEN_NATURAL:
        return "green"
    return None


# ---------- Geometrie (lokale Projektion in Metern) ----------
class Proj:
    def __init__(self, lat0, lon0):
        self.lat0, self.lon0, self.k = lat0, lon0, 111320.0
        self.kx = self.k * math.cos(math.radians(lat0))

    def to(self, lon, lat):
        return ((lon - self.lon0) * self.kx, (lat - self.lat0) * self.k)

    def back(self, x, y):
        return (self.lon0 + x / self.kx, self.lat0 + y / self.k)


def shoelace(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def centroid(r):
    a = shoelace(r)
    if abs(a) < 1:
        return (sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r))
    cx = cy = 0.0
    for i in range(len(r)):
        x0, y0 = r[i]
        x1, y1 = r[(i + 1) % len(r)]
        k = x0 * y1 - x1 * y0
        cx += (x0 + x1) * k
        cy += (y0 + y1) * k
    return (cx / (6 * a), cy / (6 * a))


def inside(r, p):
    c, j = False, len(r) - 1
    for i in range(len(r)):
        if (r[i][1] > p[1]) != (r[j][1] > p[1]) and p[0] < (r[j][0] - r[i][0]) * (p[1] - r[i][1]) / (r[j][1] - r[i][1]) + r[i][0]:
            c = not c
        j = i
    return c


def sample(pts, step):
    out, acc = [pts[0]], 0.0
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        d = math.hypot(x1 - x0, y1 - y0)
        t = step - acc
        while t <= d and d > 0:
            out.append((x0 + (x1 - x0) * t / d, y0 + (y1 - y0) * t / d))
            t += step
        acc = (acc + d) % step
    return out


def length(pts):
    return sum(math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) for i in range(1, len(pts)))


def assemble(lines):
    """Fügt Wegstücke zu Ringen zusammen (über gemeinsame Endpunkte); offene Reste bleiben Linien."""
    lines = [list(l) for l in lines if len(l) >= 2]
    rings, open_ = [], []
    while lines:
        cur = lines.pop()
        changed = True
        while cur[0] != cur[-1] and changed:
            changed = False
            for i, l in enumerate(lines):
                if l[0] == cur[-1]:
                    cur += l[1:]
                elif l[-1] == cur[-1]:
                    cur += l[::-1][1:]
                elif l[-1] == cur[0]:
                    cur = l[:-1] + cur
                elif l[0] == cur[0]:
                    cur = l[::-1][:-1] + cur
                else:
                    continue
                lines.pop(i)
                changed = True
                break
        (rings if cur[0] == cur[-1] and len(cur) >= 4 else open_).append(cur)
    return rings, open_


def anchors_for(feature, proj):
    """Wie anchorsFrom() in app.js. Liefert [(x, y, wert)]."""
    kind, rings, lines = feature["kind"], feature["rings"], feature["lines"]
    out = []
    if kind == "line":
        allp = [[proj.to(*c) for c in l] for l in lines]
        if sum(length(l) for l in allp) < 400:
            return out
        for l in allp:
            out += [(x, y, 1.2) for x, y in sample(l, 350)]
        return out
    if not rings:
        return out
    pr = [[proj.to(*c) for c in r] for r in rings]
    area = sum(abs(shoelace(r)) for r in pr)
    ring = max(pr, key=len)
    c = centroid(ring)
    if kind == "water":
        if area < 20000:
            return out
        for x, y in sample(ring, 350):
            d = math.hypot(x - c[0], y - c[1]) or 1
            out.append((x + (x - c[0]) / d * 20, y + (y - c[1]) / d * 20, 1.5))
        return out
    if area < 10000:
        return out
    ha, pts = area / 1e4, []
    if inside(ring, c):
        pts.append(c)
    if ha >= 8:
        for x, y in sample(ring, 450):
            p = ((x * 2 + c[0]) / 3, (y * 2 + c[1]) / 3)
            if inside(ring, p):
                pts.append(p)
    if not pts:
        return out
    v = max(0.6, min(4.0, math.sqrt(ha)) / math.sqrt(len(pts)))
    return [(x, y, v) for x, y in pts]


# ---------- Region verarbeiten ----------
def process(pbf, name, log=print):
    t0 = time.time()
    rels, _, _ = scan(pbf, want_relations=True)
    feats, member_ways = [], {}
    for rid, t, mem in rels:
        if t.get("type") not in ("multipolygon", "boundary"):
            continue
        k = kind_of(t, line_ok=False)
        if not k:
            continue
        outers = [m for m, typ, role in mem if typ == 1 and role != "inner"]
        if outers:
            feats.append({"id": "r%d" % rid, "name": t.get("name", ""), "kind": k, "ways": outers})
            for w in outers:
                member_ways[w] = None
    log(f"{name}: {len(feats)} Relationen ({time.time() - t0:.0f} s)")
    _, ways, _ = scan(pbf, want_ways=lambda wid, t: wid in member_ways or kind_of(t, line_ok=True) is not None)
    need = set()
    for wid, t, refs in ways:
        if wid in member_ways:
            member_ways[wid] = refs
            need.update(refs)
        k = kind_of(t, line_ok=True)
        if k:
            feats.append({"id": "w%d" % wid, "name": t.get("name", ""), "kind": k, "refs": refs})
            need.update(refs)
    del ways
    log(f"{name}: {len(feats)} Flächen/Linien, {len(need)} Knoten nötig ({time.time() - t0:.0f} s)")
    _, _, coords = scan(pbf, want_nodes=need)
    log(f"{name}: Koordinaten gelesen ({time.time() - t0:.0f} s)")
    anchors, names = [], {}
    lat0 = sum(c[1] for c in list(coords.values())[:1000]) / max(1, min(1000, len(coords)))
    lon0 = sum(c[0] for c in list(coords.values())[:1000]) / max(1, min(1000, len(coords)))
    proj = Proj(lat0, lon0)
    for F in feats:
        if "refs" in F:
            pts = [coords[r] for r in F["refs"] if r in coords]
            if len(pts) < 2:
                continue
            if F["kind"] == "line" or pts[0] != pts[-1]:
                F["rings"], F["lines"] = ([], [pts]) if F["kind"] == "line" else ([], [])
            else:
                F["rings"], F["lines"] = [pts], []
        else:
            parts = [[coords[r] for r in member_ways.get(w) or [] if r in coords] for w in F["ways"]]
            F["rings"], F["lines"] = assemble(parts)
        for x, y, v in anchors_for(F, proj):
            anchors.append((x, y, v, F["id"]))
            names[F["id"]] = F["name"]
    # Dubletten unter 150 m zusammenfassen (höheren Wert behalten), über ein Raster
    anchors.sort(key=lambda a: -a[2])
    grid, kept = {}, []
    for a in anchors:
        gx, gy = int(a[0] // 150), int(a[1] // 150)
        if any(math.hypot(a[0] - b[0], a[1] - b[1]) < 150 for i in (-1, 0, 1) for j in (-1, 0, 1) for b in grid.get((gx + i, gy + j), [])):
            continue
        grid.setdefault((gx, gy), []).append(a)
        kept.append(a)
    log(f"{name}: {len(kept)} Anker ({time.time() - t0:.0f} s)")
    return [(proj.back(a[0], a[1]), a[2], a[3]) for a in kept], names


def write_tiles(results, out):
    tiles = {}
    for (lon, lat), v, fid, name in results:
        key = "%d_%d" % (math.floor(lat / TILE_LAT), math.floor(lon / TILE_LON))
        tiles.setdefault(key, []).append((round(lon, 5), round(lat, 5), round(v, 2), fid, name))
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".json"):
            os.remove(os.path.join(out, f))
    for key, items in tiles.items():
        fids, idx = [], {}
        rows = []
        for lon, lat, v, fid, name in items:
            if fid not in idx:
                idx[fid] = len(fids)
                fids.append([fid, name])
            rows.append([lon, lat, v, idx[fid]])
        with open(os.path.join(out, key + ".json"), "w") as fh:
            json.dump({"v": 1, "a": rows, "f": fids}, fh, ensure_ascii=False, separators=(",", ":"))
    return sorted(tiles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regions", help="JSON-Liste [{name, pbf}] (pbf als URL oder Pfad)")
    ap.add_argument("--pbf")
    ap.add_argument("--name", default="Region")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=os.path.join(os.path.expanduser("~"), ".cache", "green-pbf"))
    a = ap.parse_args()
    regions = json.load(open(a.regions)) if a.regions else [{"name": a.name, "pbf": a.pbf}]
    allres, meta = [], []
    for r in regions:
        path = r["pbf"]
        if path.startswith("http"):
            os.makedirs(a.cache, exist_ok=True)
            local = os.path.join(a.cache, os.path.basename(path))
            if not os.path.exists(local):
                req = urllib.request.Request(path, headers={"User-Agent": "laufrouten-green-anchors"})
                with urllib.request.urlopen(req, timeout=600) as resp, open(local, "wb") as fh:
                    fh.write(resp.read())
            path = local
        res, names = process(path, r["name"])
        allres += [(ll, v, fid, names.get(fid, "")) for ll, v, fid in res]
        meta.append({"name": r["name"], "bbox": header_bbox(path), "anchors": len(res)})
    keys = write_tiles(allres, a.out)
    with open(os.path.join(a.out, "index.json"), "w") as fh:
        json.dump({"v": 1, "tile": [TILE_LAT, TILE_LON], "generated": time.strftime("%Y-%m-%d"), "regions": meta, "tiles": keys},
                  fh, ensure_ascii=False, indent=1)
    print(f"{len(keys)} Kacheln, {len(allres)} Anker -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
