'use strict';
// Mock minimal du grist-plugin-api.js pour tester index.html?demo=1 sans
// document Grist réel. Ce widget est en lecture seule (aucune écriture dans
// le document), donc ce mock ne reproduit que ce qui est utilisé :
// ready / onRecord / onNewRecord / onOptions / setOption / mapColumnNames.
//
// Valeurs de démo pilotables par l'URL, ex :
//   index.html?demo=1&cons=180&ges=45
//   index.html?demo=1&empty=1   (pour tester la bannière "colonnes non configurées")
window.grist = (function () {
  var params = new URLSearchParams(location.search);
  var recordListeners = [];
  var optionsListeners = [];
  var currentOptions = {};

  var demoRecord = null;
  if (params.get('empty') !== '1') {
    demoRecord = {
      id: 1,
      Consommation: params.has('cons') ? parseFloat(params.get('cons')) : 271,
      Emissions: params.has('ges') ? parseFloat(params.get('ges')) : 52,
    };
  }

  return {
    ready: function () {
      setTimeout(function () {
        optionsListeners.forEach(function (fn) { fn(currentOptions); });
        recordListeners.forEach(function (fn) { fn(demoRecord || { id: 1 }); });
      }, 0);
    },
    onRecord: function (fn) { recordListeners.push(fn); },
    onNewRecord: function () {},
    onOptions: function (fn) { optionsListeners.push(fn); },
    setOption: function (key, value) {
      currentOptions = Object.assign({}, currentOptions, { [key]: value });
      setTimeout(function () { optionsListeners.forEach(function (fn) { fn(currentOptions); }); }, 0);
      return Promise.resolve();
    },
    getOption: function (key) { return currentOptions[key]; },
    mapColumnNames: function (record) {
      if (!demoRecord) return null;
      return record;
    },
  };
})();
