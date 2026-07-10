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
        const rows = tables[name];
        if (!rows) return Promise.reject(new Error('Table inconnue : ' + name));
        return Promise.resolve(toColumnar(rows));
      },
    },
  };
})();
