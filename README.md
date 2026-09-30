# Laufrouten Hamburg (Version 2.0)

Installierbare Web-App (PWA): Laufrouten mit Wunschlänge, A→B oder Rundkurs, sieben Trainingsarten, GPX-Export. Läuft auf Android, iPhone, Windows und Mac. Ohne Konto, ohne Schlüssel, ohne Abo.

## Einmalig online stellen (GitHub Pages, ca. 10 Minuten)

1. Auf github.com ein kostenloses Konto anlegen. Empfohlen: Zwei-Faktor-Anmeldung einschalten (Settings → Password and authentication).
2. Oben rechts „+“ → „New repository“. Name: `laufrouten`, Sichtbarkeit „Public“, „Create repository“.
3. Auf der leeren Seite den Link „uploading an existing file“ anklicken. ZIP entpacken, **alle Dateien** markieren und ins Browserfenster ziehen, unten „Commit changes“.
4. Im Repository „Settings“ → links „Pages“ → Source „Deploy from a branch“, Branch `main`, Ordner `/ (root)` → „Save“.
5. Nach 1–3 Minuten ist die App unter `https://DEINNAME.github.io/laufrouten/` erreichbar.

Das Repository ist öffentlich. Es enthält nur Programmcode, keine Adressen und keine persönlichen Daten.

## Als App installieren

- Android (Chrome): Seite öffnen → „Installieren“ oben in der App oder Menü → „App installieren“.
- iPhone (Safari): Teilen → „Zum Home-Bildschirm“.
- Windows/Mac (Chrome oder Edge): Installationssymbol rechts in der Adressleiste.
- Mac (Safari): Ablage → „Zum Dock hinzufügen“.

## Update einspielen

Repository → „Add file“ → „Upload files“ → neue Dateien hineinziehen (gleiche Namen werden ersetzt) → „Commit changes“. Die App holt die neue Version beim nächsten Öffnen.

## Was die App sich merkt

Favoriten, Verlauf (letzte 30 Routen), letzte Start- und Zielpunkte und Einstellungen – nur auf dem jeweiligen Gerät, gebunden an die Adresse der App. Umzug auf ein anderes Gerät: Einstellungen → „Exportieren“, dort „Importieren“.

## Datenfluss

- Routing: Start-, Ziel- und Zwischenpunkte gehen an den BRouter-Server (Standard: brouter.de, ehrenamtlich betrieben). Später austauschbar gegen einen eigenen Server (Einstellungen → Routing-Server).
- Adresssuche: Suchbegriffe gehen an Nominatim (OpenStreetMap). Höchstens eine Anfrage pro Sekunde.
- Karten: Kacheln von OpenStreetMap.
- Keine Konten, keine Tracker, keine Werbung.

## Quellen und Lizenzen

Kartendaten © OpenStreetMap-Mitwirkende (ODbL). Routing: BRouter (MIT). Karte: Leaflet 1.9.4 (BSD-2, siehe LICENSE-leaflet.txt).
