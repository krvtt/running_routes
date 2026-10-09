# Laufrouten Hamburg

Web-App, die Laufstrecken mit Wunschlänge plant: von A nach B mit passendem Umweg oder als Rundkurs. Die Strecken bevorzugen Parks, Uferwege und ruhige Nebenstraßen und nehmen Ampeln oder große Straßen nur in Kauf, wenn sich der Weg dadurch lohnt.

**App:** https://krvtt.github.io/running_routes/

Läuft im Browser auf Android, iOS, Windows und macOS und lässt sich als App auf dem Home-Bildschirm installieren. Kein Konto, kein API-Schlüssel, keine Werbung, kein Tracking.

## Funktionen

- **A → B oder Rundkurs** mit Länge in Kilometern oder als Dauer bei gegebenem Tempo
- **Sieben Trainingsarten** mit eigener Routenlogik: lockerer Dauerlauf, langer Lauf, Recovery, Tempodauerlauf, Intervalle, Wettkampf-Simulation, Fahrtspiel
- **Parkrunden:** ganze Runden, Halbrunden und Bögen um Parks und Seen, automatisch zwischen den anderen Varianten
- **Mehrere Varianten**, sortiert nach Eignung, mit Begründung der Empfehlung
- **Kennzahlen je Route:** Anteil Grün und Wasser, längstes Stück im Grünen, Ampeln, ungesicherte Querungen, Abbiegungen, Belag, Wegtypen
- **Intervall-Runden** um nahe Parks oder ohne Querung am Start, optionale Markierung für Steigerungen
- **GPX-Export** für OsmAnd, Organic Maps oder Sportuhren
- **Favoriten, Verlauf und Backup** (Export/Import als JSON)
- **Bewertungen** je Route (gut/nicht gut, Stichworte), exportierbar ohne Start und Ziel
- Heller und dunkler Modus, für die Bedienung unterwegs ausgelegt

## So funktioniert es

Das Routing übernimmt [BRouter](https://github.com/abrensch/brouter) auf Basis von OpenStreetMap. Die App lädt beim ersten Aufruf ein eigenes Laufprofil ([`profiles/laufen.brf`](profiles/laufen.brf)) auf den Server. Das Profil bewertet jeden Weg mit einem Kostenfaktor (Parkweg = 1,0; Hauptstraße deutlich höher) und jede Ampel oder Querung mit einem Umweg-Äquivalent in Metern. Der Router nimmt eine Ampel also nur, wenn sie genug Park, Ufer oder ruhige Strecke erschließt. Die Trainingsarten verschieben diese Gewichte pro Anfrage über `profile:<name>=<wert>`.

Varianten entstehen in drei Schritten:

1. **Grünflächen:** Aus OpenStreetMap entstehen zwei Arten von Zielen. *Parkrunden:* der Umriss jeder Grünfläche ab 0,5 ha und jedes Sees ab 1 ha, alle 25 m auf den nächsten passenden Fußweg eingerastet (im Park auf Wege im Inneren, am See auf Uferwege). *Anker:* Punkte in Grünflächen ab 1 ha, an Gewässern ab 2 ha und entlang von Flüssen und Kanälen. Für die Regionen in `data/regions.json` (derzeit Hamburg und Berlin) ist beides vorberechnet und liegt als Kacheln unter `data/green/`; ein Workflow erneuert sie monatlich aus den OpenStreetMap-Extrakten der Geofabrik. Anderswo fragt die App die Grünflächen bei der Overpass-API ab (Parkrunden dann grob aus dem Umriss) und speichert sie 30 Tage im Gerät.
2. **Kandidaten:** Runden, Halbrunden und Bögen um einen Park oder See, zwei Parks nacheinander, ein Park plus Anker oder ein bis drei Anker – jeweils mit geschätzter Länge passend zur Wunschlänge. Die Länge regelt die Bogenlänge am Park, nicht ein Umweg durch Seitenstraßen. Zusätzlich geometrische Rundkurse (Stützpunkte im Fächer um den Start) bzw. Bögen links und rechts der Luftlinie als Rückfall. Ist der direkte Weg schon lang genug, liefert BRouter Alternativrouten.
3. **Auswahl:** Die besten Kandidaten außerhalb des Längenbereichs werden einmal nachgeregelt. Angezeigt werden drei möglichst verschiedene Varianten: zuerst die im Längenbereich, dann bis zur doppelten Toleranz, jeweils nach Bewertung. Die Bewertung sind die Routing-Kosten pro Meter (Grün, Wasser, Ruhe, wenig Stopps) plus Abzüge für Wenden auf Straßen und doppelt gelaufene Straßen.

Der Längenbereich ist die Toleranz der Trainingsart (±5 %, Recovery ±15 %, mindestens ±250 m); Varianten bis zur doppelten Toleranz erscheinen nachrangig. Wettkampf-Simulation und Intervalle bleiben eng (±2 % bzw. ±15 %). Kurze Stichwege, die nur entstehen, weil ein Stützpunkt in einer Seitenstraße liegt, entfernt BRouter selbst (`correctMisplacedViaPoints`, bis 400 m einfache Strecke). Längere Hin-und-zurück-Abschnitte bleiben erhalten.

Das Profil unterscheidet Wege im Grünen, sonstige Wege, Gehwege an Straßen (`footway=sidewalk`) und Straßen. Grün und Wasser (BRouter-Schätzklassen für Wald, Parks, Kleingärten, Ufer) senken vor allem die Kosten von Wegen, kaum die von Straßen am Parkrand.

## Datenschutz

| Daten | Wohin |
|---|---|
| Favoriten, Verlauf, Einstellungen | nur im Browser des Geräts (IndexedDB) |
| Bewertungen | nur im Gerät; „Bewertungen exportieren“ erzeugt eine Datei ohne Start und Ziel (siehe unten) |
| Start-, Ziel- und Zwischenpunkte | Routing-Server (Standard: brouter.de) |
| Suchbegriffe der Adresssuche | Nominatim (OpenStreetMap) |
| Kartenausschnitt für Grünflächen | Overpass-API (OpenStreetMap), nur außerhalb der vorberechneten Regionen, einmal je Gebiet und Monat |
| Kartenausschnitt | Kachelserver von OpenStreetMap |

Die Daten hängen an der Adresse der App. Für einen Gerätewechsel: Einstellungen → Exportieren bzw. Importieren.

**Bewertungen:** Gespeichert wird nur die Strecke, nie Start oder Ziel. Um jeden Start- und Zielort liegt eine Privatzone: ein Kreis mit 500 m Radius, dessen Mitte einmal zufällig bis 250 m vom Ort verschoben wird und nur im Gerät bleibt. Alles innerhalb wird abgeschnitten. So verraten die Schnittkanten auch nach vielen Bewertungen vom selben Ort nur die Zonenmitte. Dazu kommen nur das Datum (ohne Uhrzeit), Kennzahlen, Stichworte und die Art der Variante ohne Park- oder Straßennamen.

## Eigener Routing-Server

Der öffentliche Server brouter.de wird ehrenamtlich betrieben. Für intensive Nutzung empfiehlt sich ein eigener BRouter-Server (z. B. per Docker, siehe [BRouter-Dokumentation](https://github.com/abrensch/brouter)). Seine Adresse lässt sich in der App unter Einstellungen → Routing-Server eintragen. Der Server muss CORS erlauben (BRouter tut das standardmäßig) und Profil-Uploads unterstützen.

## Entwicklung

Reine statische Seite ohne Build-Schritt: HTML, CSS und JavaScript, dazu Leaflet als lokale Kopie.

```
python3 -m http.server 8765        # App unter http://localhost:8765
python3 tests/e2e.py               # Browser-Test, BRouter und Overpass simuliert
python3 tests/e2e.py --brouter http://localhost:17777 --center <lon,lat> --scale 0.2 --green <kacheln>
```

Der Test braucht [Playwright für Python](https://playwright.dev/python/) mit Chromium. Mit `--brouter` laufen alle Routing-Anfragen gegen einen echten Server, mit `--green` kommen die Grünflächen aus selbst erzeugten Kacheln (`python3 tools/green_anchors.py --pbf <datei.osm.pbf> --out <kacheln>`).

**Benchmark:** Der Workflow `.github/workflows/benchmark.yml` startet bei Änderungen an App, Profil oder Benchmark einen eigenen BRouter mit echten Kartendaten (Hamburg, Berlin) und rechnet die Fälle aus `bench/cases.json` mit der aktuellen und älteren Versionen. Jede Route wird mit einem neutralen Messprofil nachgefahren und bewertet: Anteil Wege im Grünen, längstes Stück im Grünen, Straßen und Gehwege, Ampeln, Querungen, Abbiegungen, Wenden, doppelt gelaufene Straßen, Stichwege, Länge, genutzte Grünflächen. Dazu je Fall eine Karte (`bench/maps.py`, braucht osmium-tool). Die Berichte liegen auf dem Branch [`bench-results`](../../tree/bench-results) (`latest/report.md`).

| Datei | Inhalt |
|---|---|
| `index.html`, `style.css` | Oberfläche |
| `app.js` | Routing-Logik, Grünflächen-Anker, Längenregelung, Kennzahlen, Speicher |
| `profiles/laufen.brf` | BRouter-Profil |
| `sw.js`, `manifest.webmanifest` | Installation und Offline-Start |
| `vendor/leaflet/` | Leaflet 1.9.4 |
| `tests/e2e.py` | End-to-End-Test |
| `bench/` | Benchmark: Fälle, Runner, Messprofil, Karten, BRouter-Setup |
| `tools/green_anchors.py`, `data/` | Parkrunden und Grünflächen-Anker aus OpenStreetMap-Extrakten (ohne externe Abhängigkeiten), Regionenliste, Kacheln |

## Lizenz und Quellen

Code: [MIT](LICENSE). Karten- und Wegdaten © [OpenStreetMap-Mitwirkende](https://www.openstreetmap.org/copyright) (ODbL). Routing: [BRouter](https://github.com/abrensch/brouter) (MIT). Karte: [Leaflet](https://leafletjs.com) (BSD-2-Clause, siehe `vendor/leaflet/LICENSE`). Adresssuche: [Nominatim](https://nominatim.org). Grünflächen: OpenStreetMap-Extrakte der [Geofabrik](https://download.geofabrik.de) bzw. [Overpass-API](https://overpass-api.de).
