/* =========================================================
   Carte de France – Widget Grist
   Tables attendues :
     Departements  : code_dept, nom_dept, code_region, nom_region, visible
     Categories    : nom, couleur, couleur_cumul, selectionnee
     Dept_Categories : dept (ref Departements), categorie (ref Categories), valeur
   ========================================================= */

'use strict';

// ── Couleurs nommées ───────────────────────────────────────
const NAMED_COLORS = {
  bleu:    '#2980b9',
  rouge:   '#e74c3c',
  vert:    '#27ae60',
  jaune:   '#f1c40f',
  orange:  '#e67e22',
  violet:  '#8e44ad',
  rose:    '#e91e8c',
  marron:  '#795548',
  gris:    '#7f8c8d',
  noir:    '#2c3e50',
  blanc:   '#ecf0f1',
  cyan:    '#00bcd4',
};

function resolveColor(raw) {
  if (!raw) return null;
  const key = String(raw).trim().toLowerCase();
  if (NAMED_COLORS[key]) return NAMED_COLORS[key];
  if (/^#[0-9a-f]{3,8}$/i.test(raw)) return raw;
  return null;
}

// ── Constantes géographiques ───────────────────────────────
const METRO_BOUNDS = { center: [46.5, 2.5], zoom: 6 };

const DOMTOM_CONFIG = {
  '971': { name: 'Guadeloupe',  center: [16.25, -61.55], zoom: 9 },
  '972': { name: 'Martinique',  center: [14.65, -61.00], zoom: 10 },
  '973': { name: 'Guyane',      center: [3.9,  -53.0],   zoom: 7 },
  '974': { name: 'La Réunion',  center: [-21.1, 55.55],  zoom: 10 },
  '976': { name: 'Mayotte',     center: [-12.83, 45.15], zoom: 11 },
};

const DOMTOM_CODES = Object.keys(DOMTOM_CONFIG);

// ── État global ────────────────────────────────────────────
const state = {
  allFeatures: [],      // GeoJSON features, keyed by code_dept
  deptData: {},         // { code_dept: {visible, nom, code_region, nom_region} }
  categories: {},       // { id: {nom, couleur, couleur_cumul, selectionnee} }
  deptCats: [],         // [{dept_code, cat_id, valeur}]
  mode: 'categorie',
  uniqueColor: '#e74c3c',
  cumulColor: '#f39c12',
  grayedOpacity: 0.30,
  choroColumn: 'valeur',
  choroLow: '#ffffcc',
  choroHigh: '#006837',
  savedView: null,      // {center, zoom} persisted in grist options
};

// ── Maps ───────────────────────────────────────────────────
let mainMap = null;
const miniMaps = {};
let geoLayer = null;
const miniLayers = {};

// ── Init Leaflet ───────────────────────────────────────────
function initMaps() {
  mainMap = L.map('map-main', {
    zoomControl: true,
    attributionControl: false,
  }).setView(METRO_BOUNDS.center, METRO_BOUNDS.zoom);

  mainMap.on('moveend zoomend', () => {
    // live-save view state
  });

  for (const [code, cfg] of Object.entries(DOMTOM_CONFIG)) {
    const m = L.map(`map-${code}`, {
      zoomControl: false,
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      attributionControl: false,
    }).setView(cfg.center, cfg.zoom);
    miniMaps[code] = m;
  }
}

// ── Chargement GeoJSON ─────────────────────────────────────
async function loadGeoJSON() {
  // Source officielle API Géo du gouvernement français (tous les départements)
  const url = 'https://geo.api.gouv.fr/departements?fields=nom,code,codeRegion&format=geojson&geometry=contour';
  const res = await fetch(url);
  if (!res.ok) throw new Error('Impossible de charger le GeoJSON des départements');
  return res.json();
}

// ── Style d'un département ─────────────────────────────────
function getStyle(feature) {
  const code = feature.properties.code;
  const dept = state.deptData[code];
  const visible = dept ? dept.visible : true;
  const opacity = visible ? 1 : state.grayedOpacity;

  const fillColor = computeColor(code);

  return {
    color: '#555',
    weight: 0.8,
    fillColor: fillColor || '#c8d6e5',
    fillOpacity: fillColor ? opacity : opacity * 0.5,
    opacity: 1,
  };
}

function computeColor(code) {
  if (state.mode === 'unique') {
    // Tous les depts visibles et sélectionnés → une seule couleur
    const dept = state.deptData[code];
    if (dept && dept.visible) return state.uniqueColor;
    return null;
  }

  if (state.mode === 'choropleth') {
    return choroColor(code);
  }

  // mode catégorie
  const activeCats = Object.values(state.categories).filter(c => c.selectionnee);
  if (!activeCats.length) return null;

  const matchedCats = activeCats.filter(cat => {
    return state.deptCats.some(dc => dc.dept_code === code && dc.cat_id === cat._id);
  });

  if (!matchedCats.length) return null;
  if (matchedCats.length === 1) return resolveColor(matchedCats[0].couleur) || NAMED_COLORS.bleu;

  // Plusieurs catégories → couleur cumul configurable
  // Priorité : couleur_cumul de la catégorie la plus récemment sélectionnée
  // (ici on utilise la couleur cumul du widget ou celle définie dans Categories)
  const lastCat = matchedCats[matchedCats.length - 1];
  if (lastCat.couleur_cumul && resolveColor(lastCat.couleur_cumul)) {
    return resolveColor(lastCat.couleur_cumul);
  }
  return state.cumulColor;
}

function choroColor(code) {
  const entries = state.deptCats.filter(dc => dc.dept_code === code);
  if (!entries.length) return null;
  const vals = entries.map(e => e.valeur).filter(v => typeof v === 'number' && !isNaN(v));
  if (!vals.length) return null;
  const val = vals[0];

  const allVals = state.deptCats
    .map(e => e.valeur)
    .filter(v => typeof v === 'number' && !isNaN(v));
  if (!allVals.length) return null;
  const min = Math.min(...allVals);
  const max = Math.max(...allVals);
  if (min === max) return state.choroHigh;

  const scale = chroma.scale([state.choroLow, state.choroHigh]).mode('lab');
  return scale((val - min) / (max - min)).hex();
}

// ── Rendu de la carte ──────────────────────────────────────
function renderMap(geojson) {
  if (geoLayer) {
    mainMap.removeLayer(geoLayer);
    geoLayer = null;
  }
  for (const code of DOMTOM_CODES) {
    if (miniLayers[code]) {
      miniMaps[code].removeLayer(miniLayers[code]);
      delete miniLayers[code];
    }
  }

  // Séparer métropole et DOM-TOM
  const metro = { type: 'FeatureCollection', features: [] };
  const domtom = {};

  for (const f of geojson.features) {
    const code = f.properties.code;
    if (DOMTOM_CODES.includes(code)) {
      domtom[code] = { type: 'FeatureCollection', features: [f] };
    } else {
      metro.features.push(f);
    }
  }

  // Garder référence des features
  state.allFeatures = geojson.features;

  function featureStyle(feature) { return getStyle(feature); }

  function onEachFeature(feature, layer) {
    const code = feature.properties.code;
    const nom = feature.properties.nom || code;
    const dept = state.deptData[code];

    layer.on({
      mouseover(e) {
        const l = e.target;
        l.setStyle({ weight: 2, color: '#222' });
        l.bringToFront();
        updateStatus(nom, code, dept);
      },
      mouseout(e) {
        geoLayer && geoLayer.resetStyle(e.target);
      },
      click() {
        // Zoom sur le département
        mainMap.fitBounds(layer.getBounds(), { padding: [20, 20] });
      },
    });

    layer.bindTooltip(`<b>${nom}</b> (${code})`, { sticky: true, opacity: 0.9 });
  }

  geoLayer = L.geoJSON(metro, {
    style: featureStyle,
    onEachFeature,
  }).addTo(mainMap);

  // Mini-maps DOM-TOM
  for (const [code, fc] of Object.entries(domtom)) {
    if (!miniMaps[code]) continue;
    const layer = L.geoJSON(fc, {
      style: featureStyle,
      onEachFeature: (f, l) => {
        l.bindTooltip(`<b>${f.properties.nom}</b> (${code})`, { sticky: true });
      },
    }).addTo(miniMaps[code]);
    miniLayers[code] = layer;
  }
}

// ── Mise à jour des styles sans recréer les layers ────────
function refreshStyles() {
  if (!geoLayer) return;
  geoLayer.eachLayer(layer => {
    layer.setStyle(getStyle(layer.feature));
  });
  for (const [code, layer] of Object.entries(miniLayers)) {
    layer.eachLayer(l => l.setStyle(getStyle(l.feature)));
  }
  renderLegend();
  renderChoroLegend();
}

// ── Légende catégories ─────────────────────────────────────
function renderLegend() {
  const el = document.getElementById('legend');
  const items = document.getElementById('legend-items');

  if (state.mode !== 'categorie') {
    el.classList.remove('visible');
    return;
  }

  const active = Object.values(state.categories).filter(c => c.selectionnee);
  if (!active.length) {
    el.classList.remove('visible');
    return;
  }

  items.innerHTML = '';
  for (const cat of active) {
    const color = resolveColor(cat.couleur) || NAMED_COLORS.bleu;
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.innerHTML = `
      <div class="legend-swatch" style="background:${color}"></div>
      <span>${cat.nom}</span>
    `;
    items.appendChild(div);
  }

  // Cumul entry si plusieurs catégories actives
  if (active.length > 1) {
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.innerHTML = `
      <div class="legend-swatch" style="background:${state.cumulColor}; border-style:dashed"></div>
      <span><i>Cumul</i></span>
    `;
    items.appendChild(div);
  }

  el.classList.add('visible');
}

// ── Légende choroplèthe ────────────────────────────────────
function renderChoroLegend() {
  const el = document.getElementById('choropleth-legend');
  if (state.mode !== 'choropleth') {
    el.classList.remove('visible');
    return;
  }

  const allVals = state.deptCats
    .map(e => e.valeur)
    .filter(v => typeof v === 'number' && !isNaN(v));

  if (!allVals.length) { el.classList.remove('visible'); return; }

  const min = Math.min(...allVals);
  const max = Math.max(...allVals);

  const bar = document.getElementById('gradient-bar');
  bar.style.background = `linear-gradient(to right, ${state.choroLow}, ${state.choroHigh})`;

  document.getElementById('choro-min-label').textContent = min.toLocaleString('fr-FR');
  document.getElementById('choro-max-label').textContent = max.toLocaleString('fr-FR');
  document.getElementById('choro-legend-title').textContent = state.choroColumn;

  el.classList.add('visible');
}

// ── Status bar ─────────────────────────────────────────────
function updateStatus(nom, code, dept) {
  const vis = dept ? (dept.visible ? '' : ' · grisé') : '';
  document.getElementById('status').textContent = `${nom} (${code})${vis}`;
}

// ── Toolbar bindings ───────────────────────────────────────
function initToolbar() {
  const modeSelect = document.getElementById('mode-select');
  modeSelect.addEventListener('change', () => {
    state.mode = modeSelect.value;
    updateToolbarVisibility();
    refreshStyles();
  });

  document.getElementById('unique-color').addEventListener('input', e => {
    state.uniqueColor = e.target.value;
    refreshStyles();
  });

  document.getElementById('cumul-color').addEventListener('input', e => {
    state.cumulColor = e.target.value;
    refreshStyles();
  });

  document.getElementById('dept-opacity').addEventListener('input', e => {
    state.grayedOpacity = Number(e.target.value) / 100;
    refreshStyles();
  });

  document.getElementById('choro-low').addEventListener('input', e => {
    state.choroLow = e.target.value;
    refreshStyles();
  });

  document.getElementById('choro-high').addEventListener('input', e => {
    state.choroHigh = e.target.value;
    refreshStyles();
  });

  document.getElementById('choro-col').addEventListener('change', e => {
    state.choroColumn = e.target.value;
    refreshStyles();
  });

  document.getElementById('domtom-check').addEventListener('change', e => {
    const panel = document.getElementById('domtom-panel');
    panel.classList.toggle('hidden', !e.target.checked);
    // Invalider les mini-maps pour qu'elles se redessinent
    setTimeout(() => {
      for (const m of Object.values(miniMaps)) m.invalidateSize();
    }, 50);
  });

  document.getElementById('btn-save-zoom').addEventListener('click', saveView);
  document.getElementById('btn-reset-zoom').addEventListener('click', resetView);
}

function updateToolbarVisibility() {
  const mode = state.mode;
  document.getElementById('unique-color-label').style.display = mode === 'unique' ? '' : 'none';
  document.getElementById('unique-color').style.display     = mode === 'unique' ? '' : 'none';
  document.getElementById('cumul-color-label').style.display = mode === 'categorie' ? '' : 'none';
  document.getElementById('cumul-color').style.display      = mode === 'categorie' ? '' : 'none';

  const choroVis = mode === 'choropleth' ? '' : 'none';
  for (const id of ['choro-col-label','choro-col','choro-low-label','choro-low','choro-high-label','choro-high']) {
    document.getElementById(id).style.display = choroVis;
  }
}

// ── Persistence de la vue (zoom/centre) ───────────────────
function saveView() {
  if (!mainMap) return;
  const center = mainMap.getCenter();
  const zoom   = mainMap.getZoom();
  state.savedView = { lat: center.lat, lng: center.lng, zoom };
  grist.setOptions({ savedView: state.savedView }).catch(() => {});
  document.getElementById('status').textContent = `Vue sauvegardée (zoom ${zoom})`;
}

function resetView() {
  if (!mainMap) return;
  if (state.savedView) {
    mainMap.setView([state.savedView.lat, state.savedView.lng], state.savedView.zoom);
  } else {
    mainMap.setView(METRO_BOUNDS.center, METRO_BOUNDS.zoom);
  }
}

// ── Synchronisation Grist ──────────────────────────────────
function applyGristData(deptsRecords, catsRecords, deptCatsRecords) {
  // Departements
  state.deptData = {};
  if (deptsRecords) {
    const n = (deptsRecords.id || []).length;
    for (let i = 0; i < n; i++) {
      const code = String(deptsRecords.code_dept?.[i] || '').trim();
      if (!code) continue;
      state.deptData[code] = {
        visible:      !!deptsRecords.visible?.[i],
        nom:          deptsRecords.nom_dept?.[i] || '',
        code_region:  String(deptsRecords.code_region?.[i] || ''),
        nom_region:   deptsRecords.nom_region?.[i] || '',
      };
    }
  }

  // Categories
  state.categories = {};
  if (catsRecords) {
    const n = (catsRecords.id || []).length;
    for (let i = 0; i < n; i++) {
      const id = catsRecords.id[i];
      state.categories[id] = {
        _id:          id,
        nom:          catsRecords.nom?.[i] || '',
        couleur:      catsRecords.couleur?.[i] || '',
        couleur_cumul: catsRecords.couleur_cumul?.[i] || '',
        selectionnee: !!catsRecords.selectionnee?.[i],
      };
    }
  }

  // Dept_Categories
  state.deptCats = [];
  if (deptCatsRecords) {
    const n = (deptCatsRecords.id || []).length;
    for (let i = 0; i < n; i++) {
      // dept est une Ref → Grist retourne l'ID de la ligne
      // On a besoin du code_dept → on récupère via deptData en inversant
      const deptRowId  = deptCatsRecords.dept?.[i];
      const catId      = deptCatsRecords.categorie?.[i];
      const valeur     = deptCatsRecords.valeur?.[i];

      // Retrouver le code_dept depuis l'ID de ligne Grist
      const deptCode = deptRowId ? getDeptCodeFromRowId(deptRowId, deptsRecords) : null;
      if (!deptCode) continue;

      state.deptCats.push({ dept_code: deptCode, cat_id: catId, valeur });
    }
  }

  // Mettre à jour la liste de colonnes choroplèthe
  updateChoroColumnList();

  refreshStyles();
}

function getDeptCodeFromRowId(rowId, deptsRecords) {
  if (!deptsRecords) return null;
  const idx = (deptsRecords.id || []).indexOf(rowId);
  if (idx === -1) return null;
  return String(deptsRecords.code_dept?.[idx] || '').trim() || null;
}

function updateChoroColumnList() {
  const sel = document.getElementById('choro-col');
  // Colonnes numériques disponibles dans Dept_Categories
  sel.innerHTML = '<option value="valeur">valeur</option>';
}

// ── Grist plugin ───────────────────────────────────────────
let geojsonCache = null;
let deptsCache   = null;
let catsCache    = null;
let deptCatsCache = null;

async function initGrist() {
  grist.ready({
    requiredAccess: 'read table',
    columns: [
      // Grist UI column mapping hints (non-obligatoire mais guide l'utilisateur)
    ],
  });

  // Charger le GeoJSON une seule fois
  try {
    geojsonCache = await loadGeoJSON();
    renderMap(geojsonCache);
  } catch (e) {
    document.getElementById('status').textContent = `Erreur chargement carte: ${e.message}`;
  }

  document.getElementById('loading').classList.add('hidden');

  // Restaurer la vue sauvegardée
  try {
    const opts = await grist.getOptions();
    if (opts?.savedView) {
      state.savedView = opts.savedView;
      mainMap.setView([opts.savedView.lat, opts.savedView.lng], opts.savedView.zoom);
    }
  } catch (_) {}

  // Écouter les changements de données sur les 3 tables
  async function fetchAll() {
    try {
      [deptsCache, catsCache, deptCatsCache] = await Promise.all([
        grist.docApi.fetchTable('Departements'),
        grist.docApi.fetchTable('Categories'),
        grist.docApi.fetchTable('Dept_Categories'),
      ]);
      applyGristData(deptsCache, catsCache, deptCatsCache);
    } catch (e) {
      document.getElementById('status').textContent = `Erreur lecture Grist: ${e.message}`;
    }
  }

  await fetchAll();

  // Réagir au curseur sur la table Categories (Q3-B)
  // Le widget doit être lié à la table Categories dans Grist
  grist.onRecord(async () => {
    // Quand le curseur bouge dans Categories → relire les états selectionnee
    await fetchAll();
  });

  // Réagir aux modifications de table (toutes tables)
  grist.onRecords(async () => {
    await fetchAll();
  });
}

// ── Resize handler ─────────────────────────────────────────
const ro = new ResizeObserver(() => {
  if (mainMap) mainMap.invalidateSize();
  for (const m of Object.values(miniMaps)) m.invalidateSize();
});
ro.observe(document.getElementById('map-wrapper') || document.body);

// ── Bootstrap ──────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initMaps();
  initToolbar();
  updateToolbarVisibility();
  initGrist();

  // Status par défaut
  document.getElementById('status').textContent = 'Prêt';

  // Fix resize après que Leaflet soit monté
  setTimeout(() => {
    if (mainMap) mainMap.invalidateSize();
    for (const m of Object.values(miniMaps)) m.invalidateSize();
  }, 300);
});
