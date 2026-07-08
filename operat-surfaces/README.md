# Surfaces OPERAT par EFA

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui fait la
correspondance entre les surfaces des bâtiments de l'UMPV (classées selon la
nomenclature du ministère de l'Éducation nationale) et la classification par
usage exigée par la plateforme ADEME **OPERAT** (décret éco énergie tertiaire),
pour les 5 EFA (entités fonctionnelles assujetties) encore en activité :
Route de Mende, Béziers, Saint-Charles, Saint-Louis, Boutonnet.

## Fonctionnement général

Le widget se connecte au document Grist ouvert et lit directement les tables :

- `BDD_Sites`, `BDD_Batiments`
- Une table "salles" — une ligne par local, avec site/bâtiment/type d'usage/
  statut thermique/surface. **Entièrement configurable**, voir ci-dessous.
- `Table_locaux_types_et_correspondance` (types de locaux UMPV)
- Une table de nomenclature OPERAT (catégorie / sous-catégorie / code
  technique). **Configurable**, voir ci-dessous.

Il n'est **pas** lié à une seule table via le panneau "Select by" : il embarque
ses propres menus déroulants **EFA (site)** puis **Bâtiment**, et recalcule
tout côté navigateur à chaque changement de sélection. Il faut donc lui
accorder l'accès **"Full document access"** lors de l'ajout (Grist le demande
automatiquement), nécessaire aussi bien pour lire ces tables que pour écrire
la table de correspondance décrite ci-dessous.

### Quelle surface est utilisée pour OPERAT : configurez votre propre table

**Important** : par défaut, le widget utilise `BDD_Salles.Surface_utile_m2_`
(la surface utile). **Ce n'est pas la bonne unité pour OPERAT** : la
plateforme et le décret éco énergie tertiaire utilisent la **Surface de
Plancher (SP/SDP)**, pas la surface utile. Dans ce document, la SP n'existe
nativement qu'au niveau de l'étage (`BDD_Etages.Surface_SP_m2_`, calculée par
soustraction), pas par local — d'où l'intérêt de fournir une table dédiée.

Ouvrez **❓ Aide & configuration**, section **"Table des salles (données
sources)"** : choisissez votre propre table (une ligne par local, avec Site,
Bâtiment, Type d'usage, un booléen chauffée, un booléen rafraîchie et **une
colonne de surface en Surface de Plancher**), faites correspondre chaque
colonne, puis cliquez sur **Appliquer**. Le widget recalcule alors tout à
partir de cette table — toute modification future de vos données ou de cette
correspondance de colonnes se répercute automatiquement dans les résultats.
Cette configuration est mémorisée pour le widget (indépendante de la config
de la table OPERAT ci-dessous).

Après un changement de table de salles, pensez à rouvrir **⚙ Paramétrer les
correspondances** pour chaque bâtiment : les types de locaux réellement
utilisés peuvent différer légèrement, et les surfaces affichées (bandeau du
bâtiment, ligne sous chaque type de local) doivent refléter la nouvelle
donnée.

### Si votre table OPERAT ne s'appelle pas `Segmentation_OPERAT`

Le widget essaie ce nom par défaut ; si votre document utilise un autre nom
(ex. `BDD_OPERAT`), les menus déroulants "Catégorie OPERAT" / "Sous-catégorie
OPERAT" de l'écran de paramétrage restent vides et un bandeau d'avertissement
rouge l'indique. Ouvrez **❓ Aide & configuration**, section **"Table de
nomenclature OPERAT"**, et choisissez la bonne table dans la liste déroulante
(elle liste toutes les tables du document). Le choix est mémorisé pour ce
widget. Si des correspondances ont déjà été créées avec des catégories vides
avant la correction, utilisez ensuite **↺ Restaurer les propositions par
défaut** (dans ⚙ Paramétrer les correspondances) pour chaque bâtiment
concerné, afin qu'elles se recalculent avec la bonne table.

### Fenêtre flottante

Le bouton **⛶** (icône seule, en haut à droite de la barre d'outils) ouvre
les résultats actuels dans une vraie fenêtre de navigateur séparée,
déplaçable sur un second écran. Techniquement, un widget custom Grist ne peut pas se recharger
tel quel dans une fenêtre indépendante : la connexion à l'API Grist repose
sur un canal de communication avec la page Grist qui l'héberge, qui
n'existe plus hors de l'iframe. Cette fenêtre est donc un **miroir en lecture
seule** du dernier rendu du widget — pas une seconde instance connectée à
Grist — mais elle se met à jour automatiquement à chaque nouveau calcul
(changement d'EFA, de bâtiment, de la case à cocher…) tant qu'elle reste
ouverte et que l'onglet Grist d'origine reste ouvert. Pas besoin de la
rouvrir à chaque fois.

### Aide & configuration

Le bouton **❓ Aide & configuration** ouvre un panneau avec la configuration
de la table des salles et de la table OPERAT (ci-dessus) et une notice
explicative pas-à-pas (sélection EFA/bâtiment, lecture des résultats, modes
de correspondance, répartition manuelle du prorata avec un exemple chiffré,
case code technique, fenêtre flottante).

### Le paramétrage se fait bâtiment par bâtiment

Le mapping "type de local → OPERAT" n'est **pas global** : chaque bâtiment a
sa propre correspondance, modifiable indépendamment (un même type de local,
ex. "Salle de réunion", peut être classé différemment d'un bâtiment à
l'autre). Le bouton **⚙ Paramétrer les correspondances** exige donc d'avoir
choisi un **bâtiment précis** dans la barre d'outils (pas "Tous les
bâtiments") ; sinon un message vous invite à en choisir un.

### Deux tables créées automatiquement

Au premier chargement, le widget crée dans votre document (si elles
n'existent pas déjà) :

**`Table_correspondance_OPERAT`** — une ligne par couple (bâtiment, type de
local UMPV) réellement présent dans `BDD_Salles` :

- `Batiment` : référence vers `BDD_Batiments`
- `TypeUsage` : référence vers `Table_locaux_types_et_correspondance`
- `Mode` : `Affectation directe` / `Répartition au prorata` / `Hors périmètre`
- `SousCategorieOPERAT` : référence vers `Segmentation_OPERAT` (uniquement
  utilisée en mode "Affectation directe")

**`Table_repartition_prorata_manuelle`** — vide au départ, une ligne par
**exception** que vous ajoutez vous-même (voir section suivante) :

- `Batiment`, `SousCategorieOPERAT` : références
- `StatutThermique` : le statut concerné (ex. "Chauffée (seule)")
- `PourcentageManuel` : le % que vous imposez pour cette cible

Ces deux tables sont **visibles et modifiables comme n'importe quelle table
Grist** dans le grid normal, pas seulement depuis le widget — vos collègues
peuvent les auditer sans ouvrir le widget. `Table_correspondance_OPERAT` est
pré-remplie automatiquement avec une proposition par défaut (voir plus bas) ;
si de nouvelles salles/bâtiments apparaissent plus tard, le widget leur
ajoute une ligne de proposition à l'ouverture suivante, sans jamais toucher
aux lignes déjà présentes (donc sans jamais écraser vos corrections).

Le bouton **⚙ Paramétrer les correspondances**, une fois un bâtiment choisi,
ouvre l'écran d'édition (menus déroulants Mode / Catégorie OPERAT /
Sous-catégorie OPERAT pour chaque type de local présent dans ce bâtiment,
chaque changement enregistré immédiatement) et, en dessous, la section
**Répartition manuelle du prorata**. Le bouton **↺ Restaurer les propositions
par défaut** écrase tout (avec confirmation) pour ce bâtiment uniquement.

**Cette proposition initiale n'est qu'une suggestion et doit être relue et
validée avant tout usage officiel** — voir le détail du raisonnement plus bas.

### Répartition manuelle du prorata (exceptions)

Par défaut, le prorata est **automatique** : une catégorie "à répartir"
(circulation, sanitaire…) se ventile proportionnellement aux m² déjà en
affectation directe, dans le même bâtiment et le même statut thermique — voir
"Trois modes par type de local" ci-dessous pour le détail du calcul.

Pour une **exception**, dans la section "Répartition manuelle du prorata" de
l'écran de paramétrage (un tableau par statut thermique ayant du prorata à
répartir dans ce bâtiment) : indiquez un **% exact** dans la case "% manuel"
en face de la catégorie cible. Ce % s'applique en priorité ; le reste du
prorata continue à se répartir automatiquement entre les autres catégories.
Laissez le % vide (ou cliquez **✕ Retirer**) pour revenir à l'automatique
sur cette ligne.

Le menu **"+ Ajouter une catégorie cible"** propose d'abord les catégories
**déjà affectées en Affectation directe ailleurs dans ce bâtiment** (avec
leur surface et leur statut thermique déjà connus, ex. "Bibliothèque — 297,2
m² (chauffée + rafraîchie) déjà affectés dans ce bâtiment") plutôt que la
nomenclature OPERAT complète (~490 lignes) — utile si un bâtiment a par
exemple 3 catégories déjà affectées, elles apparaissent en premier dans la
liste. L'option **"Autre catégorie OPERAT (liste complète)"** au bas du menu
révèle les 2 menus déroulants classiques (Catégorie puis Sous-catégorie) pour
les cas hors de cette liste.

La colonne **"Base + part du prorata"** affiche, en direct pendant la saisie
(avant même l'enregistrement), la surface finale que recevrait cette
catégorie : base déjà en affectation directe + part du prorata au % indiqué.
Exemple : une circulation de 118 m² à répartir, 33 % vers Bureau (qui a par
ailleurs 0 m² en direct) → la case "% manuel" en face de Bureau à 33 affiche
aussitôt "→ 38,9 m²" dans cette colonne, et le "Total % manuel" de la section
se met aussi à jour en direct.

Si la somme des % manuels d'un même statut dépasse 100 %, ils sont appliqués
tels quels (pas de replafonnement silencieux) et un avertissement rouge vous
le signale — à corriger vous-même, la surface totale de ce statut serait
sinon surestimée.

### Informations de surface pendant le paramétrage

L'écran de paramétrage affiche, en haut, un bandeau **Salles / Surface
totale / Surface chauffée / Surface rafraîchie** du bâtiment sélectionné (les
mêmes chiffres que la vue résultats, sans avoir à y retourner). Sous chaque
type de local de la table de correspondance, une ligne indique sa surface
dans ce bâtiment et sa répartition par statut thermique (ex. "266,35 m²
(266,35 m² chauffée (seule))" ou, si mixte, "45,32 m² (16,43 m² chauffée
(seule), 28,89 m² non chauffée/non rafraîchie)").

## Logique de calcul

### Statut thermique (chauffé / rafraîchi)

`BDD_Salles.Surface_Chaufee` et `Surface_Rafraichie` (déjà saisis pour chaque
local) déterminent 4 statuts possibles, chacun affiché comme une ligne
séparée dans le tableau de résultats pour une même sous-catégorie OPERAT :
Chauffée (seule), Chauffée + rafraîchie, Rafraîchie (seule), Non chauffée /
non rafraîchie.

### Trois modes par type de local

- **Affectation directe** : le local pointe vers une sous-catégorie OPERAT
  précise (ex. Bureau → Enseignement Supérieur / Administration et bureaux).
- **Répartition au prorata** : pour les circulations, sanitaires, locaux
  techniques… qui n'ont pas d'équivalent OPERAT propre. Leur surface est
  répartie **automatiquement et proportionnellement** aux m² déjà affectés en
  mode direct, **dans le même bâtiment et le même statut thermique**. Exemple :
  un bâtiment a 100 m² de bureaux chauffés + 200 m² de salles de classe
  chauffées (affectation directe) et 120 m² de circulations/sanitaires
  chauffés (prorata) → les 120 m² sont répartis 33 %/67 % (proportionnel à
  100/300 et 200/300), exactement le calcul demandé. Si un statut thermique
  d'un bâtiment ne contient **aucun** local en affectation directe (aucune
  référence pour calculer un ratio), le prorata de ce statut reste non
  ventilé et un avertissement nommé le signale (bâtiment, statut thermique,
  m² concernés) plutôt que de deviner une répartition arbitraire.
- **Hors périmètre** : locaux structurels sans usage occupé propre (trémies,
  escaliers/ascenseurs en tant que vides de structure, combles, prolongements
  extérieurs, logements de fonction — le décret tertiaire ne s'applique pas à
  l'habitation…). Exclu des totaux OPERAT, affiché à part pour information.

Le calcul est fait **bâtiment par bâtiment** puis sommé, jamais au niveau EFA
directement (une répartition au prorata sur l'agrégat de plusieurs bâtiments
n'aurait pas de sens : chaque bâtiment a sa propre composition de surfaces).

### Filtrage Site/Bâtiment

Comme dans `dashboard-batiment`, les salles sont filtrées à la fois par
`Bâtiment` **et** par `Site` (celui du bâtiment sélectionné) : une salle dont
le `Site` diverge de celui de son `Bâtiment` dans `BDD_Salles` (incohérence de
saisie déjà rencontrée sur ce document — bâtiments homonymes sur des sites
différents) est exclue des totaux et signalée nommément plutôt que comptée
dans le mauvais site.

## Proposition par défaut : raisonnement

La correspondance pré-remplie automatiquement suit le même barème pour tous
les bâtiments au départ (un type de local UMPV pointe par défaut vers la même
sous-catégorie OPERAT partout), mais **chaque bâtiment peut ensuite s'en
écarter indépendamment** puisque le mapping est stocké par bâtiment. Le
barème de départ a été établi ainsi :

- **Sans ambiguïté** (repris tel quel) : Vacant → Local vacant (SCAP0001) ;
  Aires de stationnement/manœuvre/rampes/garage → Stationnement en
  infrastructure (SCAP2201) ; Réception public → Zone d'accueil du public
  (SCAP0407) ; Amphithéâtre → Amphithéâtre/Auditorium (SCAP070305) ; Réfectoire/
  Cuisine/Cafétéria → Restauration collective scolaire et universitaire
  (SCAP1808) ; Imprimerie → Atelier d'imprimerie numérique (SCAP1103) ;
  Archives → Zone d'archives (SCAP0409).
- **Circulations, sanitaires, locaux techniques "occupants", stockage,
  ménage/standard, kitchenette, tisanerie** → mode "Répartition au prorata"
  (ce sont exactement les surfaces citées dans la demande initiale comme sans
  équivalent OPERAT).
- **Structures non occupées** (trémies/escaliers/ascenseurs en tant que
  vides, combles, hauteur < 1,80 m, toiture, prolongements extérieurs,
  logements de fonction, gaine technique, espaces verts intérieurs) → mode
  "Hors périmètre". **À reconsidérer maintenant que le widget peut utiliser
  la Surface de Plancher (SP)** : la SP inclut généralement les escaliers et
  autres circulations verticales, contrairement à l'hypothèse initiale de ce
  barème (fondée sur la surface utile) qui les traitait comme des vides
  structurels sans surface réglementaire propre. Une fois votre table SP
  configurée (voir plus haut), revérifiez ces types dans le paramétrage de
  chaque bâtiment — ils devraient probablement passer en "Répartition au
  prorata" plutôt que "Hors périmètre" si votre SP les inclut.
- **Salles de réunion/formation/cours/bibliothèque/salon de réception** →
  affectées à la sous-catégorie "Enseignement Supérieur" la plus proche
  (Administration et bureaux, ou "Salles de formation… sans process"), **à
  valider en priorité** : c'est la zone la plus sujette à interprétation
  (ex. distinguer une vraie salle de TP avec process d'une salle de cours
  classique n'est pas possible depuis les données actuelles).

## Installation dans Grist

1. Ouvrez votre document SI Patrimoine dans Grist.
2. **Add New → Add Widget to Page**, choisissez **Custom** puis **Custom URL** :

   ```
   https://bigorneau15652.github.io/map/operat-surfaces/index.html
   ```

3. Acceptez la demande d'autorisation **"Full document access"**.
4. Choisissez un EFA, puis un **bâtiment précis**, et ouvrez **⚙ Paramétrer
   les correspondances** pour relire/ajuster la proposition initiale de ce
   bâtiment avant toute utilisation officielle. À répéter pour chaque
   bâtiment que vous voulez valider.

## Développement / test local

Fichier HTML unique, sans étape de build. Pour tester sans un vrai serveur
Grist, voir le mécanisme `mock-grist.js` / `demo.html` utilisé par
`carte-batiments/` dans ce dépôt (non fourni ici, à reconstituer au besoin :
il suffit de remplacer le tag `<script src="https://docs.getgrist.com/grist-plugin-api.js">`
par un mock qui répond aux mêmes méthodes `docApi.fetchTable` /
`applyUserActions` / `ready` / `onOptions` / `setOption`).

Voir aussi `/CLAUDE.md` à la racine du dépôt avant tout changement visuel
(lisibilité des bannières, contrôles de formulaire en mode sombre, test à
largeur de panneau étroite).
