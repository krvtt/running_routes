/* Laufrouten Hamburg – Laufstrecken mit Wunschlänge auf Basis von BRouter und OpenStreetMap.
   Keine Konten, keine Schlüssel; Favoriten, Verlauf und Einstellungen bleiben auf dem Gerät. */
(function () {
'use strict';
if (!window.L) { document.getElementById('status').textContent = 'Kartenbibliothek nicht geladen – Seite neu laden.'; return; }

const APP_VERSION = '2.1.0';
const PROFILE_URL = 'profiles/laufen.brf';
const DEFAULT_SERVER = 'https://brouter.de';
const NOMINATIM = 'https://nominatim.openstreetmap.org';
const HH = { lat: 53.5511, lon: 9.9937 };
const HISTORY_MAX = 30;
const TILES = {
  osm:   { url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', max: 19, attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende' },
  osmde: { url: 'https://tile.openstreetmap.de/{z}/{x}/{y}.png', max: 18, attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende, Kacheln openstreetmap.de' },
  carto: { url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', max: 19, attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende &copy; CARTO' }
};
const COLORS = ['--v1', '--v2', '--v3', '--v4'];

// ---------- Trainingsarten ----------
// paceOff: Sekunden relativ zum normalen Dauerlauf-Tempo. p: Profilparameter für BRouter (siehe Profil).
const PRESETS = {
  dauer: { name: 'Lockerer Dauerlauf', km: 8, paceOff: 0, tol: 0.10, points: 5,
    hint: 'Grundlage, der Großteil deiner Kilometer. Viel Grün; eine Ampel ist okay, wenn sie Park oder Ufer erschließt.',
    p: { green_weight: 0.6, noise_weight: 0.4, town_weight: 0.3, big_road: 1.0, signal_cost: 100, crossing_unit: 25, zebra_cost: 20, turn_cost: 25, steps_factor: 3, paved_pref: 0, route_bonus: 0.1 } },
  lang: { name: 'Langer Lauf', km: 16, paceOff: 15, tol: 0.08, points: 6,
    hint: 'Ausdauer. Große Schleife, wenig Stopps und Kurven, gern am Wasser. Die Strecke soll man sich merken können.',
    p: { green_weight: 0.6, noise_weight: 0.4, town_weight: 0.5, big_road: 1.2, signal_cost: 150, crossing_unit: 35, zebra_cost: 30, turn_cost: 50, steps_factor: 3, paved_pref: 0, route_bonus: 0.15 } },
  recovery: { name: 'Recovery', km: 5, paceOff: 40, tol: 0.15, points: 4,
    hint: 'Erholung. Kurz, weich, ruhig, nah am Start. Die genaue Länge ist Nebensache.',
    p: { green_weight: 0.8, noise_weight: 0.6, town_weight: 0.4, big_road: 1.5, signal_cost: 80, crossing_unit: 30, zebra_cost: 20, turn_cost: 15, steps_factor: 5, paved_pref: -1, route_bonus: 0.05 } },
  tempo: { name: 'Tempodauerlauf', km: 8, paceOff: -25, tol: 0.08, points: 5,
    hint: 'Schwelle. Möglichst ohne Stopp, glatter Belag, wenig Kurven. Je ca. 1,5 km Ein- und Auslaufen einplanen; die Tempophase aufs längste Stück ohne Querung legen.',
    p: { green_weight: 0.3, noise_weight: 0.3, town_weight: 0.3, big_road: 1.0, signal_cost: 250, crossing_unit: 50, zebra_cost: 60, turn_cost: 60, steps_factor: 20, paved_pref: 1, route_bonus: 0.05 } },
  intervall: { name: 'Intervalle', lap: true, paceOff: -45, tol: 0.15, points: 4,
    hint: 'Runde ohne Querung für Wiederholungen. Setz den Start auf die Stelle, an der die Runde liegen soll (z. B. im Park).',
    p: { green_weight: 0.5, noise_weight: 0.3, town_weight: 0.2, big_road: 1.5, signal_cost: 500, crossing_unit: 100, zebra_cost: 200, turn_cost: 30, steps_factor: 30, paved_pref: 0.5, route_bonus: 0 } },
  wettkampf: { name: 'Wettkampf-Simulation', km: 10, paceOff: -40, tol: 0.02, points: 6,
    hint: 'Renn-Generalprobe. Exakte Distanz, Asphalt, keine Stopps, wenige Kurven. Start = Ziel empfohlen.',
    p: { green_weight: 0.2, noise_weight: 0.2, town_weight: 0.3, big_road: 1.0, signal_cost: 300, crossing_unit: 60, zebra_cost: 80, turn_cost: 80, steps_factor: 30, paved_pref: 1, route_bonus: 0 } },
  fahrtspiel: { name: 'Fahrtspiel', km: 8, paceOff: 0, tol: 0.12, points: 5,
    hint: 'Spielerisch. Abwechslungsreicher Belag, Stopps sind egal, Tempo nach Gefühl.',
    p: { green_weight: 0.6, noise_weight: 0.3, town_weight: 0.2, big_road: 0.8, signal_cost: 50, crossing_unit: 20, zebra_cost: 10, turn_cost: 10, steps_factor: 1.5, paved_pref: -0.5, route_bonus: 0.1 } }
};

// ---------- Helfer ----------
const $ = (id) => document.getElementById(id);
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const nf1 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const nf0 = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });
const km1 = (m) => nf1.format(m / 1000) + ' km';
function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function hav(a, b) {
  const R = 6371008.8, r = Math.PI / 180;
  const dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(s)));
}
function polyLen(pts) { let s = 0; for (let i = 1; i < pts.length; i++) s += hav(pts[i - 1], pts[i]); return s; }
function fmtLL(p) { return p.lat.toFixed(5) + ', ' + p.lon.toFixed(5); }
function parsePace(str) {
  const m = String(str || '').trim().replace(',', ':').replace('.', ':').match(/^(\d{1,2})(?::(\d{1,2}))?$/);
  if (!m) return null;
  const sec = Number(m[1]) * 60 + Number(m[2] || 0);
  return sec >= 150 && sec <= 1200 ? sec : null;
}
function fmtPace(sec) { const s = Math.round(sec); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
function fmtDur(sec) { const m = Math.round(sec / 60); return m >= 60 ? Math.floor(m / 60) + ' h ' + String(m % 60).padStart(2, '0') + ' min' : m + ' min'; }
function fmtDate(ts) { return new Date(ts).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }); }
function status(msg, cls) { const el = $('status'); el.textContent = msg || ''; el.className = cls || ''; }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
function fnv(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16); }
async function fetchT(url, opts, ms) {
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), ms || 30000);
  try { return await fetch(url, Object.assign({}, opts || {}, { signal: ctl.signal })); } finally { clearTimeout(t); }
}
function proj(o) {
  const k = 111320, kx = k * Math.cos(o.lat * Math.PI / 180);
  return { to: (p) => ({ x: (p.lon - o.lon) * kx, y: (p.lat - o.lat) * k }), from: (q) => ({ lat: o.lat + q.y / k, lon: o.lon + q.x / kx }) };
}
class RouteErr extends Error { constructor(msg, kind) { super(msg); this.kind = kind || 'other'; } }

// ---------- Speicher (IndexedDB, Rückfall: nur Sitzung) ----------
const Store = (() => {
  let dbp = null, memOnly = false;
  const mem = { kv: new Map(), fav: new Map(), hist: new Map() };
  function open() {
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      if (!('indexedDB' in window)) { rej(new Error('kein IndexedDB')); return; }
      let r;
      try { r = indexedDB.open('laufrouten', 1); } catch (e) { rej(e); return; }
      r.onupgradeneeded = () => {
        const d = r.result;
        if (!d.objectStoreNames.contains('kv')) d.createObjectStore('kv');
        if (!d.objectStoreNames.contains('fav')) d.createObjectStore('fav', { keyPath: 'id' });
        if (!d.objectStoreNames.contains('hist')) d.createObjectStore('hist', { keyPath: 'id' });
      };
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    }).catch((e) => { memOnly = true; throw e; });
    return dbp;
  }
  async function run(store, mode, fn) {
    try {
      const d = await open();
      return await new Promise((res, rej) => {
        const t = d.transaction(store, mode), req = fn(t.objectStore(store));
        t.oncomplete = () => res(req ? req.result : undefined);
        t.onerror = () => rej(t.error); t.onabort = () => rej(t.error);
      });
    } catch (e) {
      memOnly = true;
      return null;
    }
  }
  const memApi = {
    get: (k) => mem.kv.get(k), set: (k, v) => { mem.kv.set(k, v); },
    all: (s) => Array.from(mem[s].values()), put: (s, o) => { mem[s].set(o.id, o); }, del: (s, id) => { mem[s].delete(id); }, clear: (s) => { mem[s].clear(); }
  };
  return {
    isMem: () => memOnly,
    async get(k) { const v = await run('kv', 'readonly', (s) => s.get(k)); return memOnly ? memApi.get(k) : v; },
    async set(k, v) { await run('kv', 'readwrite', (s) => s.put(v, k)); if (memOnly) memApi.set(k, v); },
    async all(st) { const v = await run(st, 'readonly', (s) => s.getAll()); return memOnly ? memApi.all(st) : (v || []); },
    async put(st, o) { await run(st, 'readwrite', (s) => s.put(o)); if (memOnly) memApi.put(st, o); },
    async del(st, id) { await run(st, 'readwrite', (s) => s.delete(id)); if (memOnly) memApi.del(st, id); },
    async clear(st) { await run(st, 'readwrite', (s) => s.clear()); if (memOnly) memApi.clear(st); }
  };
})();
async function askPersist() {
  try { if (navigator.storage && navigator.storage.persist) return await navigator.storage.persist(); } catch (e) { /* egal */ }
  return false;
}

// ---------- Zustand ----------
const settings = { basePace: 405, server: DEFAULT_SERVER, tiles: 'osm', theme: 'auto', preset: 'dauer', mode: 'ab', lenMode: 'km', strides: false, lastStart: null, lastEnd: null };
let booted = false;
const state = { start: null, end: null, pick: null, variants: [], sel: 0, seed: 0, busy: false, lastKey: null, lastL: 0, notes: [], favs: [], histId: null, fromHistory: false };

// ---------- Karte ----------
const map = L.map('map', { zoomControl: true }).setView([HH.lat, HH.lon], 12);
map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
let tileLayer = null;
function setTiles(key) {
  const t = TILES[key] || TILES.osm;
  if (tileLayer) map.removeLayer(tileLayer);
  tileLayer = L.tileLayer(t.url, { maxZoom: t.max, attribution: t.attr, subdomains: 'abcd' }).addTo(map);
}
const routeLayer = L.layerGroup().addTo(map);
const infoLayer = L.layerGroup().addTo(map);
const markers = { start: null, end: null };
function pinIcon(letter, colorVar) {
  return L.divIcon({ className: '', iconSize: [30, 30], iconAnchor: [15, 30], html: '<div class="pin" style="background:' + cssVar(colorVar) + '"><span>' + letter + '</span></div>' });
}
function placeMarker(which) {
  if (markers[which]) { map.removeLayer(markers[which]); markers[which] = null; }
  const p = state[which];
  if (!p || (which === 'end' && isLoopMode())) return;
  const m = L.marker([p.lat, p.lon], { draggable: true, zIndexOffset: 1000, icon: pinIcon(which === 'start' ? 'A' : 'B', which === 'start' ? '--ok' : '--err') }).addTo(map);
  m.on('dragend', () => { const ll = m.getLatLng(); setPoint(which, { lat: ll.lat, lon: ll.lng, label: 'Karte ' + fmtLL({ lat: ll.lat, lon: ll.lng }) }, false); });
  markers[which] = m;
}
function isLoopMode() { return settings.mode === 'rt' || PRESETS[settings.preset].lap; }
function setPoint(which, p, pan) {
  state[which] = p ? { lat: p.lat, lon: p.lon, label: p.label || fmtLL(p) } : null;
  const el = $(which + 'Pt');
  el.textContent = p ? state[which].label : 'noch nicht gesetzt';
  el.classList.toggle('set', !!p);
  placeMarker(which);
  if (p && pan !== false) map.setView([p.lat, p.lon], Math.max(map.getZoom(), 14));
  $(which + 'Results').innerHTML = '';
  settings[which === 'start' ? 'lastStart' : 'lastEnd'] = state[which];
  if (booted) saveSettings();
}
function setPick(which) {
  state.pick = which;
  document.querySelectorAll('[data-pick]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.pick === which)));
  if (which) status('Jetzt auf die Karte tippen, um ' + (which === 'start' ? 'den Start' : 'das Ziel') + ' zu setzen.');
}
map.on('click', (e) => {
  let which = state.pick;
  if (!which) which = !state.start ? 'start' : (!isLoopMode() && !state.end ? 'end' : null);
  if (!which) return;
  const p = { lat: e.latlng.lat, lon: e.latlng.lng };
  setPoint(which, { lat: p.lat, lon: p.lon, label: 'Karte ' + fmtLL(p) }, false);
  setPick(null); status('');
});

// ---------- Adresssuche (Nominatim, max. 1 Anfrage/s) ----------
let lastGeo = 0;
async function geocode(q) {
  const wait = 1100 - (Date.now() - lastGeo);
  if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  lastGeo = Date.now();
  const u = NOMINATIM + '/search?' + new URLSearchParams({ q, format: 'jsonv2', limit: '6', countrycodes: 'de', viewbox: '9.70,53.75,10.35,53.38', bounded: '0', 'accept-language': 'de' });
  let res;
  try { res = await fetchT(u, { headers: { Accept: 'application/json' } }, 15000); } catch (e) { throw new Error('Adresssuche nicht erreichbar. Internet prüfen.'); }
  if (!res.ok) throw new Error('Adresssuche antwortet mit Fehler ' + res.status + '.');
  const arr = await res.json();
  return arr.map((x) => ({ lat: Number(x.lat), lon: Number(x.lon), label: String(x.display_name || q).split(',').slice(0, 3).join(',') }));
}

// ---------- BRouter ----------
function server() { return (settings.server || DEFAULT_SERVER).replace(/\/+$/, ''); }
let profileText = null;
async function loadProfileText() {
  if (profileText) return profileText;
  let res;
  try { res = await fetchT(PROFILE_URL, { cache: 'no-cache' }, 15000); } catch (e) { res = null; }
  if (!res || !res.ok) throw new RouteErr('Routing-Profil konnte nicht geladen werden. Seite neu laden.', 'other');
  profileText = await res.text();
  return profileText;
}
async function ensureProfile(force) {
  const text = await loadProfileText();
  const hash = fnv(text + '|' + server());
  if (!force) {
    const c = await Store.get('profile');
    if (c && c.hash === hash && Date.now() - c.ts < 6 * 3600e3) return c.id;
  }
  let res, j = null;
  try { res = await fetchT(server() + '/brouter/profile', { method: 'POST', body: text, headers: { 'Content-Type': 'text/plain' } }, 30000); }
  catch (e) { throw new RouteErr('Routing-Server nicht erreichbar. Internet prüfen oder später erneut versuchen.', 'net'); }
  try { j = await res.json(); } catch (e) { /* kein JSON */ }
  if (!j || !j.profileid || j.error) throw new RouteErr('Routing-Profil wurde vom Server abgelehnt' + (j && j.error ? ': ' + j.error : '.'), 'profile');
  await Store.set('profile', { id: j.profileid, hash, ts: Date.now() });
  return j.profileid;
}
function errKind(text) {
  const t = String(text).toLowerCase();
  if (/profile custom_\w+(\.brf)* does not exist/.test(t)) return 'profile'; // Server hat hochgeladenes Profil verworfen
  if (/not mapped|no track found|island|position not|not found in/.test(t)) return 'nomatch';
  if (/killed|timeout|watchdog|busy|too many/.test(t)) return 'busy';
  return 'other';
}
function errText(text, kind) {
  if (kind === 'nomatch') return 'Ein Punkt liegt zu weit von einem Weg (z. B. im Wasser) oder ist nicht erreichbar.';
  if (kind === 'busy') return 'Routing-Server ist ausgelastet. Gleich noch einmal versuchen.';
  const s = String(text).replace(/\s+/g, ' ').trim();
  return 'Routing-Fehler: ' + (s.length > 160 ? s.slice(0, 160) + '…' : s || 'unbekannt');
}
const net = { calls: 0 };
function query(points, params, extra) {
  const parts = ['lonlats=' + points.map((p) => p.lon.toFixed(6) + ',' + p.lat.toFixed(6)).join('|'),
    'profile=' + extra.pid, 'alternativeidx=' + (extra.alt || 0), 'format=geojson'];
  Object.keys(params).forEach((k) => parts.push('profile:' + k + '=' + params[k]));
  return parts.join('&');
}
// Rundkurs-Stützpunkte: Fächer aus n-1 Punkten im Abstand R um den Start (Geometrie wie BRouter-Rundkurs).
// Bewusst clientseitig: Der Rundkurs-Modus des Servers ist zwischen BRouter-Versionen nicht kompatibel.
function circlePoints(A, R, n, dir) {
  const P = proj(A), out = [A];
  for (let i = 1; i < n; i++) { const a = (dir - (90 - 180 * i / n)) * Math.PI / 180; out.push(P.from({ x: R * Math.sin(a), y: R * Math.cos(a) })); }
  out.push(A); return out;
}
async function brouter(points, ctx, extra) {
  for (let attempt = 0; attempt < 2; attempt++) {
    const q = query(points, ctx.params, Object.assign({ pid: ctx.pid }, extra || {}));
    let res, text;
    net.calls++; ctx.onCall && ctx.onCall();
    try { res = await fetchT(server() + '/brouter?' + q, {}, 60000); text = await res.text(); }
    catch (e) { throw new RouteErr(e && e.name === 'AbortError' ? 'Routing-Server antwortet nicht (Zeitüberschreitung).' : 'Routing-Server nicht erreichbar. Internet prüfen.', 'net'); }
    if (res.ok && text.trim().charAt(0) === '{') {
      let gj;
      try { gj = JSON.parse(text); } catch (e) { throw new RouteErr('Antwort des Routing-Servers ist unvollständig.', 'other'); }
      return parseRoute(gj);
    }
    const kind = errKind(text);
    if (kind === 'profile' && attempt === 0) { ctx.pid = await ensureProfile(true); continue; }
    throw new RouteErr(errText(text, kind), kind);
  }
  throw new RouteErr('Routing fehlgeschlagen.', 'other');
}

// ---------- Auswertung der Route ----------
function parseTags(s) {
  const o = {};
  String(s || '').split(' ').forEach((t) => { const i = t.indexOf('='); if (i > 0) o[t.slice(0, i)] = t.slice(i + 1); });
  return o;
}
function surfGroup(s) {
  if (!s) return 'unk';
  if (/^(asphalt|concrete)/.test(s)) return 'asph';
  if (/^(paved|paving_stones|sett|cobblestone|grass_paver|metal|wood)$/.test(s)) return 'paved';
  return 'unp';
}
function wayGroup(h) {
  if (/^(path|track|bridleway)$/.test(h)) return 'Park-/Feldweg';
  if (/^(footway|pedestrian|steps|living_street)$/.test(h)) return 'Fußweg';
  if (/^(cycleway)$/.test(h)) return 'Radweg';
  if (/^(residential|service|unclassified|road)$/.test(h)) return 'Kleine Straße';
  if (/^tertiary/.test(h)) return 'Mittlere Straße';
  if (/^(primary|secondary|trunk)/.test(h)) return 'Große Straße';
  return 'Sonstiges';
}
function parseRoute(gj) {
  const f = gj && gj.features && gj.features[0];
  if (!f || !f.geometry || !f.geometry.coordinates || f.geometry.coordinates.length < 2) throw new RouteErr('Keine Route gefunden.', 'nomatch');
  const p = f.properties || {};
  const coords = f.geometry.coordinates.map((c) => [Number(c[0]), Number(c[1]), c.length > 2 ? Number(c[2]) : NaN]);
  const dist = Number(p['track-length']) || polyLen(coords.map((c) => ({ lat: c[1], lon: c[0] })));
  const v = { coords, dist, cost: Number(p.cost) || dist * 2, up: Number(p['filtered ascend']) || 0, turns: countTurns(coords) };
  v.m = metrics(p.messages, dist);
  return v;
}
function metrics(msgs, dist) {
  const m = { green: 0, big: 0, surf: { asph: 0, paved: 0, unp: 0, unk: 0 }, way: {}, signals: [], zebras: [], cross: [], tot: 0, ok: false };
  if (!Array.isArray(msgs) || msgs.length < 2) return m;
  const h = msgs[0], col = (n, d) => { const i = h.indexOf(n); return i >= 0 ? i : d; };
  const iLon = col('Longitude', 0), iLat = col('Latitude', 1), iDist = col('Distance', 3), iWay = col('WayTags', 9), iNode = col('NodeTags', 10);
  let pos = 0;
  msgs.slice(1).forEach((row) => {
    const d = Number(row[iDist]) || 0; pos += d; m.tot += d;
    const w = parseTags(row[iWay]), n = parseTags(row[iNode]);
    if (Math.max(Number(w.estimated_forest_class || 0), Number(w.estimated_river_class || 0)) >= 3) m.green += d;
    const hw = w.highway || '';
    if (/^(primary|secondary|trunk)(_link)?$/.test(hw)) m.big += d;
    m.surf[surfGroup(w.surface)] += d;
    const g = wayGroup(hw); m.way[g] = (m.way[g] || 0) + d;
    const pt = { lat: Number(row[iLat]) / 1e6, lon: Number(row[iLon]) / 1e6, pos };
    if (n.highway === 'traffic_signals' || n.crossing === 'traffic_signals') m.signals.push(pt);
    else if (n.crossing === 'zebra' || n.crossing === 'marked') m.zebras.push(pt);
    else if (Number(n.estimated_crossing_class || 0) >= 1) m.cross.push(Object.assign(pt, { cls: Number(n.estimated_crossing_class) }));
  });
  m.signals = dedupe(m.signals, 40); m.zebras = dedupe(m.zebras, 25); m.cross = dedupe(m.cross, 25);
  m.ok = m.tot > 0;
  const scale = m.tot > 0 ? dist / m.tot : 1; // auf Gesamtlänge normieren
  m.green *= scale; m.big *= scale;
  return m;
}
// Abbiegungen aus der Geometrie: Richtungswechsel > 50° zwischen Abschnitten ≥ 12 m, Wechsel innerhalb 25 m zählen einmal
function countTurns(coords) {
  const ll = (c) => ({ lat: c[1], lon: c[0] });
  const pts = [coords[0]];
  for (let i = 1; i < coords.length; i++) if (hav(ll(pts[pts.length - 1]), ll(coords[i])) >= 12) pts.push(coords[i]);
  let turns = 0, pos = 0, lastTurn = -1e9;
  for (let i = 1; i < pts.length - 1; i++) {
    pos += hav(ll(pts[i - 1]), ll(pts[i]));
    if (angDiff(bearing(pts[i - 1], pts[i]), bearing(pts[i], pts[i + 1])) > 50 && pos - lastTurn > 25) { turns++; lastTurn = pos; }
  }
  return turns;
}
function dedupe(arr, gap) { const out = []; arr.forEach((x) => { const l = out[out.length - 1]; if (!l || x.pos - l.pos > gap) out.push(x); }); return out; }
function quality(v) { return clamp(Math.round(100 * v.dist / Math.max(v.cost, v.dist)), 0, 100); }
function scoreOf(v, L, tol) {
  const err = Math.abs(v.dist - L) / L;
  return (v.cost / Math.max(v.dist, 1)) * (1 + Math.max(0, err - tol / 2) * 3);
}

// ---------- Längenregelung ----------
function loopFactor(n) { return 2 + (n - 2) * 2 * Math.sin(Math.PI / (2 * n)); } // Radius → Kreisroute (Geometrie)
async function fitLoop(A, L, dir, preset, ctx) {
  const n = preset.points, hist = [];
  let R = L / (loopFactor(n) * 1.25), best = null, misses = 0;
  for (let i = 0; i < ctx.maxIter; i++) {
    let r;
    try { r = await brouter(circlePoints(A, R, n, dir), ctx, {}); }
    catch (e) {
      // Stützpunkt im Wasser o. Ä.: Richtung leicht drehen und Radius verkleinern (eigenes Budget)
      if (e.kind === 'nomatch' && misses < 3) { misses++; dir += 25; R *= 0.85; i--; continue; }
      if (best) break; throw e;
    }
    r.err = (r.dist - L) / L; hist.push({ R, d: r.dist });
    if (!best || Math.abs(r.err) < Math.abs(best.err)) best = r;
    if (Math.abs(r.err) <= ctx.tol) break;
    let Rn = R * L / r.dist;
    const k = hist.length;
    if (k >= 2) {
      const a = hist[k - 2], b = hist[k - 1], slope = (b.d - a.d) / (b.R - a.R);
      if (Math.abs(b.R - a.R) > 5 && slope > 1) Rn = b.R + (L - b.d) / slope;
    }
    R = clamp(Rn, R * 0.4, R * 2.5);
  }
  return best;
}
function viaPoint(A, B, t, h) {
  const P = proj(A), a = P.to(A), b = P.to(B);
  const dx = b.x - a.x, dy = b.y - a.y, D = Math.hypot(dx, dy) || 1;
  return P.from({ x: a.x + dx * t - dy / D * h, y: a.y + dy * t + dx / D * h }); // h > 0: links der Laufrichtung
}
function solveH(A, B, t, sign, G) {
  const len = (h) => polyLen([A, viaPoint(A, B, t, sign * h), B]);
  let lo = 0, hi = Math.max(G, 200);
  while (len(hi) < G && hi < 1e6) hi *= 2;
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (len(mid) < G) lo = mid; else hi = mid; }
  return (lo + hi) / 2;
}
async function fitDetour(A, B, L, f0, t, sign, ctx) {
  let h = solveH(A, B, t, sign, L / f0), best = null; const hist = [];
  for (let i = 0; i < ctx.maxIter; i++) {
    const via = viaPoint(A, B, t, sign * h);
    let r;
    try { r = await brouter([A, via, B], ctx, {}); }
    catch (e) { if (e.kind === 'nomatch' && i < ctx.maxIter - 1) { h *= 0.75; continue; } if (best) break; throw e; }
    r.err = (r.dist - L) / L; r.via = via; hist.push({ h, d: r.dist });
    if (!best || Math.abs(r.err) < Math.abs(best.err)) best = r;
    if (Math.abs(r.err) <= ctx.tol) break;
    const k = hist.length; let hn;
    if (k >= 2 && Math.abs(hist[k - 1].d - hist[k - 2].d) > 50) {
      const p1 = hist[k - 2], p2 = hist[k - 1];
      hn = p2.h + (L - p2.d) * (p2.h - p1.h) / (p2.d - p1.d);
    } else {
      const geo = polyLen([A, via, B]);
      hn = solveH(A, B, t, sign, L / clamp(r.dist / geo, 1, 3));
    }
    h = clamp(hn, 0, h * 3 + 500);
  }
  return best;
}

// ---------- Berechnen ----------
function presetPace() {
  const pr = PRESETS[settings.preset];
  return parsePace(pr.lap ? $('lapPace').value : $('paceInput').value) || (settings.basePace + pr.paceOff);
}
function targetMeters() {
  const pr = PRESETS[settings.preset];
  if (pr.lap) { const lap = Number($('lapInput').value); return lap >= 300 ? lap : null; }
  if (settings.lenMode === 'km') { const km = parseFloat(String($('kmInput').value).replace(',', '.')); return km > 0 ? km * 1000 : null; }
  const min = parseFloat($('durInput').value), pace = presetPace();
  return min > 0 && pace ? (min * 60 / pace) * 1000 : null;
}
function updateCalc() {
  const pr = PRESETS[settings.preset], L = targetMeters(), pace = presetPace();
  if (pr.lap) {
    const reps = Math.max(1, Number($('repsInput').value) || 1);
    $('calcOut').textContent = L ? reps + ' × ' + nf0.format(L) + ' m = ' + km1(L * reps) + ' Belastung · je ' + fmtDur(L / 1000 * pace) : 'Rundenlänge ab 300 m';
    return;
  }
  $('calcOut').textContent = L ? '= ' + km1(L) + ' · ' + fmtDur(L / 1000 * pace) + ' bei ' + fmtPace(pace) + ' min/km' : '';
}

async function compute(again) {
  if (state.busy) return;
  const pr = PRESETS[settings.preset], L = targetMeters(), A = state.start;
  if (!A) { status('Start fehlt: Favorit antippen, Adresse suchen, GPS oder „Auf Karte“.', 'err'); return; }
  if (!L || L < 300 || L > 42500) { status(pr.lap ? 'Rundenlänge zwischen 300 und 3.000 m angeben.' : 'Länge zwischen 1 und 42 km angeben.', 'err'); return; }
  const loop = isLoopMode() || (state.end && hav(A, state.end) < 150);
  if (!loop && !state.end) { status('Ziel fehlt – oder auf „Rundkurs“ umschalten.', 'err'); return; }
  if (navigator.onLine === false) { status('Offline: Die Berechnung braucht Internet. Der Verlauf ist trotzdem verfügbar.', 'err'); return; }
  const B = loop ? A : state.end;
  const key = JSON.stringify([settings.preset, loop, A.lat, A.lon, B.lat, B.lon, Math.round(L)]);
  const reuse = !!again && key === state.lastKey;
  state.seed = reuse ? state.seed + 1 : 0;
  state.lastKey = key; state.lastL = L; state.fromHistory = false;
  const notes = [];
  setBusy(true);
  const t0 = performance.now();
  let calls = 0;
  const ctx = { params: pr.p, tol: pr.tol, maxIter: pr.tol <= 0.03 ? 4 : 3, onCall: () => { calls++; status('Rechne … (' + calls + ' Anfragen)'); } };
  try {
    status('Verbinde mit Routing-Server …');
    ctx.pid = await ensureProfile(false);
    let vs = [];
    if (loop) {
      const base = (state.seed * 47 + 20) % 360;
      const dirs = [base, base + 120, base + 240];
      const res = await Promise.allSettled(dirs.map((d) => fitLoop(A, L, d, pr, ctx)));
      res.forEach((x, i) => {
        if (x.status === 'fulfilled' && x.value) vs.push(Object.assign(x.value, { name: (pr.lap ? 'Runde ' : 'Rundkurs ') + compass(dirs[i]) }));
        else if (x.status === 'rejected') notes.push(x.reason.message);
      });
    } else {
      const D = hav(A, B);
      const direct = await brouter([A, B], ctx, { alt: 0 });
      direct.err = (direct.dist - L) / L;
      if (direct.dist >= L * (1 - pr.tol)) {
        vs.push(Object.assign(direct, { name: 'Direkt' }));
        const alts = await Promise.allSettled((state.seed % 2 ? [2, 3] : [1, 2]).map((alt) => brouter([A, B], ctx, { alt })));
        alts.forEach((x, i) => { if (x.status === 'fulfilled') vs.push(Object.assign(x.value, { err: (x.value.dist - L) / L, name: 'Alternative ' + (i + 1) })); });
        if (direct.dist > L * (1 + pr.tol)) notes.push('Der kürzeste sinnvolle Weg ist schon ' + km1(direct.dist) + ' lang.');
      } else {
        const f0 = clamp(direct.dist / Math.max(D, 1), 1.1, 2.5);
        const t = [0.5, 0.35, 0.65][state.seed % 3];
        const res = await Promise.allSettled([fitDetour(A, B, L, f0, t, 1, ctx), fitDetour(A, B, L, f0, t, -1, ctx)]);
        res.forEach((x, i) => {
          if (x.status === 'fulfilled' && x.value) vs.push(Object.assign(x.value, { name: i === 0 ? 'Bogen links' : 'Bogen rechts' }));
          else if (x.status === 'rejected') notes.push(x.reason.message);
        });
        if (vs.length) {
          const bestV = vs.slice().sort((a, b) => scoreOf(a, L, pr.tol) - scoreOf(b, L, pr.tol))[0];
          try {
            const alt = await brouter([A, bestV.via, B], ctx, { alt: 1 + (state.seed % 2) });
            alt.err = (alt.dist - L) / L; alt.via = bestV.via;
            if (Math.abs(alt.dist - bestV.dist) > 30 || Math.abs(alt.cost - bestV.cost) > 30) vs.push(Object.assign(alt, { name: bestV.name + ', Alternative' }));
          } catch (e) { /* optional */ }
        }
      }
    }
    if (!vs.length) throw new RouteErr(notes[0] || 'Keine Route gefunden.', 'other');
    vs.forEach((v) => {
      v.q = quality(v); v.score = scoreOf(v, L, pr.tol);
      if (settings.strides) v.strides = findStrides(v);
    });
    vs.sort((a, b) => a.score - b.score);
    vs.forEach((v, i) => { v.colorVar = COLORS[i % COLORS.length]; });
    const off = vs.filter((v) => Math.abs(v.err) > pr.tol).length;
    if (off === vs.length) notes.push('Keine Variante trifft die Länge auf ±' + Math.round(pr.tol * 100) + ' % – beste Näherung angezeigt.');
    state.variants = vs; state.sel = 0; state.notes = notes;
    renderResults(true);
    await saveHistory();
    const secs = ((performance.now() - t0) / 1000).toFixed(1);
    status(notes.length ? notes[0] : 'Fertig in ' + secs + ' s (' + calls + ' Anfragen). ' + vs.length + ' Varianten, beste zuerst.', notes.length ? 'warn' : 'ok');
  } catch (e) {
    status(e.message || String(e), 'err');
  } finally {
    setBusy(false);
  }
}
function compass(deg) { return ['nach Norden', 'nach Nordosten', 'nach Osten', 'nach Südosten', 'nach Süden', 'nach Südwesten', 'nach Westen', 'nach Nordwesten'][Math.round((((deg % 360) + 360) % 360) / 45) % 8]; }
function setBusy(b) {
  state.busy = b;
  $('goBtn').disabled = b; $('againBtn').disabled = b;
  $('goBtn').textContent = b ? 'Rechne …' : 'Route berechnen';
}

// ---------- Steigerungen ----------
function bearing(a, b) { const P = proj({ lat: a[1], lon: a[0] }), q = P.to({ lat: b[1], lon: b[0] }); return Math.atan2(q.x, q.y) * 180 / Math.PI; }
function angDiff(a, b) { const d = Math.abs(a - b) % 360; return d > 180 ? 360 - d : d; }
function cumOf(v) {
  if (v._cum) return v._cum;
  const c = v.coords, cum = [0];
  for (let i = 1; i < c.length; i++) cum.push(cum[i - 1] + hav({ lat: c[i - 1][1], lon: c[i - 1][0] }, { lat: c[i][1], lon: c[i][0] }));
  Object.defineProperty(v, '_cum', { value: cum, enumerable: false, writable: true });
  return cum;
}
function findStrides(v) {
  const c = v.coords, cum = cumOf(v), tot = cum[cum.length - 1] || 1, scale = v.dist / tot;
  const stops = [].concat(v.m.signals, v.m.zebras, v.m.cross).map((s) => s.pos / scale);
  let best = null;
  for (let i = 0; i < c.length - 1; i++) {
    if (cum[i] < tot * 0.4) continue;
    if (cum[i + 1] - cum[i] < 1) continue;
    const b0 = bearing(c[i], c[i + 1]);
    let j = i + 1;
    while (j < c.length - 1 && (cum[j + 1] - cum[j] < 1 || angDiff(bearing(c[j], c[j + 1]), b0) < 20)) j++;
    // gerades Stück i..j an Stopps aufteilen, längstes freies Teilstück nehmen
    const cuts = [cum[i]].concat(stops.filter((s) => s > cum[i] && s < cum[j]).sort((a, b) => a - b), [cum[j]]);
    for (let k = 1; k < cuts.length; k++) {
      const a = cuts[k - 1] + (k > 1 ? 15 : 0), b = cuts[k] - (k < cuts.length - 1 ? 15 : 0), len = b - a;
      if (len >= 100 && !stops.some((s) => s > a - 15 && s < a) && (!best || len * scale > best.len)) {
        let ia = i; while (ia < j && cum[ia + 1] <= a) ia++;
        let jb = ia; while (jb < j && cum[jb] < b) jb++;
        best = { i: ia, j: jb, len: len * scale, at: a * scale };
      }
    }
    if (j > i + 1) i = j - 1;
  }
  return best;
}

// ---------- Anzeige ----------
function redraw() {
  routeLayer.clearLayers(); infoLayer.clearLayers();
  state.variants.forEach((v, i) => { if (i !== state.sel) addLine(v, i, false); });
  const v = state.variants[state.sel];
  if (v) { addLine(v, state.sel, true); addInfo(v); }
  placeMarker('start'); placeMarker('end');
}
function addLine(v, i, selected) {
  const ll = v.coords.map((c) => [c[1], c[0]]);
  L.polyline(ll, { color: '#ffffff', weight: selected ? 11 : 7, opacity: selected ? 0.95 : 0.6, interactive: false }).addTo(routeLayer);
  const line = L.polyline(ll, { color: cssVar(v.colorVar || '--v1'), weight: selected ? 6 : 4, opacity: selected ? 1 : 0.55, bubblingMouseEvents: false }).addTo(routeLayer);
  line.on('click', () => select(i));
}
function pointAt(v, m) {
  const cum = cumOf(v), c = v.coords, tot = cum[cum.length - 1], target = m * tot / v.dist;
  let lo = 0, hi = cum.length - 1;
  while (hi - lo > 1) { const md = (lo + hi) >> 1; if (cum[md] < target) lo = md; else hi = md; }
  const seg = cum[hi] - cum[lo] || 1, t = clamp((target - cum[lo]) / seg, 0, 1);
  return [c[lo][1] + t * (c[hi][1] - c[lo][1]), c[lo][0] + t * (c[hi][0] - c[lo][0])];
}
function addInfo(v) {
  const step = v.dist > 25000 ? 2000 : (v.dist < 2500 ? 250 : 1000);
  for (let m = step; m < v.dist - step * 0.15; m += step) {
    const label = step < 1000 ? nf0.format(m) : String(Math.round(m / 1000));
    L.marker(pointAt(v, m), { interactive: false, keyboard: false, icon: L.divIcon({ className: 'kmm', iconSize: [22, 22], iconAnchor: [11, 11], html: '<span>' + label + '</span>' }) }).addTo(infoLayer);
  }
  v.m.signals.forEach((p) => L.circleMarker([p.lat, p.lon], { radius: 6, color: '#ffffff', weight: 2, fillColor: cssVar('--err'), fillOpacity: 1, interactive: false }).addTo(infoLayer));
  v.m.cross.forEach((p) => L.marker([p.lat, p.lon], { interactive: false, keyboard: false, icon: L.divIcon({ className: 'xm', iconSize: [20, 20], iconAnchor: [10, 10], html: '<span>' + p.cls + '</span>' }) }).addTo(infoLayer));
  if (v.strides) {
    const seg = v.coords.slice(v.strides.i, v.strides.j + 1).map((c) => [c[1], c[0]]);
    L.polyline(seg, { color: cssVar('--ok'), weight: 10, opacity: 0.9, dashArray: '2 10', lineCap: 'round', interactive: false }).addTo(infoLayer);
  }
}
function select(i) { state.sel = i; renderResults(false); if (!state.fromHistory) saveHistory(); }
function renderResults(fit) {
  const pace = presetPace();
  $('resCard').hidden = !state.variants.length;
  $('againBtn').hidden = state.fromHistory;
  $('variants').innerHTML = state.variants.map((v, i) => {
    const pct = Math.round((v.err || 0) * 100);
    return '<button type="button" class="variant" data-i="' + i + '" aria-pressed="' + (i === state.sel) + '">' +
      '<span class="sw" style="background:' + cssVar(v.colorVar || '--v1') + '"></span>' +
      '<span class="body"><span class="name">' + esc(v.name) + (i === 0 && state.variants.length > 1 ? '<span class="badge">Empfehlung</span>' : '') + '</span>' +
      '<span class="meta">' + fmtDur(v.dist / 1000 * pace) + ' · ' + (pct >= 0 ? '+' : '') + pct + ' % · Qualität ' + v.q + '</span>' +
      '<span class="meta">Grün ' + km1(v.m.green) + ' · ' + v.m.signals.length + ' Ampel' + (v.m.signals.length === 1 ? '' : 'n') + ' · ' + v.m.cross.length + ' Querung' + (v.m.cross.length === 1 ? '' : 'en') + '</span></span>' +
      '<span class="km">' + nf1.format(v.dist / 1000) + '</span></button>';
  }).join('');
  $('variants').querySelectorAll('.variant').forEach((b) => b.addEventListener('click', () => select(Number(b.dataset.i))));
  renderDetail(pace);
  redraw();
  if (fit && state.variants.length) {
    const b = L.latLngBounds([]);
    state.variants.forEach((v) => v.coords.forEach((c) => b.extend([c[1], c[0]])));
    map.fitBounds(b, { padding: [24, 24] });
  }
  $('shareBtn').hidden = !canShareFile();
}
function tradeText(a, b) {
  const parts = [];
  const dg = a.m.green - b.m.green;
  if (Math.abs(dg) >= 150) parts.push(dg > 0 ? '+' + km1(dg) + ' im Grünen/am Wasser' : km1(-dg) + ' weniger Grün');
  const ds = a.m.signals.length - b.m.signals.length, dx = a.m.cross.length - b.m.cross.length;
  if (ds) parts.push(Math.abs(ds) + (Math.abs(ds) === 1 ? ' Ampel ' : ' Ampeln ') + (ds > 0 ? 'mehr' : 'weniger'));
  if (dx) parts.push(Math.abs(dx) + (Math.abs(dx) === 1 ? ' Querung ' : ' Querungen ') + (dx > 0 ? 'mehr' : 'weniger'));
  const db = a.m.big - b.m.big;
  if (Math.abs(db) >= 150) parts.push(km1(Math.abs(db)) + (db > 0 ? ' mehr' : ' weniger') + ' an großen Straßen');
  if (a.turns != null && b.turns != null) { const dt = a.turns - b.turns; if (Math.abs(dt) >= 3) parts.push(Math.abs(dt) + ' Abbiegungen ' + (dt > 0 ? 'mehr' : 'weniger')); }
  if (!parts.length) return 'Kaum Unterschied zu „' + b.name + '“, etwas besser nach deiner Trainingsart.';
  return 'Gegenüber „' + b.name + '“: ' + parts.join(', ') + '. Nach deiner Trainingsart unterm Strich besser.';
}
function renderDetail(pace) {
  const v = state.variants[state.sel], pr = PRESETS[settings.preset];
  if (!v) { $('detail').innerHTML = ''; return; }
  const km = v.dist / 1000;
  let html = '<div class="stats">' +
    '<div class="stat"><span class="lbl">Distanz</span><b>' + km1(v.dist) + '</b></div>' +
    '<div class="stat"><span class="lbl">Zeit</span><b>' + fmtDur(km * pace) + '</b></div>' +
    '<div class="stat"><span class="lbl">Qualität</span><b>' + v.q + '/100</b></div></div>';
  if (pr.lap) {
    const reps = Math.max(1, Number($('repsInput').value) || 1);
    html += '<p class="trade"><b>' + reps + ' × ' + nf0.format(v.dist) + ' m</b> = ' + km1(v.dist * reps) + ' Belastung, je Runde ca. ' + fmtDur(km * pace) + '.' +
      (v.m.signals.length + v.m.cross.length === 0 ? ' Ohne Ampel und ohne Querung.' : ' Achtung: ' + (v.m.signals.length + v.m.cross.length) + ' Stopp(s) pro Runde.') + '</p>';
  }
  if (state.sel === 0 && state.variants.length > 1 && !state.fromHistory) html += '<p class="trade">' + esc(tradeText(v, state.variants[1])) + '</p>';
  const tpk = v.turns != null && km > 0 ? v.turns / km : null;
  html += '<div class="kv">' +
    '<span>Im Grünen / am Wasser</span><span>' + km1(v.m.green) + ' (' + Math.round(100 * v.m.green / Math.max(v.dist, 1)) + ' %)</span>' +
    '<span>An großen Straßen</span><span>' + km1(v.m.big) + '</span>' +
    '<span>Ampeln</span><span>' + v.m.signals.length + '</span>' +
    '<span>Querungen ohne Ampel</span><span>' + v.m.cross.length + (v.m.cross.length ? ' (max. Risiko ' + Math.max.apply(null, v.m.cross.map((c) => c.cls)) + ')' : '') + '</span>' +
    '<span>Zebrastreifen</span><span>' + v.m.zebras.length + '</span>' +
    (tpk != null ? '<span>Abbiegungen</span><span>' + v.turns + ' (' + nf1.format(tpk) + ' pro km)</span>' : '') +
    '<span>Anstieg</span><span>' + nf0.format(v.up) + ' m</span></div>';
  if (v.strides) html += '<p class="trade">Steigerungen: gerades Stück ohne Querung, ' + nf0.format(v.strides.len) + ' m ab km ' + nf1.format(v.strides.at / 1000) + ' (grün gestrichelt).</p>';
  else if (settings.strides && !pr.lap) html += '<p class="hint">Kein gerades Stück ≥ 100 m ohne Querung in der zweiten Hälfte gefunden.</p>';
  const s = v.m.surf, st = s.asph + s.paved + s.unp + s.unk;
  if (st > 0) {
    const lbl = { asph: 'Asphalt', paved: 'Pflaster', unp: 'Unbefestigt', unk: 'Unbekannt' };
    const order = ['asph', 'paved', 'unp', 'unk'].filter((k) => s[k] > 0);
    html += '<div class="block"><span class="lbl">Belag</span><div class="bar">' +
      order.map((k) => '<span style="width:' + (s[k] / st * 100).toFixed(1) + '%;background:var(--s-' + k + ')"></span>').join('') + '</div><div class="legend">' +
      order.map((k) => '<span><i style="background:var(--s-' + k + ')"></i>' + lbl[k] + ' ' + Math.round(s[k] / st * 100) + ' %</span>').join('') + '</div></div>';
    const w = v.m.way, wt = Object.values(w).reduce((a, b) => a + b, 0) || 1;
    html += '<p class="hint">Wegtyp: ' + Object.keys(w).sort((a, b) => w[b] - w[a]).map((k) => k + ' ' + Math.round(w[k] / wt * 100) + ' %').join(' · ') + '</p>';
  }
  const notes = state.notes.slice(1);
  if (Math.abs(v.err || 0) > pr.tol) notes.push('Weicht ' + Math.round((v.err || 0) * 100) + ' % von der Wunschlänge ab.');
  if (!v.m.ok) notes.push('Der Server hat keine Wegdetails geliefert – Kennzahlen unvollständig.');
  if (notes.length) html += '<ul class="notes">' + notes.map((n) => '<li>' + esc(n) + '</li>').join('') + '</ul>';
  $('detail').innerHTML = html;
}

// ---------- GPX ----------
function gpxFor(v) {
  const name = 'Laufroute ' + nf1.format(v.dist / 1000) + ' km – ' + (PRESETS[v.preset || settings.preset] || PRESETS.dauer).name;
  const pts = v.coords.map((c) => '<trkpt lat="' + c[1].toFixed(6) + '" lon="' + c[0].toFixed(6) + '">' + (isFinite(c[2]) ? '<ele>' + Number(c[2]).toFixed(1) + '</ele>' : '') + '</trkpt>').join('\n');
  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="Laufrouten Hamburg ' + APP_VERSION + '" xmlns="http://www.topografix.com/GPX/1/1">\n' +
    '<metadata><name>' + esc(name) + '</name><time>' + new Date().toISOString() + '</time></metadata>\n' +
    '<trk><name>' + esc(name) + '</name><type>running</type><trkseg>\n' + pts + '\n</trkseg></trk>\n</gpx>\n';
  const fname = 'laufroute-' + (v.dist / 1000).toFixed(1).replace('.', '-') + 'km-' + new Date().toISOString().slice(0, 10) + '.gpx';
  return { xml, fname, name };
}
function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement('a'); a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}
function gpxFile(v) { const g = gpxFor(v); return new File([g.xml], g.fname, { type: 'application/gpx+xml' }); }
function canShareFile() { try { const v = state.variants[state.sel]; return !!(v && navigator.canShare && navigator.canShare({ files: [gpxFile(v)] })); } catch (e) { return false; } }

// ---------- Verlauf ----------
function slimVariant(v) {
  return { name: v.name, dist: v.dist, cost: v.cost, up: v.up, turns: v.turns, err: v.err, q: v.q, score: v.score, strides: v.strides || null,
    coords: v.coords.map((c) => [Math.round(c[0] * 1e5) / 1e5, Math.round(c[1] * 1e5) / 1e5, isFinite(c[2]) ? Math.round(c[2]) : null]), m: v.m };
}
async function saveHistory() {
  const v = state.variants[state.sel];
  if (!v) return;
  if (!state.histId || state.histKey !== state.lastKey) { state.histId = uid(); state.histKey = state.lastKey; }
  const e = { id: state.histId, ts: Date.now(), preset: settings.preset, loop: isLoopMode() || !state.end, L: state.lastL, from: state.start, to: isLoopMode() ? null : state.end, variant: slimVariant(v) };
  await Store.put('hist', e);
  const all = (await Store.all('hist')).sort((a, b) => b.ts - a.ts);
  for (const old of all.slice(HISTORY_MAX)) await Store.del('hist', old.id);
  if (!$('histPanel').hidden) renderHistory();
  askPersist();
}
async function renderHistory() {
  const all = (await Store.all('hist')).sort((a, b) => b.ts - a.ts);
  $('histList').innerHTML = all.length ? all.map((e) => {
    const pr = PRESETS[e.preset] || PRESETS.dauer;
    const where = (e.from && e.from.label ? e.from.label : 'Start') + (e.to ? ' → ' + (e.to.label || 'Ziel') : ' (Runde)');
    return '<div class="item"><button type="button" data-hload="' + e.id + '">' + esc(pr.name) + ' · ' + km1(e.variant.dist) +
      '<small>' + fmtDate(e.ts) + ' · ' + esc(where) + '</small></button><button type="button" class="ghost danger" data-hdel="' + e.id + '" aria-label="Löschen">Löschen</button></div>';
  }).join('') : '<p class="hint">Noch keine Routen. Jede Berechnung landet automatisch hier (die letzten ' + HISTORY_MAX + ').</p>';
  $('histList').querySelectorAll('[data-hload]').forEach((b) => b.addEventListener('click', () => loadHistory(b.dataset.hload, all)));
  $('histList').querySelectorAll('[data-hdel]').forEach((b) => b.addEventListener('click', async () => { await Store.del('hist', b.dataset.hdel); renderHistory(); }));
}
function loadHistory(id, all) {
  const e = all.find((x) => x.id === id);
  if (!e) return;
  setPreset(e.preset, true);
  setMode(e.to ? 'ab' : 'rt');
  setPoint('start', e.from, false);
  if (e.to) setPoint('end', e.to, false);
  if (!PRESETS[e.preset].lap) { setLenMode('km'); $('kmInput').value = nf1.format(e.L / 1000).replace(',', '.'); } else { $('lapInput').value = Math.round(e.L); }
  updateCalc();
  const v = Object.assign({}, e.variant, { coords: e.variant.coords.map((c) => [c[0], c[1], c[2] == null ? NaN : c[2]]), colorVar: '--v1', preset: e.preset });
  state.variants = [v]; state.sel = 0; state.notes = []; state.fromHistory = true; state.lastL = e.L; state.lastKey = null;
  $('histPanel').hidden = true; $('histBtn').setAttribute('aria-pressed', 'false');
  renderResults(true);
  status('Route vom ' + fmtDate(e.ts) + ' geladen. „Route berechnen“ rechnet sie neu.', 'ok');
  $('resCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ---------- Favoriten ----------
async function loadFavs() { state.favs = (await Store.all('fav')).sort((a, b) => a.name.localeCompare(b.name, 'de')); renderFavs(); }
function renderFavs() {
  document.querySelectorAll('[data-favs]').forEach((box) => {
    const which = box.dataset.favs;
    box.innerHTML = state.favs.map((f) => '<button type="button" data-favpick="' + f.id + '">' + esc(f.name) + '</button>').join('');
    box.querySelectorAll('[data-favpick]').forEach((b) => b.addEventListener('click', () => {
      const f = state.favs.find((x) => x.id === b.dataset.favpick);
      if (f) { setPoint(which, { lat: f.lat, lon: f.lon, label: f.name }); status(''); }
    }));
  });
  $('favList').innerHTML = state.favs.length ? state.favs.map((f) => '<div class="item"><span>' + esc(f.name) + '<small>' + fmtLL(f) + '</small></span><button type="button" class="ghost danger" data-favdel="' + f.id + '">Löschen</button></div>').join('')
    : '<p class="hint">Noch keine Favoriten. Punkt setzen, dann „Merken“.</p>';
  $('favList').querySelectorAll('[data-favdel]').forEach((b) => b.addEventListener('click', async () => { await Store.del('fav', b.dataset.favdel); loadFavs(); }));
}

// ---------- Export / Import ----------
async function exportData() {
  const data = { app: 'laufrouten-hamburg', format: 1, exported: new Date().toISOString(), settings, favorites: await Store.all('fav'), history: await Store.all('hist') };
  download('laufrouten-backup-' + new Date().toISOString().slice(0, 10) + '.json', JSON.stringify(data), 'application/json');
  status('Backup gespeichert (' + data.favorites.length + ' Favoriten, ' + data.history.length + ' Routen).', 'ok');
}
async function importData(file) {
  let data;
  try { data = JSON.parse(await file.text()); } catch (e) { status('Datei ist kein gültiges Backup.', 'err'); return; }
  if (!data || data.app !== 'laufrouten-hamburg') { status('Datei ist kein Laufrouten-Backup.', 'err'); return; }
  let nf = 0, nh = 0;
  for (const f of data.favorites || []) if (f && f.id && typeof f.lat === 'number' && typeof f.lon === 'number') { await Store.put('fav', { id: String(f.id), name: String(f.name || 'Favorit').slice(0, 60), lat: f.lat, lon: f.lon }); nf++; }
  for (const h of data.history || []) if (h && h.id && h.variant && Array.isArray(h.variant.coords)) { await Store.put('hist', h); nh++; }
  if (data.settings && typeof data.settings === 'object') {
    ['basePace', 'server', 'tiles', 'theme'].forEach((k) => { if (data.settings[k] != null) settings[k] = data.settings[k]; });
    await saveSettings(); applySettingsUI();
  }
  await loadFavs(); renderHistory();
  status('Importiert: ' + nf + ' Favoriten, ' + nh + ' Routen.', 'ok');
}

// ---------- Einstellungen / UI-Zustand ----------
async function saveSettings() { await Store.set('settings', Object.assign({}, settings)); }
function applyTheme() {
  if (settings.theme === 'auto') document.documentElement.removeAttribute('data-theme');
  else document.documentElement.setAttribute('data-theme', settings.theme);
  redraw();
}
function applySettingsUI() {
  $('basePace').value = fmtPace(settings.basePace);
  $('serverInput').value = settings.server;
  $('tileSel').value = TILES[settings.tiles] ? settings.tiles : 'osm';
  $('themeSel').value = settings.theme;
  $('stridesChk').checked = !!settings.strides;
  setTiles(settings.tiles); applyTheme();
  renderPresets(); setPreset(settings.preset, true); setMode(settings.mode); setLenMode(settings.lenMode);
}
function renderPresets() {
  $('presets').innerHTML = Object.keys(PRESETS).map((k) => {
    const p = PRESETS[k];
    return '<button type="button" data-preset="' + k + '" aria-pressed="' + (k === settings.preset) + '">' + esc(p.name) + '<small>' + fmtPace(settings.basePace + p.paceOff) + ' · ' + (p.lap ? 'Runde' : p.km + ' km') + '</small></button>';
  }).join('');
  $('presets').querySelectorAll('[data-preset]').forEach((b) => b.addEventListener('click', () => { setPreset(b.dataset.preset, false); saveSettings(); }));
}
function setPreset(k, keepInputs) {
  if (!PRESETS[k]) k = 'dauer';
  const changed = k !== settings.preset;
  settings.preset = k;
  const p = PRESETS[k];
  document.querySelectorAll('[data-preset]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.preset === k)));
  $('presetHint').textContent = p.hint + ' Tempo ' + fmtPace(settings.basePace + p.paceOff) + ' min/km.';
  $('lenBlock').hidden = !!p.lap; $('lapBlock').hidden = !p.lap;
  $('modeAB').disabled = !!p.lap;
  $('stridesChk').closest('label').hidden = !!p.lap;
  if (!keepInputs || changed) {
    $('paceInput').value = fmtPace(settings.basePace + p.paceOff);
    $('lapPace').value = fmtPace(settings.basePace + p.paceOff);
    if (!p.lap) { $('kmInput').value = p.km; $('durInput').value = Math.round(p.km * (settings.basePace + p.paceOff) / 60 / 5) * 5; }
  }
  applyModeUI();
  updateCalc();
}
function setMode(m) { settings.mode = m === 'rt' ? 'rt' : 'ab'; applyModeUI(); }
function applyModeUI() {
  const loop = isLoopMode();
  $('modeAB').setAttribute('aria-pressed', String(!loop));
  $('modeRT').setAttribute('aria-pressed', String(loop));
  $('endBlock').hidden = loop;
  placeMarker('end');
}
function setLenMode(m) {
  settings.lenMode = m === 'dur' ? 'dur' : 'km';
  $('lenKm').setAttribute('aria-pressed', String(settings.lenMode === 'km'));
  $('lenDur').setAttribute('aria-pressed', String(settings.lenMode === 'dur'));
  $('kmWrap').hidden = settings.lenMode !== 'km'; $('durWrap').hidden = settings.lenMode !== 'dur';
  updateCalc();
}
async function refreshStoreInfo() {
  let persisted = null;
  try { if (navigator.storage && navigator.storage.persisted) persisted = await navigator.storage.persisted(); } catch (e) { /* egal */ }
  $('storeInfo').textContent = Store.isMem()
    ? 'Achtung: Dieser Browser erlaubt keinen dauerhaften Speicher (z. B. privates Fenster). Daten gehen beim Schließen verloren – Backup exportieren.'
    : 'Favoriten, Verlauf und Einstellungen bleiben nur auf diesem Gerät.' + (persisted ? ' Dauerhafter Speicher ist aktiv.' : ' Als App installiert bleiben sie am zuverlässigsten erhalten.');
  $('versionInfo').textContent = 'Version ' + APP_VERSION + ' · Anfragen in dieser Sitzung: ' + net.calls;
}

// ---------- GPS ----------
function locate(which) {
  if (!navigator.geolocation) { status('GPS ist in diesem Browser nicht verfügbar.', 'warn'); return; }
  status('Suche Standort …');
  navigator.geolocation.getCurrentPosition((pos) => {
    const p = { lat: pos.coords.latitude, lon: pos.coords.longitude };
    setPoint(which, { lat: p.lat, lon: p.lon, label: 'GPS ±' + Math.round(pos.coords.accuracy) + ' m' });
    status('Standort gesetzt.', 'ok');
  }, (err) => status('Standort nicht verfügbar (' + (err.message || err.code) + '). Favorit, Adresse oder Karte nutzen.', 'warn'),
  { enableHighAccuracy: true, timeout: 15000, maximumAge: 30000 });
}

// ---------- Ereignisse ----------
document.querySelectorAll('form[data-search]').forEach((form) => form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const which = form.dataset.search, text = $(which + 'Input').value.trim();
  if (text.length < 3) { status('Mindestens 3 Zeichen eingeben.', 'warn'); return; }
  status('Suche Adresse …');
  try {
    const hits = await geocode(text), box = $(which + 'Results');
    if (!hits.length) { box.innerHTML = ''; status('Nichts gefunden. Anders schreiben oder auf die Karte tippen.', 'warn'); return; }
    box.innerHTML = hits.map((h, i) => '<button type="button" data-i="' + i + '">' + esc(h.label) + '</button>').join('');
    box.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => { setPoint(which, hits[Number(b.dataset.i)]); status(''); }));
    status(hits.length + ' Treffer – einen antippen.');
  } catch (err) { status(err.message, 'err'); }
}));
document.querySelectorAll('[data-gps]').forEach((b) => b.addEventListener('click', () => locate(b.dataset.gps)));
document.querySelectorAll('[data-pick]').forEach((b) => b.addEventListener('click', () => setPick(state.pick === b.dataset.pick ? null : b.dataset.pick)));
document.querySelectorAll('[data-fav]').forEach((b) => b.addEventListener('click', () => {
  const which = b.dataset.fav;
  if (!state[which]) { status('Erst einen Punkt setzen, dann merken.', 'warn'); return; }
  const f = document.querySelector('[data-favform="' + which + '"]');
  f.hidden = !f.hidden;
  if (!f.hidden) { const inp = $(which + 'FavName'); inp.value = /^(Karte|GPS)/.test(state[which].label) ? '' : state[which].label.split(',')[0]; inp.focus(); }
}));
document.querySelectorAll('form[data-favform]').forEach((form) => form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const which = form.dataset.favform, p = state[which], name = $(which + 'FavName').value.trim().slice(0, 60);
  if (!p || !name) { status('Namen eingeben.', 'warn'); return; }
  const existing = state.favs.find((x) => x.name.toLowerCase() === name.toLowerCase());
  await Store.put('fav', { id: existing ? existing.id : uid(), name, lat: p.lat, lon: p.lon });
  form.hidden = true;
  state[which].label = name; $(which + 'Pt').textContent = name;
  await loadFavs(); askPersist();
  status('„' + name + '“ gemerkt – nur auf diesem Gerät.', 'ok');
}));
$('swapBtn').addEventListener('click', () => { const s = state.start; setPoint('start', state.end, false); setPoint('end', s, false); });
$('modeAB').addEventListener('click', () => { setMode('ab'); saveSettings(); });
$('modeRT').addEventListener('click', () => { setMode('rt'); saveSettings(); });
$('lenKm').addEventListener('click', () => { setLenMode('km'); saveSettings(); });
$('lenDur').addEventListener('click', () => { setLenMode('dur'); saveSettings(); });
['kmInput', 'durInput', 'paceInput', 'lapInput', 'repsInput', 'lapPace'].forEach((id) => $(id).addEventListener('input', () => { updateCalc(); if (state.variants.length && /pace|Pace|reps/.test(id)) renderResults(false); }));
$('stridesChk').addEventListener('change', () => { settings.strides = $('stridesChk').checked; saveSettings(); });
$('goBtn').addEventListener('click', () => compute(false));
$('againBtn').addEventListener('click', () => compute(true));
$('gpxBtn').addEventListener('click', () => {
  const v = state.variants[state.sel]; if (!v) return;
  const g = gpxFor(v); download(g.fname, g.xml, 'application/gpx+xml');
  status('GPX gespeichert: ' + g.fname + '. In OsmAnd/Organic Maps importieren.', 'ok');
});
$('shareBtn').addEventListener('click', async () => {
  const v = state.variants[state.sel]; if (!v) return;
  try { await navigator.share({ files: [gpxFile(v)], title: gpxFor(v).name }); }
  catch (e) { if (e && e.name !== 'AbortError') status('Teilen nicht möglich – „GPX speichern“ nutzen.', 'warn'); }
});
function togglePanel(id) {
  const other = id === 'histPanel' ? 'setPanel' : 'histPanel';
  $(other).hidden = true;
  $(id).hidden = !$(id).hidden;
  $('histBtn').setAttribute('aria-pressed', String(!$('histPanel').hidden));
  $('setBtn').setAttribute('aria-pressed', String(!$('setPanel').hidden));
  if (!$(id).hidden) { if (id === 'histPanel') renderHistory(); else { renderFavs(); refreshStoreInfo(); } $(id).scrollIntoView({ behavior: 'smooth', block: 'start' }); }
}
$('histBtn').addEventListener('click', () => togglePanel('histPanel'));
$('setBtn').addEventListener('click', () => togglePanel('setPanel'));
document.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', () => togglePanel(b.dataset.close)));
let clearArmed = false;
$('histClear').addEventListener('click', async () => {
  if (!clearArmed) { clearArmed = true; $('histClear').textContent = 'Wirklich alles löschen?'; setTimeout(() => { clearArmed = false; $('histClear').textContent = 'Verlauf leeren'; }, 4000); return; }
  clearArmed = false; $('histClear').textContent = 'Verlauf leeren';
  await Store.clear('hist'); renderHistory(); status('Verlauf gelöscht.', 'ok');
});
$('basePace').addEventListener('change', () => {
  const s = parsePace($('basePace').value);
  if (!s) { status('Tempo als m:ss angeben, z. B. 6:45.', 'warn'); $('basePace').value = fmtPace(settings.basePace); return; }
  settings.basePace = s; saveSettings(); renderPresets(); setPreset(settings.preset, false);
});
$('serverInput').addEventListener('change', () => {
  const v = $('serverInput').value.trim();
  if (!/^https?:\/\/[^\s]+$/.test(v)) { status('Server-Adresse muss mit https:// beginnen.', 'warn'); $('serverInput').value = settings.server; return; }
  settings.server = v.replace(/\/+$/, ''); saveSettings(); status('Routing-Server: ' + settings.server, 'ok');
});
$('tileSel').addEventListener('change', () => { settings.tiles = $('tileSel').value; setTiles(settings.tiles); saveSettings(); });
$('themeSel').addEventListener('change', () => { settings.theme = $('themeSel').value; applyTheme(); saveSettings(); });
$('exportBtn').addEventListener('click', exportData);
$('importBtn').addEventListener('click', () => $('importFile').click());
$('importFile').addEventListener('change', () => { const f = $('importFile').files[0]; if (f) importData(f); $('importFile').value = ''; });
if (window.matchMedia) { const mq = window.matchMedia('(prefers-color-scheme: dark)'); if (mq.addEventListener) mq.addEventListener('change', redraw); }

// ---------- PWA ----------
let installEvt = null;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); installEvt = e; $('installBtn').hidden = false; });
$('installBtn').addEventListener('click', async () => { if (!installEvt) return; installEvt.prompt(); try { await installEvt.userChoice; } catch (e) { /* egal */ } installEvt = null; $('installBtn').hidden = true; });
window.addEventListener('appinstalled', () => { $('installBtn').hidden = true; askPersist(); });
if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
  window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => { /* ohne Offline-Modus weiter */ }); });
}

// ---------- Start ----------
(async function init() {
  try {
    const s = await Store.get('settings');
    if (s && typeof s === 'object') Object.keys(settings).forEach((k) => { if (s[k] != null) settings[k] = s[k]; });
  } catch (e) { /* Standardwerte */ }
  if (!PRESETS[settings.preset]) settings.preset = 'dauer';
  applySettingsUI();
  if (settings.lastStart) setPoint('start', settings.lastStart, false);
  if (settings.lastEnd) setPoint('end', settings.lastEnd, false);
  if (settings.lastStart) map.setView([settings.lastStart.lat, settings.lastStart.lon], 13);
  booted = true;
  await loadFavs();
  refreshStoreInfo();
  status(state.favs.length ? 'Start und Ziel antippen oder suchen.' : 'Start setzen: Adresse, GPS oder „Auf Karte“. Mit „Merken“ speicherst du Orte wie Zuhause oder Arbeit.');
})();

// Für Tests im Browser erreichbar (keine Wirkung im Normalbetrieb)
window.__laufrouten = { state, settings, PRESETS, metrics, findStrides, loopFactor, version: APP_VERSION };
})();
