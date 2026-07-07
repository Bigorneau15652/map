# Surfaces OPERAT par EFA

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui fait la
correspondance entre les surfaces des bâtiments de l'UMPV (classées selon la
nomenclature du ministère de l'Éducation nationale) et la classification par
usage exigée par la plateforme ADEME **OPERAT** (décret éco énergie tertiaire),
pour les 5 EFA (entités fonctionnelles assujetties) encore en activité :
Route de Mende, Béziers, Saint-Charles, Saint-Louis, Boutonnet.

## Fonctionnement général

Le widget se connecte au document Grist ouvert et lit directement les tables :

- `BDD_Sites`, `BDD_Batiments`, `BDD_Salles`
- `Table_locaux_types_et_correspondance` (types de locaux UMPV)
- `Segmentation_OPERAT` (nomenclature catégorie / sous-catégorie / code technique OPERAT)

Il n'est **pas** lié à une seule table via le panneau "Select by" : il embarque
ses propres menus déroulants **EFA (site)** puis **Bâtiment**, et recalcule
tout côté navigateur à chaque changement de sélection. Il faut donc lui
accorder l'accès **"Full document access"** lors de l'ajout (Grist le demande
automatiquement), nécessaire aussi bien pour lire ces tables que pour écrire
la table de correspondance décrite ci-dessous.

### Table de correspondance créée automatiquement

Au premier chargement, le widget crée dans votre document une table
**`Table_correspondance_OPERAT`** (si elle n'existe pas déjà), avec une ligne
par type de local UMPV et 3 colonnes :

- `TypeUsage` : référence vers `Table_locaux_types_et_correspondance`
- `Mode` : `Affectation directe` / `Répartition au prorata` / `Hors périmètre`
- `SousCategorieOPERAT` : référence vers `Segmentation_OPERAT` (uniquement
  utilisée en mode "Affectation directe")

Cette table est **visible et modifiable comme n'importe quelle table Grist**
dans le grid normal, pas seulement depuis le widget — vos collègues peuvent
l'auditer sans ouvrir le widget. Une proposition initiale est pré-remplie
automatiquement (voir "Proposition par défaut" plus bas) ; si vous ajoutez de
nouveaux types de locaux plus tard dans `Table_locaux_types_et_correspondance`,
le widget leur ajoute une ligne de proposition à l'ouverture suivante, sans
jamais toucher aux lignes déjà présentes (donc sans jamais écraser vos
corrections).

Le bouton **⚙ Paramétrer les correspondances** ouvre l'écran d'édition (menus
déroulants Mode / Catégorie OPERAT / Sous-catégorie OPERAT par type de local,
chaque changement est enregistré immédiatement). Le bouton **↺ Restaurer les
propositions par défaut** écrase tout (avec confirmation) pour repartir de la
proposition initiale.

**Cette proposition initiale n'est qu'une suggestion et doit être relue et
validée avant tout usage officiel** — voir le détail du raisonnement plus bas.

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

La correspondance pré-remplie automatiquement est **globale** (un type de
local UMPV pointe toujours vers la même sous-catégorie OPERAT, quel que soit
le site) et a été établie ainsi :

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
  "Hors périmètre".
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
4. Choisissez un EFA dans le menu déroulant. Ouvrez **⚙ Paramétrer les
   correspondances** pour relire/ajuster la proposition initiale avant toute
   utilisation officielle.

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
