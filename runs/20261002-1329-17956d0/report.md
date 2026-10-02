# Benchmark Routenqualität

Stand: 2026-10-02 13:29 UTC

## Übersicht (erste Variante je Fall, Mittelwerte)

| Kennzahl | neu | alt (3aa0e38) |
|---|---|---|
| Fälle ok | 13/13 | 13/13 |
| Wege im Grünen/am Wasser | 54 % | 46 % |
| … beste der 3 Varianten | 58 % | 51 % |
| Straßen und Gehwege | 34 % | 47 % |
| davon Gehweg an Straße | 17 % | 31 % |
| Ampeln pro km | 1.026 | 1.1 |
| Querungen ohne Ampel pro km | 0.21 | 0.195 |
| Abbiegungen pro km | 4.478 | 3.914 |
| Stichwege (alle Varianten) | 32 | 22 |
| Länge im Bereich | 13/13 | 13/13 |
| Erwartete Grünflächen genutzt | 11/13 | 11/13 |
| Nachmessung: max. Längenabweichung | 80.9 % | 27.0 % |
| Anfragen pro Fall | 9.0 | 8.923 |
| Sekunden pro Fall | 1.438 | 1.292 |

## Fälle

### hh-dammtor-rk8 (dauer, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Osten | 7780 | -220 | 63 % | 27 % | 12 % | 1.62 | 0.3 | 2.63 | Planten un Blomen: 90, Außenalster: 5731 |
| neu | Rundkurs nach Norden | 8714 | +714 | 56 % | 34 % | 23 % | 1.29 | 0.37 | 3.23 | Planten un Blomen: 1124, Außenalster: 5747 |
| neu | Rundkurs nach Südosten | 8261 | +261 | 60 % | 22 % | 3 % | 1.96 | 0.12 | 4.96 | Planten un Blomen: 275, Außenalster: 2035 |
| alt (3aa0e38) | Rundkurs nach Osten | 7856 | -144 | 59 % | 32 % | 17 % | 1.5 | 0.3 | 2.81 | Planten un Blomen: 90, Außenalster: 5833 |
| alt (3aa0e38) | Rundkurs nach Norden | 8455 | +455 | 51 % | 40 % | 29 % | 1.61 | 0.28 | 3.12 | Planten un Blomen: 1060, Außenalster: 5662 |
| alt (3aa0e38) | Rundkurs nach Südosten | 7994 | -6 | 52 % | 32 % | 5 % | 2.14 | 0.12 | 4.28 | Planten un Blomen: 186, Außenalster: 1782 |

### hh-hbf-schanze-ab10 (dauer, A→B, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Nordosten | 10806 | +806 | 68 % | 28 % | 14 % | 0.56 | 0.28 | 2.97 | Planten un Blomen: 1038, Sternschanzenpark: 647 |
| neu | Bogen nach Norden | 10593 | +593 | 46 % | 48 % | 40 % | 1.89 | 0.0 | 3.03 | Planten un Blomen: 0, Sternschanzenpark: 498 |
| neu | Bogen nach Süden | 10707 | +707 | 40 % | 50 % | 1 % | 0.98 | 0.05 | 4.03 | Planten un Blomen: 1619, Sternschanzenpark: 87 |
| alt (3aa0e38) | Bogen nach Nordosten | 9795 | -205 | 67 % | 29 % | 23 % | 0.41 | 0.1 | 2.25 | Planten un Blomen: 1063, Sternschanzenpark: 373 |
| alt (3aa0e38) | Bogen nach Norden | 10028 | +28 | 42 % | 55 % | 47 % | 1.5 | 0.0 | 2.6 | Planten un Blomen: 0, Sternschanzenpark: 498 |
| alt (3aa0e38) | Bogen nach Südwesten | 9462 | -538 | 40 % | 46 % | 3 % | 0.55 | 0.09 | 3.77 | Planten un Blomen: 1619, Sternschanzenpark: 97 |

### hh-ritterstrasse-rk10 (dauer, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Süden | 10461 | +461 | 44 % | 41 % | 15 % | 2.29 | 0.57 | 3.92 | Eilbektal: 0 |
| neu | Rundkurs nach Osten | 9260 | -740 | 50 % | 40 % | 0 % | 1.51 | 1.08 | 6.37 | Eilbektal: 256 |
| neu | Rundkurs nach Südosten | 10848 | +848 | 31 % | 49 % | 10 % | 2.12 | 0.92 | 5.72 | Eilbektal: 0 |
| alt (3aa0e38) | Rundkurs nach Süden | 10172 | +172 | 38 % | 52 % | 21 % | 2.36 | 0.59 | 3.34 | Eilbektal: 0 |
| alt (3aa0e38) | Rundkurs nach Osten | 10125 | +125 | 46 % | 44 % | 0 % | 1.98 | 0.79 | 5.93 | Eilbektal: 171 |
| alt (3aa0e38) | Rundkurs nach Norden | 10998 | +998 | 42 % | 49 % | 4 % | 2.27 | 1.09 | 4.27 | Eilbektal: 171 |

### hh-wandsbek-uhland-ab8 (dauer, A→B, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Nordwesten | 8532 | +532 | 57 % | 34 % | 2 % | 1.51 | 0.0 | 4.63 | Eilbektal: 214 |
| neu | Bogen nach Norden | 7447 | -553 | 57 % | 32 % | 1 % | 1.46 | 0.27 | 6.1 | Eilbektal: 0 |
| neu | Bogen nach Süden | 8045 | +45 | 55 % | 33 % | 9 % | 2.66 | 0.0 | 5.07 | Eilbektal: 0 |
| alt (3aa0e38) | Bogen nach Norden | 8566 | +566 | 58 % | 35 % | 3 % | 1.62 | 0.0 | 4.04 | Eilbektal: 180 |
| alt (3aa0e38) | Bogen nach Nordwesten | 8270 | +270 | 39 % | 52 % | 7 % | 1.67 | 0.0 | 4.06 | Eilbektal: 180 |
| alt (3aa0e38) | Bogen nach Süden | 7727 | -273 | 45 % | 44 % | 12 % | 2.89 | 0.25 | 4.4 | Eilbektal: 0 |

### hh-christuskirche-hoheluft-ab6 (dauer, A→B, 6 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Nordwesten | 5777 | -223 | 43 % | 39 % | 28 % | 0.51 | 0.17 | 6.41 | Isebekkanal: 1342 |
| neu | Bogen nach Nordwesten | 6176 | +176 | 22 % | 61 % | 49 % | 0.49 | 0.0 | 4.21 | Isebekkanal: 1335 |
| neu | Bogen nach Südosten | 5913 | -87 | 53 % | 34 % | 24 % | 2.37 | 0.17 | 4.57 | Isebekkanal: 1120 |
| alt (3aa0e38) | Bogen nach Nordwesten | 6259 | +259 | 22 % | 68 % | 67 % | 0.96 | 0.0 | 4.32 | Isebekkanal: 2304 |
| alt (3aa0e38) | Bogen nach Nordwesten | 6202 | +202 | 21 % | 72 % | 70 % | 0.65 | 0.0 | 3.72 | Isebekkanal: 1335 |
| alt (3aa0e38) | Bogen nach Südosten | 5364 | -636 | 35 % | 50 % | 48 % | 2.62 | 0.19 | 3.74 | Isebekkanal: 1159 |

### hh-kellinghusen-rk8 (dauer, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Osten | 8583 | +583 | 49 % | 36 % | 26 % | 1.4 | 0.35 | 4.89 | Hayns Park: 526 |
| neu | Rundkurs nach Norden | 7309 | -691 | 50 % | 38 % | 13 % | 1.09 | 0.41 | 6.02 | Hayns Park: 484 |
| neu | Rundkurs nach Nordwesten | 8324 | +324 | 47 % | 35 % | 12 % | 1.68 | 0.24 | 4.32 | Hayns Park: 526 |
| alt (3aa0e38) | Rundkurs nach Osten | 8508 | +508 | 46 % | 39 % | 31 % | 1.65 | 0.24 | 4.23 | Hayns Park: 526 |
| alt (3aa0e38) | Rundkurs nach Südosten | 8701 | +701 | 22 % | 72 % | 54 % | 1.61 | 0.34 | 2.99 | Hayns Park: 0 |
| alt (3aa0e38) | Rundkurs nach Süden | 8651 | +651 | 8 % | 91 % | 86 % | 1.97 | 0.0 | 2.89 | Hayns Park: 0 |

### hh-planetarium-lang14 (lang, Rundkurs, 14 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Osten | 13977 | -23 | 62 % | 26 % | 6 % | 1.36 | 0.0 | 5.72 | Stadtpark: 2953, Außenalster: 0 |
| neu | Rundkurs nach Norden | 14220 | +220 | 47 % | 36 % | 10 % | 1.05 | 0.0 | 4.78 | Stadtpark: 2225, Außenalster: 0 |
| neu | Rundkurs nach Südosten | 13937 | -63 | 45 % | 47 % | 16 % | 1.0 | 0.5 | 4.17 | Stadtpark: 2351, Außenalster: 4572 |
| alt (3aa0e38) | Rundkurs nach Westen | 14305 | +305 | 41 % | 47 % | 25 % | 1.47 | 0.28 | 3.01 | Stadtpark: 1352, Außenalster: 372 |
| alt (3aa0e38) | Rundkurs nach Osten | 14685 | +685 | 55 % | 37 % | 2 % | 1.02 | 0.41 | 3.41 | Stadtpark: 2974, Außenalster: 0 |
| alt (3aa0e38) | Rundkurs nach Südosten | 13906 | -94 | 36 % | 57 % | 22 % | 1.0 | 0.62 | 3.49 | Stadtpark: 2354, Außenalster: 4607 |

### hh-altona-recovery5 (recovery, Rundkurs, 5 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Südosten | 5373 | +373 | 40 % | 31 % | 1 % | 0.93 | 0.19 | 5.4 | – |
| neu | Rundkurs nach Süden | 4593 | -407 | 36 % | 46 % | 1 % | 1.31 | 0.22 | 6.97 | – |
| neu | Rundkurs nach Osten | 5378 | +378 | 36 % | 40 % | 6 % | 2.05 | 0.56 | 3.9 | – |
| alt (3aa0e38) | Rundkurs nach Süden | 4613 | -387 | 35 % | 48 % | 0 % | 1.08 | 0.43 | 5.85 | – |
| alt (3aa0e38) | Rundkurs nach Südosten | 5553 | +553 | 36 % | 45 % | 4 % | 1.26 | 0.36 | 5.22 | – |
| alt (3aa0e38) | Rundkurs nach Westen | 5583 | +583 | 28 % | 55 % | 6 % | 3.76 | 0.18 | 4.84 | – |

### hh-planten-intervall (intervall, Rundkurs, 1000 m)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Runde nach Südosten | 890 | -110 | 84 % | 16 % | 0 % | 0.0 | 0.0 | 6.74 | Planten un Blomen: 891 |
| neu | Runde nach Norden | 979 | -21 | 82 % | 18 % | 0 % | 0.0 | 0.0 | 14.3 | Planten un Blomen: 833 |
| neu | Runde nach Osten | 789 | -211 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 11.41 | Planten un Blomen: 789 |
| alt (3aa0e38) | Runde nach Westen | 1064 | +64 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 7.52 | Planten un Blomen: 1066 |
| alt (3aa0e38) | Runde nach Südosten | 959 | -41 | 85 % | 15 % | 0 % | 0.0 | 0.0 | 5.22 | Planten un Blomen: 958 |
| alt (3aa0e38) | Runde nach Nordwesten | 1142 | +142 | 100 % | 0 % | 0 % | 0.0 | 0.0 | 9.62 | Planten un Blomen: 1146 |

### hh-kellinghusen-tempo8 (tempo, Rundkurs, 8 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Westen | 8393 | +393 | 22 % | 52 % | 33 % | 1.19 | 0.12 | 5.01 | – |
| neu | Rundkurs nach Nordwesten | 8190 | +190 | 32 % | 46 % | 15 % | 1.34 | 0.37 | 4.52 | – |
| neu | Rundkurs nach Osten | 7437 | -563 | 34 % | 62 % | 30 % | 1.75 | 0.13 | 4.44 | – |
| alt (3aa0e38) | Rundkurs nach Süden | 7474 | -526 | 7 % | 86 % | 66 % | 0.13 | 0.13 | 4.15 | – |
| alt (3aa0e38) | Rundkurs nach Osten | 8421 | +421 | 29 % | 57 % | 39 % | 1.43 | 0.36 | 4.39 | – |
| alt (3aa0e38) | Rundkurs nach Südosten | 8550 | +550 | 21 % | 72 % | 53 % | 1.4 | 0.35 | 3.04 | – |

### b-brandenburger-rk10 (dauer, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Südosten | 10391 | +391 | 55 % | 38 % | 29 % | 1.06 | 0.1 | 4.52 | Großer Tiergarten: 1148 |
| neu | Rundkurs nach Nordwesten | 10586 | +586 | 50 % | 42 % | 37 % | 0.85 | 0.28 | 4.91 | Großer Tiergarten: 3158 |
| neu | Rundkurs nach Norden | 10135 | +135 | 49 % | 44 % | 42 % | 1.58 | 0.1 | 5.92 | Großer Tiergarten: 429 |
| alt (3aa0e38) | Rundkurs nach Norden | 10299 | +299 | 30 % | 65 % | 60 % | 1.36 | 0.19 | 3.98 | Großer Tiergarten: 230 |
| alt (3aa0e38) | Rundkurs nach Nordwesten | 9966 | -34 | 34 % | 64 % | 58 % | 1.1 | 0.5 | 3.91 | Großer Tiergarten: 3187 |
| alt (3aa0e38) | Rundkurs nach Südosten | 9061 | -939 | 29 % | 61 % | 56 % | 1.88 | 0.0 | 2.87 | Großer Tiergarten: 743 |

### b-hbf-tempelhof-ab12 (dauer, A→B, 12 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Bogen nach Südwesten | 11430 | -570 | 73 % | 23 % | 20 % | 0.52 | 0.26 | 3.32 | Großer Tiergarten: 1179 |
| neu | Bogen nach Osten | 11679 | -321 | 67 % | 31 % | 25 % | 1.28 | 0.0 | 3.94 | Großer Tiergarten: 0 |
| neu | Bogen nach Nordosten | 11794 | -206 | 64 % | 28 % | 23 % | 1.53 | 0.0 | 4.58 | Großer Tiergarten: 0 |
| alt (3aa0e38) | Bogen nach Südwesten | 12502 | +502 | 59 % | 39 % | 37 % | 1.36 | 0.08 | 2.88 | Großer Tiergarten: 1308 |
| alt (3aa0e38) | Bogen nach Osten | 11702 | -298 | 40 % | 58 % | 52 % | 1.71 | 0.0 | 3.33 | Großer Tiergarten: 0 |
| alt (3aa0e38) | Bogen nach Nordosten | 12179 | +179 | 43 % | 51 % | 48 % | 1.15 | 0.16 | 3.53 | Großer Tiergarten: 0 |

### b-tempelhof-wettkampf10 (wettkampf, Rundkurs, 10 km)

| Version | Variante | Länge | Abw. | Grün | Straße | Gehweg | Ampeln/km | ohne Ampel/km | Abb./km | Grünflächen (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| neu | Rundkurs nach Süden | 10193 | +193 | 45 % | 54 % | 38 % | 0.39 | 0.39 | 2.06 | – |
| neu | Rundkurs nach Westen | 10004 | +4 | 36 % | 55 % | 43 % | 0.4 | 0.0 | 4.4 | – |
| neu | Rundkurs nach Südosten | 9583 | -417 | 47 % | 44 % | 38 % | 0.52 | 0.0 | 2.92 | – |
| alt (3aa0e38) | Rundkurs nach Südosten | 9999 | -1 | 30 % | 68 % | 58 % | 0.4 | 0.2 | 2.5 | – |
| alt (3aa0e38) | Rundkurs nach Norden | 10366 | +366 | 28 % | 68 % | 65 % | 0.77 | 0.48 | 3.25 | – |
| alt (3aa0e38) | Rundkurs nach Süden | 9546 | -454 | 34 % | 66 % | 56 % | 0.52 | 0.31 | 1.89 | – |

