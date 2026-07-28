'use strict';
// Mock minimal du grist-plugin-api.js pour tester index.html?demo=1 sans
// document Grist réel. Ce widget est en lecture seule (aucune écriture dans
// le document), donc ce mock ne reproduit que ce qui est utilisé :
// ready / onOptions / setOption / docApi.fetchTable, à partir de DEMO_SEED
// (demo-seed.js, chargé avant ce fichier).
window.grist = (function () {
  const tables = JSON.parse(JSON.stringify(window.DEMO_SEED || {}));
  const optionsListeners = [];
  let currentOptions = {};

  function toColumnar(rows) {
    const keys = new Set(['id']);
    rows.forEach((r) => Object.keys(r).forEach((k) => keys.add(k)));
    const cols = {};
    for (const k of keys) cols[k] = rows.map((r) => (k in r ? r[k] : null));
    return cols;
  }

  // _grist_Tables / _grist_Tables_column : métadonnées internes Grist, utilisées
  // par le panneau "⚙️ Colonnes utilisées" pour lister les tables/colonnes
  // réellement présentes dans le document. Reconstruites ici à partir des clés
  // de DEMO_SEED (un "tableId" par table, un id interne arbitraire par table,
  // et une ligne _grist_Tables_column par colonne observée dans ses lignes).
  const tableNames = Object.keys(tables);
  const gristTables = tableNames.map((name, i) => ({ id: i + 1, tableId: name }));
  const gristColumns = [];
  let nextColId = 1;
  for (const t of gristTables) {
    const keys = new Set(['id']);
    (tables[t.tableId] || []).forEach((r) => Object.keys(r).forEach((k) => keys.add(k)));
    for (const colId of keys) gristColumns.push({ id: nextColId++, parentId: t.id, colId });
  }

  function fetchTableRows(name) {
    if (name === '_grist_Tables') return gristTables;
    if (name === '_grist_Tables_column') return gristColumns;
    return tables[name];
  }

  return {
    ready() {
      setTimeout(() => optionsListeners.forEach((fn) => fn(currentOptions)), 0);
    },
    onOptions(fn) {
      optionsListeners.push(fn);
    },
    setOption(key, value) {
      currentOptions = Object.assign({}, currentOptions, { [key]: value });
      setTimeout(() => optionsListeners.forEach((fn) => fn(currentOptions)), 0);
      return Promise.resolve();
    },
    docApi: {
      fetchTable(name) {
        const rows = fetchTableRows(name);
        if (!rows) return Promise.reject(new Error('Table inconnue : ' + name));
        return Promise.resolve(toColumnar(rows));
      },
    },
  };
})();
