# Migration des widgets Grist vers l'organisation GitHub de l'UMPV

Ce dossier contient le mode d'emploi et le script pour recopier la dernière
version de chaque widget Grist depuis le compte personnel `Bigorneau15652`
vers une organisation GitHub de l'université Paul-Valéry.

---

## 0. À lire en premier : « mode caché » et GitHub Pages

C'est le point le plus important, parce qu'il conditionne tout le reste.

Un widget Grist personnalisé est une **page web chargée dans une iframe** par
le navigateur de chaque utilisateur. Pour que Grist puisse l'afficher, l'URL
de la page doit être **accessible publiquement, sans authentification**. Ce
n'est pas un choix de conception : c'est le navigateur de l'utilisateur qui va
chercher la page, et il n'a aucun moyen de s'authentifier auprès de GitHub.

Il faut donc distinguer deux choses que le mot « caché » mélange :

| | Peut être privé ? | Conséquence |
|---|---|---|
| **Le code source** (le dépôt GitHub) | Oui | Personne ne peut lire ni cloner le code sans être membre de l'organisation. |
| **La page servie** (l'URL du widget) | Non | Si elle n'est pas publiquement joignable, Grist affiche une page blanche. |

Et une contrainte de facturation GitHub s'ajoute :

- **GitHub Free** (compte perso ou organisation gratuite) : GitHub Pages
  n'est disponible **que sur les dépôts publics**. Passer `map` en privé
  **coupe** `…github.io/map/…` et tous vos widgets cessent de s'afficher.
- **GitHub Team / Enterprise** (payant, mais **gratuit pour les
  établissements via GitHub Education**) : Pages fonctionne depuis un dépôt
  **privé** — le code reste fermé, seule la page publiée reste publique.
- **GitHub Enterprise Cloud** uniquement : Pages « privées », visibles
  seulement des membres de l'organisation. Dans ce cas Grist ne pourrait
  plus charger les widgets pour les utilisateurs non connectés à GitHub.

C'est probablement pour cette raison que vos quatre autres dépôts
(`grist-energie-eau-sync`, `eau-umpv-import`, `carte-batiments-eau`,
`pv-umpv-import`) peuvent être privés sans problème : ce sont des outils
d'import/synchronisation, **ils ne servent aucune page à Grist**. Seul `map`
sert des pages.

### Ce que le script fait à la place

Le script applique donc un **« privé partout où c'est possible, discret
partout ailleurs »** :

- les 4 dépôts d'outillage → **privés** ;
- `map` → **public par défaut**, mais rendu discret :
  - `<meta name="robots" content="noindex, nofollow">` injecté dans **chaque
    page HTML** → les widgets ne remontent pas dans Google ;
  - dépôt créé **sans description ni topics** → invisible dans les
    recherches GitHub par sujet ;
  - le catalogue de widgets Grist (`manifest.json`) n'est pas publié → les
    widgets s'ajoutent uniquement en collant leur URL, ils n'apparaissent pas
    dans la liste déroulante publique de Grist.

**Si l'université dispose de GitHub Education / Team**, vous pouvez alors
lancer le script avec `--map-visibility private` et tout devient privé, Pages
compris. C'est la meilleure option : à demander à la DSI avant de migrer, ça
ne coûte rien de vérifier.

> **Cloudflare Pages**, que j'évoquais dans ma question : c'est un hébergeur
> de sites statiques gratuit (concurrent de GitHub Pages). Il permet de garder
> le dépôt privé sur GitHub tout en publiant les pages. Ce n'est **pas
> nécessaire** ici — je le mentionne seulement comme solution de repli si
> l'université refuse un dépôt public et n'a pas GitHub Education.

---

## 1. Créer l'organisation GitHub (à faire par vous, ~5 min)

L'API GitHub ne permet pas de créer une organisation : cette étape est
forcément manuelle.

1. <https://github.com/account/organizations/new> → plan **Free**.
2. **Organization name** : choisissez un nom court et stable, il apparaîtra
   dans toutes les URL des widgets. Suggestions :
   `univ-paul-valery`, `umpv-montpellier3`, `upv-dpi`.
   ⚠️ Ce nom sera **impossible à changer sans casser toutes les URL Grist** —
   choisissez-le avec la personne qui gérera le compte après vous.
3. **Contact email** : une **adresse de service** (ex. `dpi@univ-montp3.fr`),
   **pas** une adresse personnelle — c'est tout l'intérêt de la manœuvre.
4. « This organization belongs to: » → **A business or institution**.
5. Ignorez l'invitation de collaborateurs pour l'instant.

### Réglages de l'organisation, juste après création

Settings de l'organisation :

- **Member privileges** → « Base permissions » : `Read`.
- **Member privileges** → décochez « Members can create public repositories »
  (évite qu'un dépôt sorte en public par inadvertance).
- **Moderation / Repository visibility** : laissez la possibilité de créer des
  dépôts publics aux propriétaires seulement.
- **People** → invitez au moins **un deuxième propriétaire (Owner)** dans le
  service. Une organisation à un seul owner est un point de défaillance
  unique : si vous partez, plus personne ne peut administrer les widgets.

---

## 2. Préparer le poste (~5 min)

Le script a besoin de `git`. Il utilise `gh` (la CLI GitHub) si elle est
disponible, pour créer les dépôts et pousser automatiquement — sinon il
prépare tout localement et vous affiche les commandes à lancer.

```bash
# macOS
brew install git gh
# Debian / Ubuntu
sudo apt install git && sudo apt install gh
# Windows
winget install Git.Git GitHub.cli
```

Puis authentifiez-vous avec le compte qui est **owner de la nouvelle
organisation** :

```bash
gh auth login          # → GitHub.com → HTTPS → login via navigateur
gh auth status         # doit afficher votre compte
```

Vous devez aussi pouvoir cloner les **4 dépôts privés** du compte source. Si
`gh auth login` a été fait avec le compte `Bigorneau15652`, c'est déjà le cas.
Sinon, connectez-vous d'abord avec ce compte pour la copie, puis rebasculez.

---

## 3. Lancer la migration

Récupérez le script :

```bash
git clone https://github.com/Bigorneau15652/map.git
cd map/docs/migration-umpv
```

**Répétition générale** (ne touche à rien sur GitHub, prépare tout dans un
dossier local que vous pouvez inspecter) :

```bash
./migrer-vers-umpv.sh --org VOTRE-ORG --dry-run --workdir ~/migration-umpv
```

Ouvrez `~/migration-umpv/map/` et vérifiez que tout est là. Puis, pour de
vrai :

```bash
./migrer-vers-umpv.sh --org VOTRE-ORG
```

Options utiles :

| Option | Effet |
|---|---|
| `--map-visibility private` | si l'organisation a GitHub Team / Education |
| `--only map` | ne migrer qu'un dépôt (reprise après erreur) |
| `--branch master` | garder `master` comme branche par défaut au lieu de `main` |
| `--no-noindex` | ne pas injecter la balise robots |
| `--keep-workflows` | garder les GitHub Actions héritées |

### Ce que le script fait, dépôt par dépôt

1. clone la **dernière version uniquement**, sans l'historique (votre choix) ;
2. réécrit `bigorneau15652.github.io` → `VOTRE-ORG.github.io`,
   `github.com/Bigorneau15652` → `github.com/VOTRE-ORG`, dans les README,
   `package.json` et pages de démo (les mentions d'auteur sont conservées) ;
3. injecte `<meta name="robots" content="noindex, nofollow">` dans chaque
   page HTML ;
4. déplace `.github/workflows/` vers `.github/workflows-desactives/` — ces
   workflows hérités du dépôt amont (`release.yml` crée une release à chaque
   push, `publish-npm-package.yml` publie sur npm) échoueraient bruyamment
   sur la nouvelle organisation ;
5. crée un **commit initial unique** ;
6. crée le dépôt dans l'organisation avec la bonne visibilité, et pousse.

---

## 4. Activer GitHub Pages sur le nouveau dépôt `map`

1. `https://github.com/VOTRE-ORG/map` → **Settings** → **Pages**.
2. **Source** : `Deploy from a branch` → branche `main` → dossier `/ (root)`.
3. **Save**. Attendez 1 à 2 minutes, puis vérifiez :
   `https://VOTRE-ORG.github.io/map/dashboard-batiment/index.html`

Le fichier `.nojekyll` est déjà présent à la racine du dépôt : il évite que
GitHub ignore les dossiers commençant par `_`. Ne le supprimez pas.

---

## 5. Mettre à jour les URL dans Grist

Dans chaque document Grist : sélectionnez le widget → panneau de droite →
**Custom URL** → remplacez l'URL. Tableau de correspondance :

| Widget | Ancienne URL | Nouvelle URL |
|---|---|---|
| Surfaces OPERAT / EFA | `bigorneau15652.github.io/map/surfaces-operat-efa/` | `VOTRE-ORG.github.io/map/surfaces-operat-efa/` |
| Tableau de bord bâtiment | `bigorneau15652.github.io/map/dashboard-batiment/index.html?v=2` | `VOTRE-ORG.github.io/map/dashboard-batiment/index.html?v=2` |
| Viewer universel | `raw.githack.com/Bigorneau15652/map/master/viewer-universel/index.html` | `VOTRE-ORG.github.io/map/viewer-universel/index.html` |
| Visionneuse PDF | `bigorneau15652.github.io/map/pdf-viewer/index.html` | `VOTRE-ORG.github.io/map/pdf-viewer/index.html` |
| Carte enrichie | `bigorneau15652.github.io/map/map-enhanced/index.html` | `VOTRE-ORG.github.io/map/map-enhanced/index.html` |
| Visionneuse d'images | `bigorneau15652.github.io/map/image-viewer.html` | `VOTRE-ORG.github.io/map/image-viewer.html` |
| Étiquette DPE/GES | `bigorneau15652.github.io/map/etiquette-dpe-ges/index.html` | `VOTRE-ORG.github.io/map/etiquette-dpe-ges/index.html` |
| Carte des bâtiments | `bigorneau15652.github.io/map/carte-batiments/` | `VOTRE-ORG.github.io/map/carte-batiments/` |
| Surfaces OPERAT | `bigorneau15652.github.io/map/operat-surfaces/index.html` | `VOTRE-ORG.github.io/map/operat-surfaces/index.html` |
| Images + commentaires | `bigorneau15652.github.io/map/image-viewer-enhanced/index.html` | `VOTRE-ORG.github.io/map/image-viewer-enhanced/index.html` |

⚠️ **`raw.githack.com` est à abandonner.** C'est un service tiers gratuit,
sans engagement de disponibilité, qui n'a pas sa place dans un usage
universitaire durable : le jour où il tombe ou ferme, le widget disparaît.
L'URL GitHub Pages équivalente (`VOTRE-ORG.github.io/map/viewer-universel/`)
sert exactement le même fichier — c'est celle à utiliser.

**Conservez l'ancien dépôt en ligne quelques semaines** après la bascule, le
temps de vérifier que plus aucun document Grist ne pointe vers les anciennes
URL. Une fois la migration confirmée, vous pourrez archiver
`Bigorneau15652/map` (Settings → Archive this repository) plutôt que le
supprimer.

---

## 6. Le relais CORS (Cloudflare Worker)

Le viewer universel lit les plans hébergés sur UPVDrive via un relais CORS :

```
https://upv-cors.oholweck.workers.dev/?url={url}
```

Ce worker tourne aujourd'hui sur un **compte Cloudflare personnel**. C'est le
maillon qui casserait le premier si ce compte disparaissait — il doit être
redéployé sur un compte de service de l'université.

Le code source et le mode d'emploi (déploiement 100 % navigateur, ~10 min,
compte gratuit sans carte bancaire) sont déjà dans le dépôt :

- [`viewer-universel/cloudflare-worker/worker.js`](../../viewer-universel/cloudflare-worker/worker.js)
- [`viewer-universel/cloudflare-worker/README.md`](../../viewer-universel/cloudflare-worker/README.md)

Marche à suivre :

1. Créer un compte Cloudflare avec une **adresse de service** de l'UPV.
2. Déployer `worker.js` (voir le README ci-dessus). Vérifiez que
   `ALLOWED_HOST` vaut bien `upvdrive.univ-montp3.fr` — le worker n'ira
   chercher que des fichiers de ce domaine, il ne peut pas servir de relais
   ouvert.
3. Dans le widget viewer universel → **⚙ Config** → champ **Proxy CORS** :
   remplacer par `https://VOTRE-WORKER.workers.dev/?url={url}`.
4. Une fois tous les documents Grist basculés, supprimer l'ancien worker
   `upv-cors.oholweck.workers.dev`.

> La meilleure solution reste d'activer les en-têtes CORS directement côté
> Nextcloud (UPVDrive) : le relais devient alors inutile. C'est une demande à
> adresser à la DSI, à faire figurer dans la passation.

---

## 7. Vérifications finales

- [ ] Les 5 dépôts existent dans l'organisation, avec la bonne visibilité.
- [ ] `map` a au moins 2 propriétaires (Owners) sur l'organisation.
- [ ] GitHub Pages est actif et une page de widget s'ouvre dans le navigateur.
- [ ] `view-source:` sur une page de widget montre bien la balise `noindex`.
- [ ] Chaque widget a été rouvert **dans Grist** (pas seulement dans un
      navigateur) et affiche bien les données.
- [ ] Testé aussi dans un **panneau étroit** (~340 px) et avec le **thème
      sombre** du système — deux cas qui ont déjà révélé des bugs
      d'affichage sur ces widgets (voir `CLAUDE.md` à la racine).
- [ ] Le nouveau worker Cloudflare répond et le viewer universel charge un
      plan depuis UPVDrive.
- [ ] Ancien dépôt `Bigorneau15652/map` archivé (pas supprimé).
