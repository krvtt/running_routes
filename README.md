# Laufrouten Hamburg

Web-App, die Laufstrecken mit Wunschlänge plant: von A nach B mit passendem Umweg oder als Rundkurs. Die Strecken bevorzugen Parks, Uferwege und ruhige Nebenstraßen und nehmen Ampeln oder große Straßen nur in Kauf, wenn sich der Weg dadurch lohnt.

**App:** https://krvtt.github.io/running_routes/

Läuft im Browser auf Android, iOS, Windows und macOS und lässt sich als App auf dem Home-Bildschirm installieren. Kein Konto, kein API-Schlüssel, keine Werbung, kein Tracking.

## Funktionen

- **A → B oder Rundkurs** mit Länge in Kilometern oder als Dauer bei gegebenem Tempo
- **Sieben Trainingsarten** mit eigener Routenlogik: lockerer Dauerlauf, langer Lauf, Recovery, Tempodauerlauf, Intervalle, Wettkampf-Simulation, Fahrtspiel
- **Mehrere Varianten**, sortiert nach Eignung, mit Begründung der Empfehlung
- **Kennzahlen je Route:** Anteil Grün und Wasser, Ampeln, ungesicherte Querungen, Abbiegungen, Belag, Wegtypen
- **Intervall-Runden** ohne Querung und optionale Markierung für Steigerungen
- **GPX-Export** für OsmAnd, Organic Maps oder Sportuhren
- **Favoriten, Verlauf und Backup** (Export/Import als JSON)
- Heller und dunkler Modus, für die Bedienung unterwegs ausgelegt

## So funktioniert es

Das Routing übernimmt [BRouter](https://github.com/abrensch/brouter) auf Basis von OpenStreetMap. Die App lädt beim ersten Aufruf ein eigenes Laufprofil ([`profiles/laufen.brf`](profiles/laufen.brf)) auf den Server. Das Profil bewertet jeden Weg mit einem Kostenfaktor (Parkweg = 1,0; Hauptstraße deutlich höher) und jede Ampel oder Querung mit einem Umweg-Äquivalent in Metern. Der Router nimmt eine Ampel also nur, wenn sie genug Park, Ufer oder ruhige Strecke erschließt. Die Trainingsarten verschieben diese Gewichte pro Anfrage über `profile:<name>=<wert>`.

Varianten entstehen in drei Schritten:

1. **Grünflächen:** Die App fragt Parks, Wälder, Kleingärten, Wiesen, Gewässer und Kanäle im Umkreis bei OpenStreetMap ab (Overpass, je Kachel von etwa 5 × 5 km, 30 Tage im Gerät gespeichert). Daraus entstehen Anker: Punkte in Grünflächen, an Ufern und entlang von Kanälen. Kandidaten führen über ein bis drei Anker, deren geschätzte Länge zur Wunschlänge passt.
2. **Geometrische Kandidaten:** Zusätzlich Rundkurse in mehreren Richtungen (Stützpunkte im Fächer um den Start) bzw. Bögen links und rechts der Luftlinie. Sie sichern die Länge ab und dienen als Rückfall, wenn keine Grünflächen-Daten verfügbar sind. Ist der direkte Weg schon lang genug, liefert BRouter Alternativrouten.
3. **Auswahl:** Die günstigsten Kandidaten außerhalb des Längenbereichs werden nachgeregelt. Angezeigt werden drei möglichst verschiedene Varianten; zuerst die im Längenbereich, darunter die mit den geringsten Routing-Kosten pro Meter. Grün-Kandidaten setzen sich also nur durch, wenn sie laut Profil wirklich grüner und ruhiger sind.

Der Längenbereich ist die Toleranz der Trainingsart, mindestens ±500 m. Wettkampf-Simulation und Intervalle bleiben eng (±2 % bzw. ±15 %). Kurze Stichwege, die nur entstehen, weil ein Stützpunkt in einer Seitenstraße liegt, entfernt BRouter selbst (`correctMisplacedViaPoints`, bis 400 m einfache Strecke). Längere Hin-und-zurück-Abschnitte bleiben erhalten.

Das Profil unterscheidet Wege im Grünen, sonstige Wege, Gehwege an Straßen (`footway=sidewalk`) und Straßen. Grün und Wasser (BRouter-Schätzklassen für Wald, Parks, Kleingärten, Ufer) senken vor allem die Kosten von Wegen, kaum die von Straßen am Parkrand.

## Datenschutz

| Daten | Wohin |
|---|---|
| Favoriten, Verlauf, Einstellungen | nur im Browser des Geräts (IndexedDB) |
| Start-, Ziel- und Zwischenpunkte | Routing-Server (Standard: brouter.de) |
| Suchbegriffe der Adresssuche | Nominatim (OpenStreetMap) |
| Kartenausschnitt für Grünflächen | Overpass-API (OpenStreetMap), einmal je Gebiet und Monat |
| Kartenausschnitt | Kachelserver von OpenStreetMap |

Die Daten hängen an der Adresse der App. Für einen Gerätewechsel: Einstellungen → Exportieren bzw. Importieren.

## Eigener Routing-Server

Der öffentliche Server brouter.de wird ehrenamtlich betrieben. Für intensive Nutzung empfiehlt sich ein eigener BRouter-Server (z. B. per Docker, siehe [BRouter-Dokumentation](https://github.com/abrensch/brouter)). Seine Adresse lässt sich in der App unter Einstellungen → Routing-Server eintragen. Der Server muss CORS erlauben (BRouter tut das standardmäßig) und Profil-Uploads unterstützen.

## Entwicklung

Reine statische Seite ohne Build-Schritt: HTML, CSS und JavaScript, dazu Leaflet als lokale Kopie.

```
python3 -m http.server 8765        # App unter http://localhost:8765
python3 tests/e2e.py               # Browser-Test, BRouter und Overpass simuliert
python3 tests/e2e.py --brouter http://localhost:17777 --center <lon,lat> --scale 0.2
```

Der Test braucht [Playwright für Python](https://playwright.dev/python/) mit Chromium. Mit `--brouter` laufen alle Routing-Anfragen gegen einen echten Server.

**Benchmark:** Der Workflow `.github/workflows/benchmark.yml` startet bei Änderungen an App, Profil oder Benchmark einen eigenen BRouter mit echten Kartendaten (Hamburg, Berlin) und rechnet die Fälle aus `bench/cases.json` mit der aktuellen und älteren Versionen. Jede Route wird mit einem neutralen Messprofil nachgefahren und bewertet: Anteil Wege im Grünen, Straßen und Gehwege, Ampeln, Querungen, Abbiegungen, Stichwege, Länge, genutzte Grünflächen. Die Berichte liegen auf dem Branch [`bench-results`](../../tree/bench-results) (`latest/report.md`).

| Datei | Inhalt |
|---|---|
| `index.html`, `style.css` | Oberfläche |
| `app.js` | Routing-Logik, Grünflächen-Anker, Längenregelung, Kennzahlen, Speicher |
| `profiles/laufen.brf` | BRouter-Profil |
| `sw.js`, `manifest.webmanifest` | Installation und Offline-Start |
| `vendor/leaflet/` | Leaflet 1.9.4 |
| `tests/e2e.py` | End-to-End-Test |
| `bench/` | Benchmark: Fälle, Runner, Messprofil, BRouter-Setup |

## Lizenz und Quellen

Code: [MIT](LICENSE). Karten- und Wegdaten © [OpenStreetMap-Mitwirkende](https://www.openstreetmap.org/copyright) (ODbL). Routing: [BRouter](https://github.com/abrensch/brouter) (MIT). Karte: [Leaflet](https://leafletjs.com) (BSD-2-Clause, siehe `vendor/leaflet/LICENSE`). Adresssuche: [Nominatim](https://nominatim.org). Grünflächen: [Overpass-API](https://overpass-api.de).
