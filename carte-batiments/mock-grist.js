'use strict';
// Mock minimal du grist-plugin-api.js pour la démo autonome (sans Grist réel).
// Reproduit fetchTable / applyUserActions / setOptions / onOptions / onRecords / ready
// avec un stockage en mémoire, pré-rempli depuis DEMO_SEED (demo-seed.js).
window.grist = (function(){
  const tables = JSON.parse(JSON.stringify(DEMO_SEED));
  let nextId = {};
  for(const name of Object.keys(tables)){
    nextId[name] = 1 + tables[name].reduce((m,r)=>Math.max(m,r.id),0);
  }
  let optionsListeners = [];
  let recordListeners = [];
  let currentOptions = {
    tableBat:'Batiments', colSite:'Site', colBat:'Bâtiment',
    tableCats:'Categories', tableDc:'Batiment_categories',
    colDept:'batiment', colCat:'categorie',
  };

  function toColumnar(rows){
    const keys = new Set(['id']);
    rows.forEach(r=>Object.keys(r).forEach(k=>keys.add(k)));
    const cols = {};
    for(const k of keys) cols[k] = rows.map(r=>r[k]);
    return cols;
  }
  function notifyRecords(){ recordListeners.forEach(fn=>fn()); }

  return {
    ready(){
      setTimeout(()=>{ optionsListeners.forEach(fn=>fn(currentOptions)); notifyRecords(); }, 0);
    },
    onOptions(fn){ optionsListeners.push(fn); },
    onRecords(fn){ recordListeners.push(fn); },
    setOptions(opts){ Object.assign(currentOptions, opts); return Promise.resolve(); },
    docApi: {
      fetchTable(name){
        if(name==='_grist_Tables'){
          return Promise.resolve({tableId: Object.keys(tables)});
        }
        const rows = tables[name];
        if(!rows) return Promise.reject(new Error('Table inconnue : '+name));
        return Promise.resolve(toColumnar(rows));
      },
      applyUserActions(actions){
        for(const act of actions){
          const [type, tableName, rowId, fields] = act;
          const rows = tables[tableName];
          if(!rows) continue;
          if(type==='AddRecord'){
            const id = nextId[tableName]++;
            rows.push(Object.assign({id}, fields));
          }else if(type==='UpdateRecord'){
            const row = rows.find(r=>r.id===rowId);
            if(row) Object.assign(row, fields);
          }else if(type==='RemoveRecord'){
            tables[tableName] = rows.filter(r=>r.id!==rowId);
          }
        }
        notifyRecords();
        return Promise.resolve();
      },
    },
  };
})();
