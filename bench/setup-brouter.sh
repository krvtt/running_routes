#!/usr/bin/env bash
# Lädt BRouter (Release) und Kartensegmente nach $BROUTER_HOME und startet den Server auf Port 17777.
# Aufruf: bench/setup-brouter.sh [Segment ...]   (Standard: E5_N50 E10_N50 = Hamburg, Berlin)
set -euo pipefail
VERSION="${BROUTER_VERSION:-1.7.10}"
HOME_DIR="${BROUTER_HOME:-$HOME/brouter}"
if [ $# -gt 0 ]; then SEGMENTS=("$@"); else SEGMENTS=(E5_N50 E10_N50); fi
mkdir -p "$HOME_DIR/segments4"
cd "$HOME_DIR"

# Programm: Release-Paket von GitHub, sonst aus dem Quellcode bauen
JAR="$(find . -name "brouter-*-all.jar" | head -n 1 || true)"
if [ -z "$JAR" ]; then
  if gh release download "v$VERSION" --repo abrensch/brouter --pattern "brouter-*.zip" --dir dl 2>/dev/null; then
    unzip -q -o dl/*.zip -d release
  else
    git clone -q --depth 1 --branch "v$VERSION" https://github.com/abrensch/brouter src
    (cd src && ./gradlew -q :brouter-server:fatJar)
    mkdir -p release && cp src/brouter-server/build/libs/brouter-*-all.jar release/ && cp -r src/misc/profiles2 release/
  fi
  JAR="$(find . -name "brouter-*-all.jar" | head -n 1)"
fi
PROFILES="$(dirname "$(find . -name lookups.dat -path "*profiles2*" | head -n 1)")"
mkdir -p "$PROFILES/customprofiles"
echo "BRouter: $JAR, Profile: $PROFILES"

# Kartensegmente (monatlich aktualisiert auf brouter.de)
for s in "${SEGMENTS[@]}"; do
  f="segments4/$s.rd5"
  if [ ! -s "$f" ]; then
    curl -fsSL --retry 3 -o "$f" "https://brouter.de/brouter/segments4/$s.rd5"
  fi
  ls -lh "$f"
done

nohup java -Xmx2g -DmaxRunningTime=300 -cp "$JAR" btools.server.RouteServer \
  segments4 "$PROFILES" customprofiles 17777 4 > server.log 2>&1 &
for i in $(seq 1 60); do
  if curl -s -o /dev/null "http://localhost:17777/brouter?lonlats=9.99,53.55|10.00,53.56&profile=trekking&format=geojson"; then
    echo "BRouter läuft"; exit 0
  fi
  sleep 2
done
echo "BRouter startet nicht"; tail -n 50 server.log; exit 1
