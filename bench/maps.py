"""Karten zum Benchmark: je Fall die Varianten der neuen und einer Vergleichsversion auf einem OpenStreetMap-Ausschnitt.

Aufruf (nach bench/run.py):
    python3 bench/maps.py --routes bench-out/routes.json --osm <ordner mit .osm.pbf> --green data/green --out bench-out/maps

Benötigt osmium-tool (Ausschnitt und Export der Kartendaten) und matplotlib. Die erste Variante ist nach Wegart
eingefärbt (grün = Weg im Grünen, blau = sonstiger Weg, orange = Gehweg an Straße, rot = Straße, dunkelrot = große
Straße), die anderen Varianten sind dünn gestrichelt. Dunkelgrün gepunktet: vorberechnete Parkrunden.
Kartendaten © OpenStreetMap-Mitwirkende (ODbL).
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CLS = {"green": "#1b9e3e", "path": "#2a7fff", "sidewalk": "#ff9f1c", "street": "#d7263d", "big": "#7b1020"}
ALT = ["#6a3d9a", "#e7298a", "#555555"]
GREEN_TAGS = {"park", "garden", "nature_reserve", "recreation_ground", "forest", "allotments", "village_green", "meadow",
              "grass", "cemetery", "wood", "heath"}
PATHS = {"footway", "path", "track", "cycleway", "pedestrian", "bridleway", "steps"}
SMALL = {"residential", "service", "living_street", "unclassified", "road"}
BIG = {"primary", "primary_link", "secondary", "secondary_link", "trunk", "trunk_link"}


def osm_extract(pbf, bbox, tmp):
    """Straßen, Wege, Grünflächen und Wasser im Rechteck als GeoJSON-Features (osmium)."""
    w, s, e, n = bbox
    cut, flt, out = (os.path.join(tmp, x) for x in ("cut.pbf", "flt.pbf", "out.geojsonseq"))
    subprocess.run(["osmium", "extract", "-b", f"{w},{s},{e},{n}", pbf, "-o", cut, "--overwrite", "-s", "smart"], check=True,
                   capture_output=True)
    subprocess.run(["osmium", "tags-filter", cut, "w/highway", "wr/leisure", "wr/landuse", "wr/natural", "wr/waterway",
                    "-o", flt, "--overwrite"], check=True, capture_output=True)
    subprocess.run(["osmium", "export", flt, "-f", "geojsonseq", "-o", out, "--overwrite"], check=True, capture_output=True)
    feats = []
    with open(out) as fh:
        for line in fh:
            line = line.strip().lstrip("\x1e")
            if line:
                feats.append(json.loads(line))
    return feats


def rings_in(green_dir, bbox):
    """Parkrunden aus den vorberechneten Kacheln im Rechteck."""
    w, s, e, n = bbox
    out = []
    for f in glob.glob(os.path.join(green_dir, "*_*.json")):
        try:
            j = json.load(open(f))
        except ValueError:
            continue
        for r in j.get("r", []):
            x = y = 0
            pts = []
            for i in range(0, len(r[5]) - 1, 2):
                x += r[5][i]
                y += r[5][i + 1]
                pts.append((x / 1e5, y / 1e5))
            if any(w <= p[0] <= e and s <= p[1] <= n for p in pts):
                out.append(pts)
    return out


def draw(ax, feats, rings, routes, start, end, to_xy, title):
    for f in feats:
        p, g = f.get("properties", {}), f.get("geometry") or {}
        polys = [g["coordinates"]] if g.get("type") == "Polygon" else (g["coordinates"] if g.get("type") == "MultiPolygon" else [])
        water = p.get("natural") == "water" or p.get("waterway") in ("riverbank",)
        green = p.get("leisure") in GREEN_TAGS or p.get("landuse") in GREEN_TAGS or p.get("natural") in GREEN_TAGS
        if polys and (water or green):
            for poly in polys:
                xy = [to_xy(c) for c in poly[0]]
                ax.fill([q[0] for q in xy], [q[1] for q in xy], color="#a8d0f0" if water else "#d4ebc8", lw=0, zorder=1)
    for f in feats:
        p, g = f.get("properties", {}), f.get("geometry") or {}
        hw = p.get("highway")
        if not hw or g.get("type") != "LineString":
            continue
        xy = [to_xy(c) for c in g["coordinates"]]
        if hw in PATHS:
            if p.get("footway") in ("sidewalk", "crossing"):
                continue
            ax.plot([q[0] for q in xy], [q[1] for q in xy], color="#7a9a7a", lw=0.5, ls=(0, (2, 2)), zorder=2)
        elif hw in BIG:
            ax.plot([q[0] for q in xy], [q[1] for q in xy], color="#a0a0a0", lw=2.6, zorder=2)
        elif hw == "tertiary" or hw.startswith("tertiary"):
            ax.plot([q[0] for q in xy], [q[1] for q in xy], color="#b0b0b0", lw=1.8, zorder=2)
        elif hw in SMALL:
            ax.plot([q[0] for q in xy], [q[1] for q in xy], color="#c4c4c4", lw=1.0, zorder=2)
    for r in rings:
        xy = [to_xy(c) for c in r + r[:1]]
        ax.plot([q[0] for q in xy], [q[1] for q in xy], color="#2e7d32", lw=0.9, ls=(0, (1, 2)), zorder=3)
    for i, rt in list(enumerate(routes))[::-1]:
        xy = [to_xy(c) for c in rt["coords"]]
        if i:
            ax.plot([q[0] for q in xy], [q[1] for q in xy], color=ALT[(i - 1) % len(ALT)], lw=1.4, ls=(0, (5, 3)), alpha=0.85, zorder=4,
                    label=f"{i + 1}: {rt['name']}")
            continue
        cum = [0.0]
        for a, b in zip(rt["coords"], rt["coords"][1:]):
            cum.append(cum[-1] + math.hypot(to_xy(b)[0] - to_xy(a)[0], to_xy(b)[1] - to_xy(a)[1]))
        tot, rows = cum[-1] or 1, rt.get("rows") or []
        end_m = rows[-1][0] if rows else 1
        k = 0
        for j in range(len(xy) - 1):
            pos = (cum[j] + cum[j + 1]) / 2 / tot * end_m
            while k < len(rows) - 1 and rows[k][0] < pos:
                k += 1
            c = CLS.get(rows[k][1], "#d7263d") if rows else "#d7263d"
            ax.plot([xy[j][0], xy[j + 1][0]], [xy[j][1], xy[j + 1][1]], color=c, lw=3.2, solid_capstyle="round", zorder=5)
        ax.plot([], [], color="#333333", lw=3, label=f"1: {rt['name']} (Farbe = Wegart)")
    for pt, mk in ((start, "o"), (end, "s")):
        if pt:
            q = to_xy(pt)
            ax.plot(q[0], q[1], marker=mk, color="black", ms=8, zorder=6)
    ax.set_title(title, fontsize=10)
    ax.legend(loc="lower left", fontsize=7, framealpha=0.85)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--routes", required=True)
    ap.add_argument("--osm", required=True, help="Ordner mit <stadt>-latest.osm.pbf")
    ap.add_argument("--green", default=os.path.join(HERE, "..", "data", "green"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--versions", default="", help="Versionen nebeneinander (Standard: die ersten zwei)")
    a = ap.parse_args()
    data = json.load(open(a.routes))
    versions = a.versions.split() or list(data["routes"])[:2]
    places = json.load(open(os.path.join(os.path.dirname(a.routes), "places.json")))
    os.makedirs(a.out, exist_ok=True)
    # Je Stadt einmal den Ausschnitt aller Fälle aus dem großen Extrakt schneiden (schneller als je Fall)
    city_pbf, tmp_all = {}, tempfile.mkdtemp()
    for city in sorted({c["city"] for c in data["cases"]}):
        src = next(iter(glob.glob(os.path.join(a.osm, city.lower() + "*.osm.pbf"))), None)
        pts = [p for c in data["cases"] if c["city"] == city for v in versions for rt in data["routes"].get(v, {}).get(c["id"], [])
               for p in rt["coords"]]
        if not src or not pts:
            continue
        out = os.path.join(tmp_all, city.lower() + ".osm.pbf")
        w, s = min(p[0] for p in pts) - 0.02, min(p[1] for p in pts) - 0.02
        e, n = max(p[0] for p in pts) + 0.02, max(p[1] for p in pts) + 0.02
        try:
            subprocess.run(["osmium", "extract", "-b", f"{w},{s},{e},{n}", src, "-o", out, "--overwrite", "-s", "smart"],
                           check=True, capture_output=True)
            city_pbf[city] = out
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"  {city}: Ausschnitt fehlgeschlagen ({e})", flush=True)
    for c in data["cases"]:
        per = {v: data["routes"].get(v, {}).get(c["id"], []) for v in versions}
        pts = [p for rs in per.values() for rt in rs for p in rt["coords"]]
        if not pts:
            continue
        pbf = city_pbf.get(c["city"])
        lons, lats = [p[0] for p in pts], [p[1] for p in pts]
        mlat = (min(lats) + max(lats)) / 2
        dx, dy = 300 / (111320 * math.cos(math.radians(mlat))), 300 / 111320
        bbox = (min(lons) - dx, min(lats) - dy, max(lons) + dx, max(lats) + dy)
        k, kx = 111320, 111320 * math.cos(math.radians(mlat))
        to_xy = lambda q: ((q[0] - bbox[0]) * kx, (q[1] - bbox[1]) * k)  # noqa: E731
        with tempfile.TemporaryDirectory() as tmp:
            try:
                feats = osm_extract(pbf, bbox, tmp) if pbf else []
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"  {c['id']}: Kartendaten fehlen ({e})", flush=True)
                feats = []
        rings = rings_in(a.green, bbox)
        st = places.get(f"{c['start']}, {c['city']}")
        en = places.get(f"{c['end']}, {c['city']}") if c.get("end") else None
        start = (st["lon"], st["lat"]) if st else None
        end = (en["lon"], en["lat"]) if en else None
        w, h = to_xy((bbox[2], bbox[3]))
        fig, axes = plt.subplots(1, len(versions), figsize=(7 * len(versions), 7 * h / max(w, 1) + 0.6), squeeze=False)
        for ax, v in zip(axes[0], versions):
            draw(ax, feats, rings, per[v], start, end, to_xy, f"{c['id']} – {v}")
        fig.text(0.99, 0.005, "Kartendaten © OpenStreetMap-Mitwirkende", ha="right", fontsize=7, color="#666")
        fig.tight_layout()
        path = os.path.join(a.out, c["id"] + ".png")
        fig.savefig(path, dpi=110)
        plt.close(fig)
        try:  # Palette-PNG: deutlich kleiner
            from PIL import Image
            Image.open(path).convert("RGB").quantize(colors=64).save(path, optimize=True)
        except Exception:  # noqa: BLE001
            pass
        print(f"  Karte {c['id']}: {len(feats)} OSM-Objekte, {len(rings)} Parkrunden", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
