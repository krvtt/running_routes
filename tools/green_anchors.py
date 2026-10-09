"""Grünflächen-Anker aus OpenStreetMap-Extrakten (PBF) vorberechnen – ohne externe Abhängigkeiten.

Aufruf:
    python3 tools/green_anchors.py --regions data/regions.json --out data/green
    python3 tools/green_anchors.py --pbf datei.osm.pbf --name Test --out /tmp/green   # einzelne Datei

Ergebnis: Kacheln data/green/<y>_<x>.json (Raster 0,05° × 0,08°, wie in app.js); dazu data/green/index.json.
  a: Anker [lon, lat, wert, flächen-index] – wie anchorsFrom() in app.js: Punkte in Grünflächen ab 1 ha,
     Uferpunkte an Gewässern ab 2 ha, Punkte entlang von Flüssen und Kanälen.
  r: Parkrunden [flächen-index, länge_m, abdeckung, art (0 Grün, 1 See), ha, punkte, auf_weg] – der Umriss einer Grünfläche (ab 0,5 ha)
     oder eines Sees (ab 1 ha), alle 25 m auf den nächsten passenden Fußweg eingerastet: in Parks auf Wege im
     Inneren, an Seen auf Uferwege außerhalb des Wassers. Abdeckung = Anteil der Umrisspunkte mit Weg.
     Punkte als ganze Zahlen in 1e-5 Grad: erster Punkt absolut, danach Differenzen (lon, lat abwechselnd);
     auf_weg: je Punkt "1" (liegt auf einem Weg) oder "0" (kein Weg gefunden).
  f: Flächen [id, name]
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
FOOT_HIGHWAY = {"footway", "path", "track", "pedestrian", "bridleway", "cycleway"}
LOOP_STEP = 25          # Abstand der Umrisspunkte (m)
LOOP_REACH = {"green": 70, "water": 90}   # Suchradius für den Weg (m)


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


def is_foot(t):
    """Fußweg im Grünen (keine Gehwege an Straßen, keine gesperrten Wege)."""
    if t.get("highway") not in FOOT_HIGHWAY or t.get("footway") in ("sidewalk", "crossing"):
        return False
    if t.get("foot") in ("no", "private", "use_sidepath"):
        return False
    if t.get("access") in ("private", "no") and t.get("foot") not in ("yes", "designated", "permissive"):
        return False
    return not (t.get("highway") == "cycleway" and t.get("foot") not in ("yes", "designated", "permissive"))


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


# ---------- Parkrunden: Umriss auf Fußwege einrasten ----------
class SegGrid:
    """Raster (50 m) über alle Fußweg-Abschnitte für die Nächster-Weg-Suche."""
    CELL = 50.0

    def __init__(self):
        self.cells = {}
        self.n = 0

    def add(self, a, b):
        c = self.CELL
        seg = (a[0], a[1], b[0], b[1])
        for gx in range(int(min(a[0], b[0]) // c), int(max(a[0], b[0]) // c) + 1):
            for gy in range(int(min(a[1], b[1]) // c), int(max(a[1], b[1]) // c) + 1):
                self.cells.setdefault((gx, gy), []).append(seg)
        self.n += 1

    def near(self, x, y, r):
        c, seen = self.CELL, set()
        for gx in range(int((x - r) // c), int((x + r) // c) + 1):
            for gy in range(int((y - r) // c), int((y + r) // c) + 1):
                for s in self.cells.get((gx, gy), ()):
                    if s not in seen:
                        seen.add(s)
                        yield s


def closest(s, x, y):
    ax, ay, bx, by = s
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
    qx, qy = ax + t * dx, ay + t * dy
    return qx, qy, math.hypot(x - qx, y - qy), dx, dy, math.sqrt(L2)


def sample_tangent(pts, step):
    """Punkte im Abstand step entlang eines geschlossenen Linienzugs, mit Einheits-Tangente."""
    out, acc = [], 0.0
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        d = math.hypot(x1 - x0, y1 - y0)
        if d == 0:
            continue
        t = (step - acc) % step
        while t < d:
            out.append((x0 + (x1 - x0) * t / d, y0 + (y1 - y0) * t / d, (x1 - x0) / d, (y1 - y0) / d))
            t += step
        acc = (acc + d) % step
    return out


def simplify(pts, tol):
    """Douglas-Peucker für einen offenen Linienzug."""
    if len(pts) < 3:
        return list(pts)
    keep, stack = {0, len(pts) - 1}, [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        ax, ay, bx, by = pts[i][0], pts[i][1], pts[j][0], pts[j][1]
        best, bi = 0.0, -1
        for k in range(i + 1, j):
            d = closest((ax, ay, bx, by), pts[k][0], pts[k][1])[2]
            if d > best:
                best, bi = d, k
        if bi > 0 and best > tol:
            keep.add(bi)
            stack += [(i, bi), (bi, j)]
    return [pts[k] for k in sorted(keep)]


def loop_for(ring, kind, grid):
    """Parkrunde zu einem Umriss: [(x, y, auf_weg)] geschlossen, Länge, Abdeckung, Fläche – oder None."""
    area, per = abs(shoelace(ring)), length(ring + ring[:1])
    if area < (5000 if kind == "green" else 10000) or per > 15000 or per < 250:
        return None
    if 4 * math.pi * area / per ** 2 < (0.04 if kind == "green" else 0.08):  # lange, schmale Flächen (Flüsse) nicht
        return None
    pts = ring if shoelace(ring) > 0 else ring[::-1]  # gegen den Uhrzeigersinn: innen = links
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    reach, out, hit = LOOP_REACH[kind], [], 0
    samples = sample_tangent(pts, LOOP_STEP)
    if len(samples) < 8:
        return None
    for x, y, tx, ty in samples:
        cands = []
        for s in grid.near(x, y, reach):
            qx, qy, d, dx, dy, ln = closest(s, x, y)
            if d > reach or ln == 0:
                continue
            cands.append((d + 25 * (1 - abs(dx * tx + dy * ty) / ln), d, qx, qy))  # parallele Wege bevorzugen
        cands.sort()
        snap = None
        for score, d, qx, qy in cands[:6]:
            ins = inside(pts, (qx, qy))
            if (kind == "green" and (ins or d <= 12)) or (kind == "water" and not ins):
                snap = (qx, qy)
                break
        if snap:
            out.append((snap[0], snap[1], 1))
            hit += 1
        else:  # kein Weg: Umriss 15 m nach innen (Park) bzw. 20 m nach außen (See)
            k = 15 if kind == "green" else -20
            out.append((x - ty * k, y + tx * k, 0))
    cov = hit / len(samples)
    if cov < 0.5:
        return None
    line = simplify(out + out[:1], 6)
    return line, length(line), cov, area


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
    _, ways, _ = scan(pbf, want_ways=lambda wid, t: wid in member_ways or kind_of(t, line_ok=True) is not None or is_foot(t))
    need, foot = set(), []
    for wid, t, refs in ways:
        if wid in member_ways:
            member_ways[wid] = refs
            need.update(refs)
        k = kind_of(t, line_ok=True)
        if k:
            feats.append({"id": "w%d" % wid, "name": t.get("name", ""), "kind": k, "refs": refs})
            need.update(refs)
        if is_foot(t):
            foot.append(refs)
            need.update(refs)
    del ways
    log(f"{name}: {len(feats)} Flächen/Linien, {len(foot)} Fußwege, {len(need)} Knoten nötig ({time.time() - t0:.0f} s)")
    _, _, coords = scan(pbf, want_nodes=need)
    log(f"{name}: Koordinaten gelesen ({time.time() - t0:.0f} s)")
    anchors, names, loops = [], {}, []
    lat0 = sum(c[1] for c in list(coords.values())[:1000]) / max(1, min(1000, len(coords)))
    lon0 = sum(c[0] for c in list(coords.values())[:1000]) / max(1, min(1000, len(coords)))
    proj = Proj(lat0, lon0)
    grid = SegGrid()
    for refs in foot:
        pts = [proj.to(*coords[r]) for r in refs if r in coords]
        for a, b in zip(pts, pts[1:]):
            grid.add(a, b)
    del foot
    log(f"{name}: {grid.n} Wegabschnitte im Raster ({time.time() - t0:.0f} s)")
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
        if F["kind"] in ("green", "water"):
            rings = sorted(([proj.to(*c) for c in r] for r in F["rings"]), key=lambda r: -abs(shoelace(r)))[:3]
            for r in rings:
                lp = loop_for(r, F["kind"], grid)
                if lp:
                    line, per, cov, area = lp
                    loops.append(([proj.back(x, y) + (f,) for x, y, f in line], round(per), round(cov, 2), F["kind"], round(area / 1e4, 1), F["id"]))
                    names[F["id"]] = F["name"]
    # Dubletten unter 150 m zusammenfassen (höheren Wert behalten), über ein Raster
    anchors.sort(key=lambda a: -a[2])
    grid_a, kept = {}, []
    for a in anchors:
        gx, gy = int(a[0] // 150), int(a[1] // 150)
        if any(math.hypot(a[0] - b[0], a[1] - b[1]) < 150 for i in (-1, 0, 1) for j in (-1, 0, 1) for b in grid_a.get((gx + i, gy + j), [])):
            continue
        grid_a.setdefault((gx, gy), []).append(a)
        kept.append(a)
    log(f"{name}: {len(kept)} Anker, {len(loops)} Parkrunden ({time.time() - t0:.0f} s)")
    return [(proj.back(a[0], a[1]), a[2], a[3]) for a in kept], names, loops


def write_tiles(results, loops, out):
    """results: [((lon, lat), wert, fid, name)], loops: [(punkte, länge, abdeckung, art, ha, fid, name)]."""
    tiles = {}
    tkey = lambda lon, lat: "%d_%d" % (math.floor(lat / TILE_LAT), math.floor(lon / TILE_LON))  # noqa: E731
    for (lon, lat), v, fid, name in results:
        tiles.setdefault(tkey(lon, lat), {"a": [], "r": []})["a"].append((round(lon, 5), round(lat, 5), round(v, 2), fid, name))
    for pts, per, cov, kind, ha, fid, name in loops:
        clon, clat = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)  # Kachel nach Mittelpunkt
        flat, px, py = [], 0, 0
        for lon, lat, _ in pts:
            x, y = round(lon * 1e5), round(lat * 1e5)
            flat += [x - px, y - py]
            px, py = x, y
        onway = "".join(str(f) for _, _, f in pts)
        tiles.setdefault(tkey(clon, clat), {"a": [], "r": []})["r"].append((fid, name, per, cov, 1 if kind == "water" else 0, ha, flat, onway))
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".json"):
            os.remove(os.path.join(out, f))
    for key, t in tiles.items():
        fids, idx = [], {}

        def fi(fid, name):
            if fid not in idx:
                idx[fid] = len(fids)
                fids.append([fid, name])
            return idx[fid]
        rows = [[lon, lat, v, fi(fid, name)] for lon, lat, v, fid, name in t["a"]]
        rr = [[fi(fid, name), per, cov, kind, ha, flat, onway] for fid, name, per, cov, kind, ha, flat, onway in t["r"]]
        with open(os.path.join(out, key + ".json"), "w") as fh:
            json.dump({"v": 2, "a": rows, "r": rr, "f": fids}, fh, ensure_ascii=False, separators=(",", ":"))
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
    allres, allloops, meta = [], [], []
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
        res, names, loops = process(path, r["name"])
        allres += [(ll, v, fid, names.get(fid, "")) for ll, v, fid in res]
        allloops += [lp + (names.get(lp[5], ""),) for lp in loops]
        meta.append({"name": r["name"], "bbox": header_bbox(path), "anchors": len(res), "loops": len(loops)})
    keys = write_tiles(allres, allloops, a.out)
    with open(os.path.join(a.out, "index.json"), "w") as fh:
        json.dump({"v": 2, "tile": [TILE_LAT, TILE_LON], "generated": time.strftime("%Y-%m-%d"), "regions": meta, "tiles": keys},
                  fh, ensure_ascii=False, indent=1)
    print(f"{len(keys)} Kacheln, {len(allres)} Anker, {len(allloops)} Parkrunden -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
