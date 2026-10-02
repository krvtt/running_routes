# Benchmark Routenqualität

Stand: 2026-10-02 14:27 UTC

## Übersicht (erste Variante je Fall, Mittelwerte)

| Kennzahl | neu | 3aa0e38 | 17956d0 |
|---|---|---|---|
| Fälle ok | 13/13 | 13/13 | 13/13 |
| Wege im Grünen/am Wasser | 67 % | 46 % | 55 % |
| … beste der 3 Varianten | 70 % | 52 % | 58 % |
| Straßen und Gehwege | 25 % | 46 % | 34 % |
| davon Gehweg an Straße | 11 % | 30 % | 17 % |
| Ampeln pro km | 1.13 | 1.092 | 1.02 |
| Querungen ohne Ampel pro km | 0.158 | 0.182 | 0.197 |
| Abbiegungen pro km | 4.618 | 3.88 | 4.422 |
| Stichwege (alle Varianten) | 0 | 0 | 0 |
| Länge im Bereich | 13/13 | 13/13 | 13/13 |
| Erwartete Grünflächen genutzt | 10/11 | 11/11 | 11/11 |
| Empfehlung über Grünflächen-Anker | 8/13 | 0/13 | 0/13 |
| Varianten ohne neutrale Nachmessung | 0 | 5 | 5 |
| Anfragen pro Fall | 12.923 | 8.923 | 9.0 |
| Sekunden pro Fall | 1.931 | 1.262 | 1.292 |

## Fälle

### hh-dammtor-rk8 (dauer, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über Alter Botanischer Garten und Grünzug Borgfelder Straße | 8247 | +247 | 80 % | 12 % | 1 % | 1.82 | 0.0 | 2.06 | Planten un Blomen: 90, Außenalster: 3346 | neutral |
| neu | Über Alter Botanischer Garten und Alter Elbpark | 7725 | -275 | 58 % | 35 % | 30 % | 1.17 | 0.26 | 4.27 | Planten un Blomen: 3521, Außenalster: 0 | neutral |
| neu | Über Alter Botanischer Garten und Alter Elbpark | 8115 | +115 | 57 % | 27 % | 16 % | 1.36 | 0.25 | 4.31 | Planten un Blomen: 3978, Außenalster: 0 | neutral |
| 3aa0e38 | Rundkurs nach Osten | 7856 | -144 | 72 % | 17 % | 0 % | 1.4 | 0.13 | 2.67 | Planten un Blomen: 90, Außenalster: 3848 | original |
| 3aa0e38 | Rundkurs nach Norden | 8455 | +455 | 60 % | 12 % | 0 % | 1.66 | 0.12 | 3.19 | Planten un Blomen: 1060, Außenalster: 3677 | original |
| 3aa0e38 | Rundkurs nach Südosten | 7994 | -6 | 53 % | 28 % | 0 % | 1.5 | 0.0 | 3.25 | Planten un Blomen: 186, Außenalster: 1782 | original |
| 17956d0 | Rundkurs nach Osten | 7780 | -220 | 68 % | 22 % | 4 % | 1.54 | 0.13 | 2.44 | Planten un Blomen: 90, Außenalster: 3747 | original |
| 17956d0 | Rundkurs nach Norden | 8714 | +714 | 59 % | 31 % | 19 % | 1.26 | 0.23 | 3.21 | Planten un Blomen: 1124, Außenalster: 3762 | original |
| 17956d0 | Rundkurs nach Südosten | 8261 | +261 | 60 % | 22 % | 3 % | 1.21 | 0.0 | 3.99 | Planten un Blomen: 275, Außenalster: 2035 | original |

### hh-hbf-schanze-ab10 (dauer, A→B, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Nordosten | 9805 | -195 | 74 % | 21 % | 18 % | 0.61 | 0.1 | 2.75 | Planten un Blomen: 1038, Sternschanzenpark: 646 | neutral |
| neu | Über Tennisgelände Rotherbaum und Parkanlage Grindelberg | 10461 | +461 | 47 % | 48 % | 29 % | 2.49 | 0.19 | 3.06 | Planten un Blomen: 0, Sternschanzenpark: 371 | neutral |
| neu | Über Sportpark Rotherbaum und Parkanlage Grindelberg | 10440 | +440 | 39 % | 50 % | 34 % | 2.49 | 0.19 | 4.41 | Planten un Blomen: 0, Sternschanzenpark: 371 | neutral |
| 3aa0e38 | Bogen nach Nordosten | 9795 | -205 | 67 % | 29 % | 23 % | 0.41 | 0.1 | 2.25 | Planten un Blomen: 1063, Sternschanzenpark: 373 | neutral |
| 3aa0e38 | Bogen nach Norden | 10028 | +28 | 42 % | 55 % | 47 % | 1.5 | 0.0 | 2.59 | Planten un Blomen: 0, Sternschanzenpark: 498 | neutral |
| 3aa0e38 | Bogen nach Südwesten | 9462 | -538 | 35 % | 48 % | 0 % | 0.63 | 0.21 | 2.54 | Planten un Blomen: 1619, Sternschanzenpark: 97 | original |
| 17956d0 | Bogen nach Nordosten | 10806 | +806 | 68 % | 28 % | 14 % | 0.56 | 0.28 | 2.96 | Planten un Blomen: 1038, Sternschanzenpark: 646 | neutral |
| 17956d0 | Bogen nach Norden | 10593 | +593 | 46 % | 48 % | 40 % | 1.89 | 0.0 | 3.02 | Planten un Blomen: 0, Sternschanzenpark: 498 | neutral |
| 17956d0 | Bogen nach Süden | 10707 | +707 | 34 % | 50 % | 0 % | 0.84 | 0.19 | 2.15 | Planten un Blomen: 1619, Sternschanzenpark: 87 | original |

### hh-ritterstrasse-rk10 (dauer, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über KGV 129 Pachtgemeinschaft Bille IV und KGV 159 Gartenfreunde am Horner Weg | 10290 | +290 | 69 % | 23 % | 3 % | 0.68 | 0.78 | 5.34 | – | neutral |
| neu | Über KGV 129 Pachtgemeinschaft Bille IV und KGV 594 Gartenfreunde in Marienthal | 10290 | +290 | 69 % | 23 % | 3 % | 0.68 | 0.78 | 5.34 | – | neutral |
| neu | Rundkurs nach Süden | 10461 | +461 | 44 % | 41 % | 15 % | 2.29 | 0.57 | 3.92 | – | neutral |
| 3aa0e38 | Rundkurs nach Süden | 10172 | +172 | 38 % | 52 % | 21 % | 2.36 | 0.59 | 3.34 | – | neutral |
| 3aa0e38 | Rundkurs nach Osten | 10125 | +125 | 46 % | 44 % | 0 % | 1.98 | 0.79 | 5.93 | – | neutral |
| 3aa0e38 | Rundkurs nach Norden | 10998 | +998 | 42 % | 49 % | 4 % | 2.27 | 1.09 | 4.27 | – | neutral |
| 17956d0 | Rundkurs nach Süden | 10461 | +461 | 44 % | 41 % | 15 % | 2.29 | 0.57 | 3.92 | – | neutral |
| 17956d0 | Rundkurs nach Osten | 9260 | -740 | 50 % | 40 % | 0 % | 1.51 | 1.08 | 6.37 | – | neutral |
| 17956d0 | Rundkurs nach Südosten | 10848 | +848 | 31 % | 49 % | 10 % | 2.12 | 0.92 | 5.72 | – | neutral |

### hh-wandsbek-uhland-ab8 (dauer, A→B, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über KGV 159 Gartenfreunde am Horner Weg und Jacobipark | 8166 | +166 | 56 % | 28 % | 3 % | 2.14 | 0.0 | 6.49 | – | neutral |
| neu | Bogen nach Süden | 8045 | +45 | 55 % | 33 % | 9 % | 2.66 | 0.0 | 4.85 | – | neutral |
| neu | Über Blohms Park und KGV 159 Gartenfreunde am Horner Weg | 8515 | +515 | 64 % | 18 % | 1 % | 1.26 | 0.0 | 5.17 | – | neutral |
| 3aa0e38 | Bogen nach Norden | 8566 | +566 | 58 % | 35 % | 3 % | 1.62 | 0.0 | 3.85 | – | neutral |
| 3aa0e38 | Bogen nach Nordwesten | 8270 | +270 | 39 % | 52 % | 7 % | 1.67 | 0.0 | 3.87 | – | neutral |
| 3aa0e38 | Bogen nach Süden | 7727 | -273 | 45 % | 44 % | 12 % | 2.89 | 0.25 | 4.14 | – | neutral |
| 17956d0 | Bogen nach Nordwesten | 8532 | +532 | 57 % | 34 % | 2 % | 1.51 | 0.0 | 4.45 | – | neutral |
| 17956d0 | Bogen nach Norden | 7447 | -553 | 57 % | 32 % | 1 % | 1.46 | 0.27 | 5.91 | – | neutral |
| 17956d0 | Bogen nach Süden | 8045 | +45 | 55 % | 33 % | 9 % | 2.66 | 0.0 | 4.85 | – | neutral |

### hh-christuskirche-hoheluft-ab6 (dauer, A→B, 6 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über Planten un Blomen und Alter Botanischer Garten | 6320 | +320 | 60 % | 27 % | 19 % | 1.74 | 0.16 | 6.17 | Isebekkanal: 1155 | neutral |
| neu | Über Alter Botanischer Garten und Große Moorweide | 5790 | -210 | 58 % | 29 % | 20 % | 1.9 | 0.17 | 5.7 | Isebekkanal: 1155 | neutral |
| neu | Bogen nach Nordwesten | 5777 | -223 | 43 % | 39 % | 28 % | 0.51 | 0.17 | 6.06 | Isebekkanal: 1342 | neutral |
| 3aa0e38 | Bogen nach Nordwesten | 6259 | +259 | 22 % | 68 % | 67 % | 0.96 | 0.0 | 4.31 | Isebekkanal: 2304 | neutral |
| 3aa0e38 | Bogen nach Nordwesten | 6202 | +202 | 21 % | 72 % | 70 % | 0.65 | 0.0 | 3.71 | Isebekkanal: 1335 | neutral |
| 3aa0e38 | Bogen nach Südosten | 5364 | -636 | 35 % | 50 % | 48 % | 2.62 | 0.19 | 3.73 | Isebekkanal: 1159 | neutral |
| 17956d0 | Bogen nach Nordwesten | 5777 | -223 | 43 % | 39 % | 28 % | 0.51 | 0.17 | 6.06 | Isebekkanal: 1342 | neutral |
| 17956d0 | Bogen nach Nordwesten | 6176 | +176 | 22 % | 61 % | 49 % | 0.49 | 0.0 | 4.21 | Isebekkanal: 1335 | neutral |
| 17956d0 | Bogen nach Südosten | 5913 | -87 | 53 % | 34 % | 24 % | 2.37 | 0.17 | 4.57 | Isebekkanal: 1120 | neutral |

### hh-kellinghusen-rk8 (dauer, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über KGV 434 Gartenverein Groot Osterfeld und Eppendorfer Park | 8431 | +431 | 71 % | 22 % | 4 % | 1.54 | 0.36 | 4.74 | Hayns Park: 484 | neutral |
| neu | Über KGV 434 Gartenverein Groot Osterfeld und KGV 424 Gartenverein Tarpenbekufer | 7984 | -16 | 70 % | 13 % | 4 % | 2.0 | 0.25 | 4.38 | Hayns Park: 484 | neutral |
| neu | Rundkurs nach Osten | 7650 | -350 | 54 % | 41 % | 32 % | 1.7 | 0.0 | 4.84 | Hayns Park: 0 | neutral |
| 3aa0e38 | Rundkurs nach Osten | 8508 | +508 | 46 % | 39 % | 31 % | 1.65 | 0.24 | 4.23 | Hayns Park: 526 | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 8701 | +701 | 22 % | 72 % | 54 % | 1.61 | 0.34 | 2.99 | Hayns Park: 0 | neutral |
| 3aa0e38 | Rundkurs nach Süden | 8651 | +651 | 8 % | 91 % | 86 % | 1.97 | 0.0 | 2.89 | Hayns Park: 0 | neutral |
| 17956d0 | Rundkurs nach Osten | 8583 | +583 | 49 % | 36 % | 26 % | 1.4 | 0.35 | 4.89 | Hayns Park: 526 | neutral |
| 17956d0 | Rundkurs nach Norden | 7309 | -691 | 50 % | 38 % | 13 % | 1.09 | 0.41 | 6.02 | Hayns Park: 484 | neutral |
| 17956d0 | Rundkurs nach Nordwesten | 8324 | +324 | 47 % | 35 % | 12 % | 1.68 | 0.24 | 4.32 | Hayns Park: 526 | neutral |

### hh-planetarium-lang14 (lang, Rundkurs, 14 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Norden | 14220 | +220 | 47 % | 36 % | 10 % | 1.05 | 0.0 | 4.78 | Stadtpark: 2225, Außenalster: 0 | neutral |
| neu | Rundkurs nach Osten | 13691 | -309 | 50 % | 36 % | 11 % | 1.17 | 0.22 | 5.33 | Stadtpark: 2134, Außenalster: 0 | neutral |
| neu | Rundkurs nach Westen | 13855 | -145 | 32 % | 50 % | 14 % | 1.59 | 0.14 | 3.68 | Stadtpark: 1127, Außenalster: 0 | neutral |
| 3aa0e38 | Rundkurs nach Westen | 14305 | +305 | 41 % | 47 % | 25 % | 1.47 | 0.28 | 3.01 | Stadtpark: 1352, Außenalster: 372 | neutral |
| 3aa0e38 | Rundkurs nach Osten | 14685 | +685 | 55 % | 37 % | 2 % | 1.02 | 0.41 | 3.47 | Stadtpark: 2974, Außenalster: 0 | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 13906 | -94 | 54 % | 39 % | 0 % | 0.86 | 0.65 | 3.67 | Stadtpark: 2354, Außenalster: 2623 | original |
| 17956d0 | Rundkurs nach Osten | 13977 | -23 | 62 % | 26 % | 6 % | 1.36 | 0.0 | 5.8 | Stadtpark: 2953, Außenalster: 0 | neutral |
| 17956d0 | Rundkurs nach Norden | 14220 | +220 | 47 % | 36 % | 10 % | 1.05 | 0.0 | 4.78 | Stadtpark: 2225, Außenalster: 0 | neutral |
| 17956d0 | Rundkurs nach Südosten | 13937 | -63 | 45 % | 47 % | 12 % | 0.86 | 0.5 | 4.38 | Stadtpark: 2351, Außenalster: 2586 | original |

### hh-altona-recovery5 (recovery, Rundkurs, 5 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über Rosengarten und Heine-Park | 4676 | -324 | 70 % | 15 % | 0 % | 1.72 | 0.0 | 5.13 | – | neutral |
| neu | Über Altonaer Balkon und Walter-Möller-Park | 4741 | -259 | 48 % | 20 % | 1 % | 1.05 | 0.21 | 4.22 | – | neutral |
| neu | Über Rosengarten und Donners-Park | 5422 | +422 | 42 % | 31 % | 0 % | 3.32 | 0.0 | 4.8 | – | neutral |
| 3aa0e38 | Rundkurs nach Süden | 4613 | -387 | 35 % | 48 % | 0 % | 1.08 | 0.43 | 5.85 | – | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 5553 | +553 | 36 % | 45 % | 4 % | 1.26 | 0.36 | 5.22 | – | neutral |
| 3aa0e38 | Rundkurs nach Westen | 5583 | +583 | 28 % | 55 % | 6 % | 3.76 | 0.18 | 4.84 | – | neutral |
| 17956d0 | Rundkurs nach Südosten | 5373 | +373 | 40 % | 31 % | 1 % | 0.93 | 0.19 | 5.4 | – | neutral |
| 17956d0 | Rundkurs nach Süden | 4593 | -407 | 36 % | 46 % | 1 % | 1.31 | 0.22 | 6.97 | – | neutral |
| 17956d0 | Rundkurs nach Osten | 5378 | +378 | 36 % | 40 % | 6 % | 2.05 | 0.56 | 3.9 | – | neutral |

### hh-planten-intervall (intervall, Rundkurs, 1000 m)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Runde nach Südosten | 890 | -110 | 84 % | 16 % | 0 % | 0.0 | 0.0 | 6.74 | Planten un Blomen: 891 | neutral |
| neu | Runde nach Norden | 979 | -21 | 82 % | 18 % | 0 % | 0.0 | 0.0 | 14.3 | Planten un Blomen: 833 | neutral |
| neu | Runde nach Osten | 789 | -211 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 11.41 | Planten un Blomen: 789 | neutral |
| 3aa0e38 | Runde nach Westen | 1064 | +64 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 7.52 | Planten un Blomen: 1066 | neutral |
| 3aa0e38 | Runde nach Südosten | 959 | -41 | 85 % | 15 % | 0 % | 0.0 | 0.0 | 5.21 | Planten un Blomen: 958 | neutral |
| 3aa0e38 | Runde nach Nordwesten | 1142 | +142 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 9.63 | Planten un Blomen: 1146 | neutral |
| 17956d0 | Runde nach Südosten | 890 | -110 | 84 % | 16 % | 0 % | 0.0 | 0.0 | 6.74 | Planten un Blomen: 891 | neutral |
| 17956d0 | Runde nach Norden | 979 | -21 | 82 % | 18 % | 0 % | 0.0 | 0.0 | 14.3 | Planten un Blomen: 833 | neutral |
| 17956d0 | Runde nach Osten | 789 | -211 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 11.41 | Planten un Blomen: 789 | neutral |

### hh-kellinghusen-tempo8 (tempo, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über KGV 434 Gartenverein Groot Osterfeld und KGV 424 Gartenverein Tarpenbekufer | 7546 | -454 | 82 % | 13 % | 8 % | 0.66 | 0.27 | 4.9 | – | neutral |
| neu | Über KGV 434 Gartenverein Groot Osterfeld und Eppendorfer Park | 8022 | +22 | 76 % | 19 % | 8 % | 0.75 | 0.5 | 5.48 | – | neutral |
| neu | Über Parkanlage Grindelberg und KGV 424 Gartenverein Tarpenbekufer | 8302 | +302 | 44 % | 52 % | 35 % | 0.48 | 0.48 | 4.82 | – | neutral |
| 3aa0e38 | Rundkurs nach Süden | 7474 | -526 | 7 % | 86 % | 66 % | 0.13 | 0.13 | 4.15 | – | neutral |
| 3aa0e38 | Rundkurs nach Osten | 8421 | +421 | 29 % | 57 % | 39 % | 1.43 | 0.36 | 4.39 | – | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 8550 | +550 | 21 % | 72 % | 53 % | 1.4 | 0.35 | 3.04 | – | neutral |
| 17956d0 | Rundkurs nach Westen | 8393 | +393 | 22 % | 52 % | 33 % | 1.19 | 0.12 | 5.0 | – | neutral |
| 17956d0 | Rundkurs nach Nordwesten | 8190 | +190 | 32 % | 46 % | 15 % | 1.34 | 0.37 | 4.52 | – | neutral |
| 17956d0 | Rundkurs nach Osten | 7437 | -563 | 34 % | 62 % | 30 % | 1.75 | 0.13 | 4.44 | – | neutral |

### b-brandenburger-rk10 (dauer, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Westen | 10465 | +465 | 57 % | 40 % | 32 % | 1.15 | 0.38 | 4.78 | Großer Tiergarten: 3370 | neutral |
| neu | Über Park am Nordbahnhof und Spreebogenpark | 10070 | +70 | 56 % | 37 % | 34 % | 1.19 | 0.4 | 5.56 | Großer Tiergarten: 2392 | neutral |
| neu | Rundkurs nach Norden | 10135 | +135 | 49 % | 44 % | 42 % | 1.58 | 0.1 | 5.92 | Großer Tiergarten: 429 | neutral |
| 3aa0e38 | Rundkurs nach Norden | 10299 | +299 | 30 % | 65 % | 60 % | 1.36 | 0.19 | 3.98 | Großer Tiergarten: 230 | neutral |
| 3aa0e38 | Rundkurs nach Nordwesten | 9966 | -34 | 34 % | 64 % | 58 % | 1.1 | 0.5 | 3.91 | Großer Tiergarten: 3187 | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 9061 | -939 | 29 % | 61 % | 56 % | 1.88 | 0.0 | 2.87 | Großer Tiergarten: 743 | neutral |
| 17956d0 | Rundkurs nach Südosten | 10391 | +391 | 55 % | 38 % | 29 % | 1.06 | 0.1 | 4.52 | Großer Tiergarten: 1148 | neutral |
| 17956d0 | Rundkurs nach Nordwesten | 10586 | +586 | 50 % | 42 % | 37 % | 0.85 | 0.28 | 4.91 | Großer Tiergarten: 3158 | neutral |
| 17956d0 | Rundkurs nach Norden | 10135 | +135 | 49 % | 44 % | 42 % | 1.58 | 0.1 | 5.92 | Großer Tiergarten: 429 | neutral |

### b-hbf-tempelhof-ab12 (dauer, A→B, 12 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Osten | 11679 | -321 | 67 % | 31 % | 25 % | 1.28 | 0.0 | 3.94 | Großer Tiergarten: 0 | neutral |
| neu | Über Böcklerpark und Anita-Berber-Park | 11426 | -574 | 67 % | 25 % | 16 % | 1.05 | 0.35 | 3.94 | Großer Tiergarten: 2151 | neutral |
| neu | Über Heinrich-von-Kleist-Park und Hans-Baluschek-Park | 12590 | +590 | 50 % | 39 % | 32 % | 0.48 | 0.32 | 3.65 | Großer Tiergarten: 1422 | neutral |
| 3aa0e38 | Bogen nach Südwesten | 12502 | +502 | 59 % | 39 % | 37 % | 1.36 | 0.08 | 2.88 | Großer Tiergarten: 1308 | neutral |
| 3aa0e38 | Bogen nach Osten | 11702 | -298 | 40 % | 58 % | 52 % | 1.71 | 0.0 | 3.33 | Großer Tiergarten: 0 | neutral |
| 3aa0e38 | Bogen nach Nordosten | 12179 | +179 | 43 % | 51 % | 48 % | 1.15 | 0.16 | 3.53 | Großer Tiergarten: 0 | neutral |
| 17956d0 | Bogen nach Südwesten | 11430 | -570 | 73 % | 23 % | 20 % | 0.52 | 0.26 | 3.24 | Großer Tiergarten: 1179 | neutral |
| 17956d0 | Bogen nach Osten | 11679 | -321 | 67 % | 31 % | 25 % | 1.28 | 0.0 | 3.94 | Großer Tiergarten: 0 | neutral |
| 17956d0 | Bogen nach Nordosten | 11794 | -206 | 64 % | 28 % | 23 % | 1.53 | 0.0 | 4.58 | Großer Tiergarten: 0 | neutral |

### b-tempelhof-wettkampf10 (wettkampf, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) | Messung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neu | Über Marienglück und Sorgenfrei | 9919 | -81 | 59 % | 41 % | 17 % | 0.3 | 0.0 | 2.22 | – | neutral |
| neu | Über Sorgenfrei und Anita-Berber-Park | 10094 | +94 | 55 % | 44 % | 25 % | 0.2 | 0.2 | 1.88 | – | neutral |
| neu | Rundkurs nach Süden | 10193 | +193 | 45 % | 54 % | 38 % | 0.39 | 0.39 | 2.06 | – | neutral |
| 3aa0e38 | Rundkurs nach Südosten | 9999 | -1 | 30 % | 68 % | 58 % | 0.4 | 0.2 | 2.4 | – | neutral |
| 3aa0e38 | Rundkurs nach Norden | 10366 | +366 | 28 % | 68 % | 65 % | 0.77 | 0.48 | 2.99 | – | neutral |
| 3aa0e38 | Rundkurs nach Süden | 9546 | -454 | 34 % | 66 % | 56 % | 0.52 | 0.31 | 1.89 | – | neutral |
| 17956d0 | Rundkurs nach Süden | 10193 | +193 | 45 % | 54 % | 38 % | 0.39 | 0.39 | 2.06 | – | neutral |
| 17956d0 | Rundkurs nach Westen | 10004 | +4 | 36 % | 55 % | 43 % | 0.4 | 0.0 | 4.5 | – | neutral |
| 17956d0 | Rundkurs nach Südosten | 9583 | -417 | 47 % | 44 % | 38 % | 0.52 | 0.0 | 2.82 | – | neutral |

