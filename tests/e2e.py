"""End-to-End-Test der App im Headless-Chromium (Handy-Viewport).

Aufruf (im Repo-Ordner):
    python3 -m http.server 8765 &
    python3 tests/e2e.py                                   # BRouter simuliert
    python3 tests/e2e.py --brouter http://localhost:17777 \\
        --center 8.7120,50.0020 --scale 0.25               # echter BRouter-Server

Adresssuche (Nominatim) und Kartenkacheln werden immer simuliert, Grünflächen
(data/green/ und Overpass) ebenfalls, außer mit --green <ordner>: dann kommen die
vorberechneten Kacheln aus diesem Ordner (Ausgabe von tools/green_anchors.py).
Mit --brouter gehen Profil-Upload und alle Routing-Anfragen an den angegebenen
Server; --center muss dann in dessen Kartendaten liegen, --scale verkleinert die
Testlängen passend zur Größe des Datenausschnitts.

Benötigt: pip install playwright (Chromium muss installiert sein).
Rückgabewert 0 = alle Prüfungen bestanden.
"""
import argparse
import base64
import json
import math
import os
import re
import sys
import tempfile
from urllib.parse import parse_qs, unquote, urlparse

from playwright.sync_api import sync_playwright

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
CORS = {"Access-Control-Allow-Origin": "*"}


def hav(a, b):
    r = math.pi / 180
    s = math.sin((b[1] - a[1]) * r / 2) ** 2 + math.cos(a[1] * r) * math.cos(b[1] * r) * math.sin((b[0] - a[0]) * r / 2) ** 2
    return 2 * 6371008.8 * math.asin(min(1, math.sqrt(s)))


def offset(p, dx, dy):
    """Punkt p (lon, lat) um dx/dy Meter verschieben."""
    return (p[0] + dx / (111320 * math.cos(math.radians(p[1]))), p[1] + dy / 111320)


# ---------- Simulierter BRouter ----------
WAYS = [
    ("highway=path surface=compacted estimated_forest_class=5", 1280),
    ("highway=residential surface=asphalt estimated_town_class=5", 2200),
    ("highway=footway surface=asphalt estimated_river_class=6 route_hiking_lwn=yes", 1410),
    ("highway=secondary surface=asphalt estimated_noise_class=5", 3800),
]
NODES = ["", "highway=traffic_signals", "", "estimated_crossing_class=4", "crossing=zebra"]
HEADER = ["Longitude", "Latitude", "Elevation", "Distance", "CostPerKm", "ElevCost", "TurnCost",
          "NodeCost", "InitialCost", "WayTags", "NodeTags", "Time", "Energy"]


def mock_route(wps, seed):
    """Zickzack-Linie durch alle Wegpunkte (Umwegfaktor ~1,25) im BRouter-GeoJSON-Format."""
    coords, flip = [], 1
    for p, q in zip(wps, wps[1:]):
        n = max(1, int(hav(p, q) // 50))
        for i in range(n):
            a = (p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n)
            coords.append([a[0], a[1], 10.0])
            m = (p[0] + (q[0] - p[0]) * (i + .5) / n, p[1] + (q[1] - p[1]) * (i + .5) / n)
            dx, dy = q[0] - p[0], q[1] - p[1]
            norm = math.hypot(dx, dy) or 1
            o = offset(m, -dy / norm * 19 * flip, dx / norm * 19 * flip)
            coords.append([o[0], o[1], 11.0])
            flip = -flip
    coords.append([wps[-1][0], wps[-1][1], 10.0])
    msgs, cost, last, acc, seg = [HEADER], 0, 0, 0, 0
    for i in range(1, len(coords)):
        acc += hav(coords[i - 1], coords[i])
        if acc - last >= 300 or i == len(coords) - 1:
            d = acc - last
            last = acc
            tags, cf = WAYS[(seg + seed) % len(WAYS)]
            node = NODES[(seg + seed) % len(NODES)] if i < len(coords) - 1 else ""
            cost += d * cf / 1000 + (100 if node else 0)
            msgs.append([str(round(coords[i][0] * 1e6)), str(round(coords[i][1] * 1e6)), "10", str(int(d)), str(cf),
                         "0", "0", "0", "0", tags, node, "0", "0"])
            seg += 1
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {
        "track-length": str(int(acc)), "filtered ascend": "3", "cost": str(int(cost)), "messages": msgs},
        "geometry": {"type": "LineString", "coordinates": coords}}]}


class MockBRouter:
    def __init__(self):
        self.calls = 0
        self.fail = False

    def __call__(self, route):
        url = route.request.url
        if "/brouter/profile" in url:
            assert "---context:way" in (route.request.post_data or ""), "Profiltext fehlt im Upload"
            return route.fulfill(status=200, content_type="application/json", headers=CORS, body='{"profileid": "custom_1"}')
        self.calls += 1
        q = parse_qs(urlparse(url).query)
        assert "engineMode" not in q, "App darf den Server-Rundkurs-Modus nicht benutzen"
        assert any(k.startswith("profile:") for k in q), "Preset-Parameter fehlen"
        if self.fail:
            return route.fulfill(status=500, content_type="text/plain", headers=CORS,
                                 body="operation killed by thread-priority-watchdog after 60 seconds")
        pts = [tuple(map(float, p.split(",")[:2])) for p in unquote(q["lonlats"][0]).split("|")]
        body = mock_route(pts, len(pts) + int(q.get("alternativeidx", ["0"])[0]))
        route.fulfill(status=200, content_type="application/json", headers=CORS, body=json.dumps(body))


# ---------- Test ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default="http://localhost:8765/")
    ap.add_argument("--brouter", help="echter BRouter-Server statt Simulation")
    ap.add_argument("--center", default="9.9930,53.5600", help="lon,lat für Start/Ziel")
    ap.add_argument("--scale", type=float, default=1.0, help="Faktor für Testlängen")
    ap.add_argument("--shots", help="Ordner für Screenshots")
    ap.add_argument("--green", help="Ordner mit vorberechneten Grünflächen-Kacheln statt Simulation")
    a = ap.parse_args()
    center = tuple(map(float, a.center.split(",")))
    places = {"start": offset(center, 700 * a.scale, -150 * a.scale), "ziel": offset(center, -700 * a.scale, 150 * a.scale)}
    km = lambda x: str(round(x * a.scale, 1))  # noqa: E731
    checks, errors = [], []

    def check(name, ok, info=""):
        checks.append((name, bool(ok), info))

    def geocoder(route):
        q = parse_qs(urlparse(route.request.url).query)["q"][0].lower()
        p = places.get(q, center)
        body = [{"lat": str(p[1]), "lon": str(p[0]), "display_name": q.title() + ", Teststadt"}]
        route.fulfill(status=200, content_type="application/json", headers=CORS, body=json.dumps(body))

    def overpass(route):
        """Simulierte Grünflächen um den Testmittelpunkt: Park, See, Kanal."""
        def ring(cx, cy, w, h):
            pts = [offset(center, cx - w, cy - h), offset(center, cx + w, cy - h), offset(center, cx + w, cy + h),
                   offset(center, cx - w, cy + h), offset(center, cx - w, cy - h)]
            return [{"lat": p[1], "lon": p[0]} for p in pts]
        k = a.scale
        els = [
            {"type": "way", "id": 1, "tags": {"leisure": "park", "name": "Testpark"}, "geometry": ring(-900 * k, 800 * k, 500 * k, 300 * k)},
            {"type": "way", "id": 2, "tags": {"natural": "water", "name": "Testsee"}, "geometry": ring(1200 * k, -600 * k, 400 * k, 400 * k)},
            {"type": "way", "id": 3, "tags": {"waterway": "canal", "name": "Testkanal"},
             "geometry": [{"lat": p[1], "lon": p[0]} for p in (offset(center, -1500 * k, -1200 * k), offset(center, 0, -1500 * k), offset(center, 1500 * k, -1800 * k))]},
        ]
        route.fulfill(status=200, content_type="application/json", headers=CORS, body=json.dumps({"elements": els}))

    def tile_of(p):
        return "%d_%d" % (math.floor(p[1] / 0.05), math.floor(p[0] / 0.08))

    def green_tiles(route):
        """Vorberechnete Kacheln: aus --green oder simuliert (Kachel am Testmittelpunkt mit Wiese, Teich, Anker)."""
        name = urlparse(route.request.url).path.rsplit("/", 1)[-1]
        if a.green:
            path = os.path.join(a.green, name)
            if not os.path.exists(path):
                return route.fulfill(status=404, body="")
            return route.fulfill(status=200, content_type="application/json", body=open(path, "rb").read())
        key = tile_of(center)
        if name == "index.json":
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({"v": 2, "tiles": [key]}))
        if name != key + ".json":
            return route.fulfill(status=404, body="")
        k = a.scale

        def ring(cx, cy, w, h, n=24):
            pts = []
            for i in range(n):
                t = i / n * 4
                x, y = [(-w + 2 * w * t, -h), (w, -h + 2 * h * (t - 1)), (w - 2 * w * (t - 2), h), (-w, h - 2 * h * (t - 3))][min(3, int(t))]
                pts.append(offset(center, cx + x, cy + y))
            flat, px, py = [], 0, 0
            for lon, lat in pts:
                x, y = round(lon * 1e5), round(lat * 1e5)
                flat += [x - px, y - py]
                px, py = x, y
            return flat, "1" * n
        wiese, wm = ring(500 * k, 300 * k, 120 * k, 120 * k)
        teich, tm = ring(-600 * k, -900 * k, 350 * k, 250 * k)
        anchor = offset(center, -1300 * k, 600 * k)
        body = {"v": 2, "a": [[round(anchor[0], 5), round(anchor[1], 5), 1.2, 2]], "f": [["w11", "Testwiese"], ["w12", "Testteich"], ["w13", "Testgraben"]],
                "r": [[0, round(960 * k), 0.9, 0, 1.4, wiese, wm], [1, round(2400 * k), 0.8, 1, 17.5, teich, tm]]}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    mock = MockBRouter()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="de-DE", service_workers="block",
                                  timezone_id="Europe/Berlin", accept_downloads=True)
        ctx.route("https://nominatim.openstreetmap.org/**", geocoder)
        ctx.route(re.compile(r"https://.*(tile\.openstreetmap|basemaps\.cartocdn).*"),
                  lambda r: r.fulfill(status=200, content_type="image/png", body=PNG))
        ctx.route(re.compile(r"https://overpass[^/]*/api/interpreter"), overpass)
        ctx.route(re.compile(r".*/data/green/[^/]+\.json$"), green_tiles)
        if not a.brouter:
            ctx.route("https://brouter.de/**", mock)
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "status of 5" not in m.text else None)
        page.goto(a.app)
        page.wait_for_selector("#presets button")
        status = lambda: page.inner_text("#status")  # noqa: E731

        if a.brouter:
            page.click("#setBtn")
            page.fill("#serverInput", a.brouter)
            page.press("#serverInput", "Tab")
            page.click("[data-close=setPanel]")

        def pick(which, query, fav):
            page.fill(f"#{which}Input", query)
            page.click(f"form[data-search={which}] button")
            page.click(f"#{which}Results button >> nth=0")
            page.click(f"[data-fav={which}]")
            page.fill(f"#{which}FavName", fav)
            page.click(f"form[data-favform={which}] button")

        pick("start", "Start", "Arbeit")
        pick("end", "Ziel", "Zuhause")

        def run(label):
            """Berechnen und prüfen, ob mindestens eine Variante im Längenbereich der App liegt."""
            page.click("#goBtn")
            page.wait_for_function("!document.getElementById('goBtn').disabled && document.getElementById('status').className",
                                   timeout=120000)
            res = page.evaluate("""() => { const T = window.__laufrouten, L = T.state.lastL, pr = T.PRESETS[T.settings.preset];
                // Stichwege: Wendepunkt, an dem die Route auf denselben Knoten zurückläuft (einfache Länge < 400 m)
                const spurs = (c) => { let n = 0; const k = (p) => p[0].toFixed(6) + ',' + p[1].toFixed(6);
                  for (let m = 1; m < c.length - 1; m++) { let j = 0, len = 0;
                    while (m - j - 1 >= 0 && m + j + 1 < c.length && k(c[m - j - 1]) === k(c[m + j + 1])) j++;
                    if (j) { for (let i = m - j; i < m; i++) { const dx = (c[i + 1][0] - c[i][0]) * 71500, dy = (c[i + 1][1] - c[i][1]) * 111320; len += Math.hypot(dx, dy); }
                      if (len < 400) n++; m += j; } }
                  return n; };
                return { band: T.band(L, pr), vs: T.state.variants.map(v => ({ name: v.name, dev: Math.round(v.dist - L), spurs: spurs(v.coords) })) }; }""")
            ok = bool(res["vs"]) and page.evaluate("document.getElementById('status').className") != "err"
            best = min((abs(v["dev"]) for v in res["vs"]), default=10**9)
            spurs = sum(v["spurs"] for v in res["vs"])
            check(label, ok and best <= res["band"] and (not a.brouter or spurs == 0),
                  f"{status()} | beste Abweichung {best} m (Bereich ±{round(res['band'])} m) | Stichwege {spurs}")
            return res["vs"]

        # A→B, Länge über direktem Weg: Bögen mit Nachregelung
        page.fill("#kmInput", km(6))
        run("A→B Dauerlauf mit Umweg")
        with page.expect_download() as dl:
            page.click("#gpxBtn")
        gpx = open(dl.value.path()).read()
        check("GPX-Export", gpx.startswith("<?xml") and gpx.count("<trkpt") > 10, dl.value.suggested_filename)
        if a.shots:
            page.screenshot(path=f"{a.shots}/ab.png", full_page=True)

        # Rundkurse (Stützpunkte clientseitig)
        page.click("#modeRT")
        page.click("[data-preset=wettkampf]")
        page.fill("#kmInput", km(10))
        run("Rundkurs Wettkampf-Simulation")
        page.click("[data-preset=lang]")
        page.fill("#kmInput", km(25))
        run("Rundkurs Langer Lauf")
        page.click("[data-preset=intervall]")
        page.fill("#lapInput", str(int(max(600, 1000 * a.scale))))
        run("Intervall-Runde")
        laps = page.evaluate("window.__laufrouten.state.lapCount || 0")
        check("Intervall-Runden um Parks gerechnet", laps > 0 or (a.brouter and not a.green), f"{laps} Parkrunden")
        page.click("[data-preset=dauer]")
        page.check("#stridesChk")
        page.fill("#kmInput", km(8))
        run("Rundkurs Dauerlauf mit Steigerungen")
        green_names = page.evaluate("window.__laufrouten.state.variants.filter(v => v.green).map(v => v.name)")
        green_count = page.evaluate("window.__laufrouten.state.greenCount || 0")
        rings = page.evaluate("window.__laufrouten.state.rings || 0")
        arcs = page.evaluate("window.__laufrouten.state.arcCount || 0")
        if a.brouter:  # echte Daten ohne Grün-Klassen: nur prüfen, dass Grün-Kandidaten gerechnet wurden
            check("Grünflächen-Kandidaten gerechnet", green_count > 0, f"{green_count} Kandidaten")
        else:
            # Simulierter Server kennt kein Grün: prüfen, dass Grün-Kandidaten im Längenbereich gerechnet wurden
            cands = page.evaluate("window.__laufrouten.state.cands || []")
            band = page.evaluate("(() => { const T = window.__laufrouten; return T.band(T.state.lastL, T.PRESETS[T.settings.preset]); })()")
            ok = [c for c in cands if c["green"] and abs(c["dist"] - 8000 * a.scale) <= band]
            check("Grünflächen-Kandidaten im Längenbereich", ok, "; ".join(f"{c['name']} {c['dist']} m" for c in ok) or "keine")
        check("Parkrunden geladen und gerechnet", rings > 0 and arcs > 0, f"{rings} Parkrunden, {arcs} Kandidaten mit Bogen")
        names_before = page.evaluate("window.__laufrouten.state.variants.map(v => v.name).join()")
        page.click("#againBtn")
        page.wait_for_function("!document.getElementById('goBtn').disabled", timeout=120000)
        check("Andere Varianten", page.evaluate("window.__laufrouten.state.variants.map(v => v.name).join()") != names_before)
        if a.shots:
            page.screenshot(path=f"{a.shots}/rundkurs.png", full_page=True)

        if not a.brouter:
            mock.fail = True
            page.click("#goBtn")
            page.wait_for_function("document.getElementById('status').className === 'err'", timeout=30000)
            check("Fehlermeldung bei überlastetem Server", "ausgelastet" in status(), status())
            mock.fail = False

        # Gedächtnis nach Neuladen
        page.reload()
        page.wait_for_selector("#presets button")
        check("Favoriten nach Neuladen", page.locator("[data-favs=start] button").all_inner_texts() == ["Arbeit", "Zuhause"])
        check("Startpunkt nach Neuladen", page.inner_text("#startPt") == "Arbeit", page.inner_text("#startPt"))
        check("Einstellungen nach Neuladen", page.evaluate("window.__laufrouten.settings.mode") == "rt" and page.is_checked("#stridesChk"))
        page.click("#histBtn")
        page.wait_for_selector("[data-hload]")
        n_hist = page.locator("[data-hload]").count()
        page.click("[data-hload] >> nth=0")
        page.wait_for_selector("#resCard:not([hidden])")
        check("Verlauf", n_hist >= 5, f"{n_hist} Einträge")

        # Backup
        page.click("#setBtn")
        with page.expect_download() as dl2:
            page.click("#exportBtn")
        backup = json.load(open(dl2.value.path()))
        page.set_input_files("#importFile", dl2.value.path())
        page.wait_for_function("document.getElementById('status').textContent.startsWith('Importiert')")
        check("Export/Import", len(backup["favorites"]) == 2 and len(backup["history"]) >= 5, status())
        page.click("[data-close=setPanel]")

        # Dunkelmodus
        page.emulate_media(color_scheme="dark")
        page.click("#modeAB")
        page.fill("#kmInput", km(6))
        run("A→B im Dunkelmodus")
        if a.shots:
            page.screenshot(path=f"{a.shots}/dunkel.png")
        browser.close()

    check("Keine JavaScript-Fehler", not errors, "; ".join(errors[:3]))
    width = max(len(c[0]) for c in checks)
    for name, ok, info in checks:
        print(f"{'OK  ' if ok else 'FAIL'} {name.ljust(width)}  {info}")
    failed = [c for c in checks if not c[1]]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} bestanden")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
