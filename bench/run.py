"""Benchmark der Routenqualität: steuert die App im Headless-Browser gegen einen BRouter-Server.

Aufruf:
    python3 bench/run.py --brouter http://localhost:17777 \
        --app neu=http://localhost:8765/ --app alt=http://localhost:8766/ --out bench-out

Jede App-Version rechnet alle Fälle aus bench/cases.json. Bewertet wird einheitlich aus den
Server-Antworten (Wegtypen und Grün-/Wasserklassen von BRouter), unabhängig von der App-Version.
Orte werden per Nominatim geokodiert und in bench/places.json zwischengespeichert.
"""
import argparse
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "laufrouten-benchmark (https://github.com/krvtt/running_routes)"
TRAIL = {"path", "track", "bridleway", "footway", "pedestrian", "steps"}
BIG = re.compile(r"^(primary|secondary|trunk)(_link)?$")


# ---------- Geometrie ----------
def hav(a, b):
    r = math.pi / 180
    s = math.sin((b[1] - a[1]) * r / 2) ** 2 + math.cos(a[1] * r) * math.cos(b[1] * r) * math.sin((b[0] - a[0]) * r / 2) ** 2
    return 2 * 6371008.8 * math.asin(min(1, math.sqrt(s)))


def bearing(a, b):
    dx = (b[0] - a[0]) * math.cos(math.radians(a[1]))
    return math.degrees(math.atan2(dx, b[1] - a[1]))


def turns_per_km(coords, dist):
    pts = [coords[0]]
    for c in coords[1:]:
        if hav(pts[-1], c) >= 12:
            pts.append(c)
    n, pos, last = 0, 0.0, -1e9
    for i in range(1, len(pts) - 1):
        pos += hav(pts[i - 1], pts[i])
        d = abs(bearing(pts[i - 1], pts[i]) - bearing(pts[i], pts[i + 1])) % 360
        if min(d, 360 - d) > 50 and pos - last > 25:
            n += 1
            last = pos
    return n / max(dist / 1000, 0.1)


def spurs(coords, maxlen=400):
    c = [(round(p[0], 6), round(p[1], 6)) for p in coords]
    n, m = 0, 1
    while m < len(c) - 1:
        k = 0
        while m - k - 1 >= 0 and m + k + 1 < len(c) and c[m - k - 1] == c[m + k + 1]:
            k += 1
        if k:
            if sum(hav(c[i], c[i + 1]) for i in range(m - k, m)) < maxlen:
                n += 1
            m += k
        m += 1
    return n


def length_in_box(coords, box):
    s, n, w, e = box
    tot = 0.0
    for a, b in zip(coords, coords[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if w <= mx <= e and s <= my <= n:
            tot += hav(a, b)
    return tot


# ---------- Bewertung aus BRouter-Antwort ----------
def tags(s):
    return dict(t.split("=", 1) for t in (s or "").split() if "=" in t)


def evaluate(feature):
    p = feature["properties"]
    coords = feature["geometry"]["coordinates"]
    dist = float(p["track-length"])
    msgs = p.get("messages") or []
    h = msgs[0] if msgs else []
    col = lambda name, d: h.index(name) if name in h else d  # noqa: E731
    i_dist, i_way, i_node = col("Distance", 3), col("WayTags", 9), col("NodeTags", 10)
    tot = green = street = big = sidewalk = route = 0.0
    signals = crossings = 0
    for row in msgs[1:]:
        d = float(row[i_dist] or 0)
        w, nd = tags(row[i_way]), tags(row[i_node])
        tot += d
        hw, fw = w.get("highway", ""), w.get("footway", "")
        trail = hw in TRAIL and fw not in ("sidewalk", "crossing")
        cls = max(int(w.get("estimated_forest_class", 0) or 0), int(w.get("estimated_river_class", 0) or 0))
        if trail and cls >= 3:
            green += d
        if not trail:
            street += d
        if fw in ("sidewalk", "crossing"):
            sidewalk += d
        if BIG.match(hw):
            big += d
        if any(k.startswith(("route_hiking_", "route_foot_")) and v == "yes" for k, v in w.items()):
            route += d
        if nd.get("highway") == "traffic_signals" or nd.get("crossing") == "traffic_signals":
            signals += 1
        elif int(nd.get("estimated_crossing_class", 0) or 0) >= 1:
            crossings += 1
    tot = tot or 1
    km = max(dist / 1000, 0.1)
    return {
        "dist": round(dist), "cost_per_m": round(float(p["cost"]) / max(dist, 1), 3),
        "green": round(green / tot, 3), "street": round(street / tot, 3), "sidewalk": round(sidewalk / tot, 3),
        "big": round(big / tot, 3), "route": round(route / tot, 3),
        "signals_km": round(signals / km, 2), "crossings_km": round(crossings / km, 2),
        "turns_km": round(turns_per_km(coords, dist), 2), "spurs": spurs(coords), "coords": coords,
    }


# ---------- Orte ----------
AREA_CATS = {"leisure", "landuse", "natural", "waterway", "water", "boundary"}


def geocode(places, name, city, area=False):
    key = f"{name}, {city}"
    if key in places:
        return places[key]
    q = urllib.parse.urlencode({"q": key, "format": "jsonv2", "limit": 5, "countrycodes": "de"})
    req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + q, headers={"User-Agent": UA})
    time.sleep(1.1)
    res = json.load(urllib.request.urlopen(req, timeout=30))
    if area:
        res = [r for r in res if r.get("category") in AREA_CATS] or res
    if not res:
        places[key] = None
        return None
    r = res[0]
    bb = [float(x) for x in r["boundingbox"]]  # süd, nord, west, ost
    places[key] = {"lat": float(r["lat"]), "lon": float(r["lon"]), "box": bb, "label": r.get("display_name", "")[:80],
                   "category": r.get("category", "")}
    return places[key]


# ---------- Nachmessen mit neutralem Profil ----------
def upload_messprofil(brouter):
    text = open(os.path.join(HERE, "messprofil.brf")).read()
    req = urllib.request.Request(brouter + "/brouter/profile", data=text.encode(), headers={"Content-Type": "text/plain"})
    return json.load(urllib.request.urlopen(req, timeout=60))["profileid"]


def remeasure(brouter, pid, coords):
    """Fährt die Route über Stützpunkte im Abstand von ~30 m (plus Knickpunkte) nach und liefert das Feature."""
    pts = [coords[0]]
    for i in range(1, len(coords) - 1):
        a, b, c = pts[-1], coords[i], coords[i + 1]
        d = abs(bearing(a, b) - bearing(b, c)) % 360
        if hav(a, b) >= 30 or (min(d, 360 - d) > 25 and hav(a, b) >= 8):
            pts.append(b)
    pts.append(coords[-1])
    q = "lonlats=" + "%7C".join(f"{p[0]:.6f},{p[1]:.6f}" for p in pts) + f"&profile={pid}&alternativeidx=0&format=geojson"
    with urllib.request.urlopen(brouter + "/brouter?" + q, timeout=120) as r:  # 1.7.10 kennt kein POST-Routing
        return json.loads(r.read().decode())["features"][0]


# ---------- Lauf ----------
def run_app(pw, app_url, brouter, cases, places, mess_pid):
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, locale="de-DE")
    ctx.route(re.compile(r"https://.*(tile\.openstreetmap|basemaps\.cartocdn).*"), lambda r: r.abort())
    page = ctx.new_page()
    captured = []
    page.on("response", lambda r: captured.append(r) if "/brouter?" in r.url else None)
    page.goto(app_url)
    page.wait_for_selector("#presets button")
    page.click("#setBtn")
    page.fill("#serverInput", brouter)
    page.press("#serverInput", "Tab")
    page.click("[data-close=setPanel]")
    out = []
    for c in cases:
        start = geocode(places, c["start"], c["city"])
        end = geocode(places, c["end"], c["city"]) if c.get("end") else None
        res = {"id": c["id"], "preset": c["preset"], "ok": False}
        if not start or (c["mode"] == "ab" and not end):
            res["error"] = "Ort nicht gefunden"
            out.append(res)
            continue
        page.click(f"[data-preset={c['preset']}]")
        page.click("#modeAB" if c["mode"] == "ab" else "#modeRT")
        if c.get("lap"):
            page.fill("#lapInput", str(c["lap"]))
        else:
            page.fill("#kmInput", str(c["km"]))
        page.evaluate("""([s, e]) => { const st = window.__laufrouten.state; st.start = s; st.end = e; }""",
                      [{"lat": start["lat"], "lon": start["lon"], "label": c["start"]},
                       {"lat": end["lat"], "lon": end["lon"], "label": c["end"]} if end else None])
        captured.clear()
        t0 = time.time()
        page.click("#goBtn")
        try:
            page.wait_for_function("!document.getElementById('goBtn').disabled && document.getElementById('status').className",
                                   timeout=300000)
        except Exception as e:  # noqa: BLE001
            res["error"] = f"Zeitüberschreitung: {e}"
            out.append(res)
            continue
        res["seconds"] = round(time.time() - t0, 1)
        res["status"] = page.inner_text("#status")
        res["requests"] = len(captured)
        res["notes"] = page.evaluate("window.__laufrouten.state.notes || []")
        bodies = {}
        for r in captured:
            try:
                f = json.loads(r.text())["features"][0]
                bodies[(round(float(f["properties"]["track-length"])), round(float(f["properties"]["cost"])))] = f
            except Exception:  # noqa: BLE001
                pass
        target = c["lap"] if c.get("lap") else c["km"] * 1000
        variants = page.evaluate("window.__laufrouten.state.variants.map(v => ({name: v.name, dist: v.dist, cost: v.cost, green: !!v.green}))")
        res["variants"] = []
        for v in variants:
            f = bodies.get((round(v["dist"]), round(v["cost"])))
            if not f:
                continue
            orig = evaluate(f)
            try:
                g = remeasure(brouter, mess_pid, f["geometry"]["coordinates"])
                abw = float(g["properties"]["track-length"]) / max(orig["dist"], 1) - 1
            except Exception as e:  # noqa: BLE001
                print(f"    Nachmessen fehlgeschlagen: {e}", flush=True)
                g, abw = None, None
            # Merkmale aus der Nachmessung, wenn sie die Route trifft; sonst aus der Originalantwort
            m = evaluate(g) if g is not None and abs(abw) <= 0.05 else dict(orig)
            m["mess"] = "neutral" if g is not None and abs(abw) <= 0.05 else "original"
            m["mess_abw"] = round(abw, 3) if abw is not None else None
            for k in ("dist", "cost_per_m", "turns_km", "spurs"):  # Geometrie immer von der Originalroute
                m[k] = orig[k]
            m["coords"] = orig["coords"]
            m["name"] = v["name"]
            m["src"] = "grün" if v.get("green") else "geo"
            m["dev"] = round(m["dist"] - target)
            m["areas"] = {}
            for a in c.get("expect", []):
                pl = geocode(places, a, c["city"], area=True)
                if pl:
                    m["areas"][a] = round(length_in_box(m["coords"], pl["box"]))
            del m["coords"]
            res["variants"].append(m)
        res["ok"] = bool(res["variants"])
        out.append(res)
        print(f"  {c['id']}: {res.get('status', '')[:60]} | {len(res['variants'])} Varianten", flush=True)
    browser.close()
    return out


def summarize(results, cases):
    by_id = {c["id"]: c for c in cases}
    agg = {"cases": 0, "ok": 0, "green": 0.0, "street": 0.0, "sidewalk": 0.0, "signals_km": 0.0, "crossings_km": 0.0,
           "turns_km": 0.0, "spurs": 0, "in_band": 0, "area_hits": 0, "area_total": 0, "requests": 0, "seconds": 0.0,
           "best_green": 0.0, "mess_max": 0.0, "green_first": 0, "mess_orig": 0}
    for r in results:
        agg["cases"] += 1
        if not r.get("ok"):
            continue
        c, v = by_id[r["id"]], r["variants"][0]
        agg["ok"] += 1
        for k in ("green", "street", "sidewalk", "signals_km", "crossings_km", "turns_km"):
            agg[k] += v[k]
        agg["best_green"] += max(x["green"] for x in r["variants"])
        agg["spurs"] += sum(x["spurs"] for x in r["variants"])
        agg["green_first"] += int(v.get("src") == "grün")
        agg["mess_orig"] += sum(1 for x in r["variants"] if x.get("mess") == "original")
        target = c["lap"] if c.get("lap") else c["km"] * 1000
        band = target * 0.15 if c["preset"] == "intervall" else (target * 0.02 if c["preset"] == "wettkampf" else max(500, target * 0.1))
        agg["in_band"] += int(any(abs(x["dev"]) <= band for x in r["variants"]))
        for a in c.get("expect", []):
            agg["area_total"] += 1
            agg["area_hits"] += int(any(x["areas"].get(a, 0) >= 300 for x in r["variants"]))
        agg["requests"] += r.get("requests", 0)
        agg["seconds"] += r.get("seconds", 0)
    n = max(agg["ok"], 1)
    for k in ("green", "street", "sidewalk", "signals_km", "crossings_km", "turns_km", "requests", "seconds", "best_green"):
        agg[k] = round(agg[k] / n, 3)
    return agg


def report(all_results, cases, out_dir):
    names = list(all_results)
    sums = {k: summarize(v, cases) for k, v in all_results.items()}
    pct = lambda x: f"{x * 100:.0f} %"  # noqa: E731
    lines = ["# Benchmark Routenqualität", "", f"Stand: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}", "",
             "## Übersicht (erste Variante je Fall, Mittelwerte)", "", "| Kennzahl | " + " | ".join(names) + " |",
             "|---|" + "---|" * len(names)]
    rows = [("Fälle ok", lambda s: f"{s['ok']}/{s['cases']}"), ("Wege im Grünen/am Wasser", lambda s: pct(s["green"])),
            ("… beste der 3 Varianten", lambda s: pct(s["best_green"])), ("Straßen und Gehwege", lambda s: pct(s["street"])),
            ("davon Gehweg an Straße", lambda s: pct(s["sidewalk"])), ("Ampeln pro km", lambda s: s["signals_km"]),
            ("Querungen ohne Ampel pro km", lambda s: s["crossings_km"]), ("Abbiegungen pro km", lambda s: s["turns_km"]),
            ("Stichwege (alle Varianten)", lambda s: s["spurs"]), ("Länge im Bereich", lambda s: f"{s['in_band']}/{s['ok']}"),
            ("Erwartete Grünflächen genutzt", lambda s: f"{s['area_hits']}/{s['area_total']}"),
            ("Empfehlung über Grünflächen-Anker", lambda s: f"{s['green_first']}/{s['ok']}"),
            ("Varianten ohne neutrale Nachmessung", lambda s: s["mess_orig"]),
            ("Anfragen pro Fall", lambda s: s["requests"]), ("Sekunden pro Fall", lambda s: s["seconds"])]
    for label, fn in rows:
        lines.append(f"| {label} | " + " | ".join(str(fn(sums[n])) for n in names) + " |")
    lines += ["", "## Fälle", ""]
    for c in cases:
        lines.append(f"### {c['id']} ({c['preset']}, {'A→B' if c['mode'] == 'ab' else 'Rundkurs'}, "
                     f"{c.get('lap', '') or c.get('km')}{' m' if c.get('lap') else ' km'})")
        for n in names:
            r = next((x for x in all_results[n] if x["id"] == c["id"]), None)
            if r and r.get("notes"):
                lines.append(f"Hinweise {n}: " + " · ".join(r["notes"]))
        lines.append("")
        lines.append("| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for n in names:
            r = next((x for x in all_results[n] if x["id"] == c["id"]), None)
            if not r or not r.get("ok"):
                lines.append(f"| {n} | Fehler: {(r or {}).get('error') or (r or {}).get('status', '?')} | | | | | | | | | | |")
                continue
            for v in r["variants"]:
                areas = ", ".join(f"{k}: {val}" for k, val in v["areas"].items()) or "–"
                lines.append(f"| {n} | {v['name']} | {v['dist']} | {v['dev']:+d} | {pct(v['green'])} | {pct(v['street'])} | "
                             f"{pct(v['sidewalk'])} | {v['signals_km']} | {v['crossings_km']} | {v['turns_km']} | {areas} | {v.get('mess', '')} |")
        lines.append("")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump({"summary": sums, "results": all_results}, f, ensure_ascii=False, indent=1)
    print("\n".join(lines[:22]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brouter", required=True)
    ap.add_argument("--app", action="append", required=True, help="name=url, mehrfach möglich")
    ap.add_argument("--cases", default=os.path.join(HERE, "cases.json"))
    ap.add_argument("--only", help="nur Fälle, deren id diesen Text enthält")
    ap.add_argument("--places", default=os.path.join(HERE, "places.json"), help="Zwischenspeicher der Geokodierung")
    ap.add_argument("--out", default="bench-out")
    a = ap.parse_args()
    cases = json.load(open(a.cases))["cases"]
    if a.only:
        cases = [c for c in cases if a.only in c["id"]]
    places = json.load(open(a.places)) if os.path.exists(a.places) else {}
    all_results = {}
    mess_pid = upload_messprofil(a.brouter)
    with sync_playwright() as pw:
        for spec in a.app:
            name, url = spec.split("=", 1)
            print(f"== {name}: {url}", flush=True)
            all_results[name] = run_app(pw, url, a.brouter, cases, places, mess_pid)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "places.json"), "w") as f:
        json.dump(places, f, ensure_ascii=False, indent=1, sort_keys=True)
    report(all_results, cases, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
