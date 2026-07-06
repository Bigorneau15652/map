# Relais CORS — Cloudflare Worker (pour le Viewer Grist)

Petit relais **gratuit** qui permet au widget de lire les DXF/plans du drive UPV,
en contournant proprement le blocage CORS **et** la redirection 303 du lien
`/download` de Nextcloud. Déploiement **100 % dans le navigateur** (aucun
Terminal) — idéal sur un poste verrouillé.

## Déploiement (≈ 10 min, tout au navigateur)

1. Crée un compte gratuit sur **https://dash.cloudflare.com** (email + mot de
   passe, pas de carte bancaire).
2. Menu de gauche → **Workers & Pages** → **Create application** →
   **Create Worker**.
3. Donne un nom (ex. `upv-cors`) → **Deploy**.
4. Clique **Edit code**, efface le code par défaut, colle le contenu de
   [`worker.js`](./worker.js), puis **Deploy**.
5. Copie l'URL du worker affichée, du type :
   `https://upv-cors.TON-SOUS-DOMAINE.workers.dev`

## Brancher au widget

Dans le widget → **⚙ Config** → champ **Proxy CORS** :

```
https://upv-cors.TON-SOUS-DOMAINE.workers.dev/?url={url}
```

**Enregistrer**, recharge Grist, clique une ligne → le plan s'affiche.

## Sécurité

Le worker n'accepte par défaut que les URLs du domaine `upvdrive.univ-montp3.fr`
(constante `ALLOWED_HOST` dans `worker.js`). Adapte-la si le drive change de
domaine, ou mets `''` pour tout autoriser (déconseillé).

## Coût

Plan gratuit Cloudflare : 100 000 requêtes/jour — très largement suffisant.
