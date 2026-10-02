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

Die Wunschlänge regelt die App selbst nach:

- **Rundkurs:** Stützpunkte im Fächer um den Start in drei Richtungen; der Radius wird nachgeregelt, bis die Länge innerhalb der Toleranz der Trainingsart liegt.
- **A → B:** Ist der direkte Weg zu kurz, entstehen Bögen links und rechts der Luftlinie über einen Zwischenpunkt, dessen Abstand ebenso nachgeregelt wird.

Die Varianten werden nach den Routing-Kosten pro Meter und der Längenabweichung sortiert.

## Datenschutz

| Daten | Wohin |
|---|---|
| Favoriten, Verlauf, Einstellungen | nur im Browser des Geräts (IndexedDB) |
| Start-, Ziel- und Zwischenpunkte | Routing-Server (Standard: brouter.de) |
| Suchbegriffe der Adresssuche | Nominatim (OpenStreetMap) |
| Kartenausschnitt | Kachelserver von OpenStreetMap |

Die Daten hängen an der Adresse der App. Für einen Gerätewechsel: Einstellungen → Exportieren bzw. Importieren.

## Eigener Routing-Server

Der öffentliche Server brouter.de wird ehrenamtlich betrieben. Für intensive Nutzung empfiehlt sich ein eigener BRouter-Server (z. B. per Docker, siehe [BRouter-Dokumentation](https://github.com/abrensch/brouter)). Seine Adresse lässt sich in der App unter Einstellungen → Routing-Server eintragen. Der Server muss CORS erlauben (BRouter tut das standardmäßig) und Profil-Uploads unterstützen.

## Entwicklung

Reine statische Seite ohne Build-Schritt: HTML, CSS und JavaScript, dazu Leaflet als lokale Kopie.

```
python3 -m http.server 8765        # App unter http://localhost:8765
python3 tests/e2e.py               # Browser-Test, BRouter simuliert
python3 tests/e2e.py --brouter http://localhost:17777 --center <lon,lat> --scale 0.2
```

Der Test braucht [Playwright für Python](https://playwright.dev/python/) mit Chromium. Mit `--brouter` laufen alle Routing-Anfragen gegen einen echten Server.

| Datei | Inhalt |
|---|---|
| `index.html`, `style.css` | Oberfläche |
| `app.js` | Routing-Logik, Längenregelung, Kennzahlen, Speicher |
| `profiles/laufen.brf` | BRouter-Profil |
| `sw.js`, `manifest.webmanifest` | Installation und Offline-Start |
| `vendor/leaflet/` | Leaflet 1.9.4 |
| `tests/e2e.py` | End-to-End-Test |

## Lizenz und Quellen

Code: [MIT](LICENSE). Karten- und Wegdaten © [OpenStreetMap-Mitwirkende](https://www.openstreetmap.org/copyright) (ODbL). Routing: [BRouter](https://github.com/abrensch/brouter) (MIT). Karte: [Leaflet](https://leafletjs.com) (BSD-2-Clause, siehe `vendor/leaflet/LICENSE`). Adresssuche: [Nominatim](https://nominatim.org).
