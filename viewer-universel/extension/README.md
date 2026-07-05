# Extension « UPV Drive CORS » — pour le Viewer Grist

Petite extension Chromium (compatible **Vivaldi**, **Brave**, Chrome, Edge) qui
permet au widget Viewer de lire les **DXF/plans** stockés sur le drive de
l'université (`upvdrive.univ-montp3.fr`), **sans proxy ni pièce jointe**.

## À quoi ça sert

Un navigateur interdit à une page web (le widget, hébergé ailleurs) de
**télécharger les octets** d'un fichier situé sur un autre domaine (le drive),
sauf si ce domaine renvoie l'en-tête `Access-Control-Allow-Origin` (CORS).
Les partages publics Nextcloud ne l'envoient pas → erreur « Failed to fetch ».

Cette extension **ajoute cet en-tête** aux réponses de `upvdrive.univ-montp3.fr`.
Le widget peut alors lire les plans directement. Tes liens publics restent
inchangés, aucune donnée ne passe par un service tiers.

> ⚠️ Portée volontairement **minimale** : l'extension n'agit QUE sur
> `upvdrive.univ-montp3.fr`, uniquement pour ajouter les en-têtes CORS.
> Elle ne lit rien, n'envoie rien nulle part, n'a pas d'accès aux autres sites.

## Installation (Vivaldi / Brave)

1. **Récupérer le dossier** `extension/` (ces 3 fichiers : `manifest.json`,
   `rules.json`, `README.md`).
   - Le plus simple : télécharger le dépôt en ZIP depuis GitHub
     (bouton **Code ▸ Download ZIP**), puis dézipper. Le dossier est dans
     `map/viewer-universel/extension/`.
2. Ouvrir la page des extensions :
   - **Vivaldi** : barre d'adresse → `vivaldi://extensions`
   - **Brave** : barre d'adresse → `brave://extensions`
3. Activer en haut à droite le **Mode développeur**.
4. Cliquer **Charger l'extension non empaquetée** (« Load unpacked »).
5. Sélectionner le dossier **`extension/`** (celui qui contient `manifest.json`).
6. L'extension apparaît dans la liste, activée. C'est tout.

## Utilisation

1. Dans le widget Viewer, ouvrir **⚙ Config** et **vider le champ « Proxy CORS »**
   (il n'est plus nécessaire — l'extension gère le CORS en direct).
2. Cliquer une ligne dans Grist → le plan DXF s'affiche.

## Si un jour le drive change de domaine

Édite `manifest.json` (clé `host_permissions`) **et** `rules.json`
(`requestDomains`) pour remplacer `upvdrive.univ-montp3.fr` par le nouveau
domaine, puis recharge l'extension.

## Limite

À installer sur **chaque poste / navigateur** qui utilise le viewer. Pour un
déploiement à grande échelle sans installation, la solution définitive reste
l'ajout des en-têtes CORS côté serveur Nextcloud par l'administrateur du drive.
