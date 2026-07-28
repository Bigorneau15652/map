# Surfaces OPERAT par EFA — catégorie dominante

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui calcule,
pour chacun des 5 EFA (entités fonctionnelles assujetties au sens du décret
éco énergie tertiaire) encore en activité à l'UMPV — **Route de Mende,
Béziers, Saint-Charles, Saint-Louis, Boutonnet** — la surface à déclarer sur
la plateforme ADEME **OPERAT**, catégorie par catégorie, statut thermique par
statut thermique.

Contrairement au widget `operat-surfaces/` (une approche différente, conservée
telle quelle), celui-ci applique la règle de **catégorie dominante** : un
bâtiment n'est jamais déclaré "à cheval" sur trop de petites catégories —
OPERAT attend qu'un bâtiment principalement affecté à un usage soit détecté
comme tel dans son ensemble.

## Pourquoi ce widget est simple

`BDD_Salles` contient déjà, salle par salle, `Categorie_SCE_OPERAT` et
`SS_categorie_SCE_OPERAT` : la classification de base existe. Ce widget ne
fait **aucune écriture** dans le document — il lit, agrège, et affiche. Pour
corriger la classification d'une salle, modifiez directement `BDD_Salles`
dans la grille Grist ; le widget recalculera au prochain rafraîchissement.

## Logique de calcul

### Quatre cas par salle, selon `Categorie_SCE_OPERAT`

- **Catégorie vide (id 0)** → **hors périmètre** : structures non occupées
  (escaliers-vides, toitures, rampes, aires de manœuvre, vérandas…). Exclues
  du total OPERAT, affichées à part pour information.
- **Catégorie "À répartir"** → circulations, sanitaires, locaux techniques
  "occupants"… qui n'ont pas d'équivalent OPERAT propre. Redistribuées dans
  les sous-catégories dominantes **"utilisées"** du bâtiment (voir plus bas).
- **Catégorie "Local vacant"** → locaux réellement inoccupés. Toujours
  affichée avec sa propre surface, telle quelle, dans le total OPERAT du
  bâtiment. Cette catégorie ne participe **jamais** à la règle de catégorie
  dominante et ne reçoit donc jamais de surface redistribuée depuis une
  autre catégorie (voir plus bas).
- **Toute autre catégorie** ("utilisée") → affectation directe à sa
  `SS_categorie_SCE_OPERAT`. Une salle avec une catégorie renseignée mais
  sans sous-catégorie est exclue et signalée (donnée incomplète).

### Règle de catégorie dominante (par bâtiment, jamais au niveau EFA)

Sur la surface des catégories **"utilisées"** en affectation directe
uniquement (hors "à répartir" et hors "Local vacant") :

1. Si une sous-catégorie atteint **70%** ou plus de cette surface, **tout le
   bâtiment** (y compris "à répartir" et les autres sous-catégories
   "utilisées" minoritaires) lui est affecté intégralement.
2. Sinon, les **3 sous-catégories "utilisées" les plus grandes** sont
   retenues (même si aucune n'atteint 30%, ou si plus de 3 en dépassent 30% :
   la règle des pourcentages sert à motiver le choix, mais la sélection
   reste toujours plafonnée aux 3 plus grandes). La surface du bâtiment
   restant à classer — catégories "utilisées" non retenues + "à répartir",
   mais **jamais** "Local vacant" — leur est redistribuée au prorata de
   leurs surfaces directes respectives.
3. Si aucune sous-catégorie "utilisée" n'est affectée en direct dans un
   bâtiment (cas rare : un local technique isolé, poste EDF, chaufferie…),
   aucune règle ne peut s'appliquer au "à répartir" restant : ce cas est
   signalé nommément et sa surface apparaît dans un total **"Non classé"**
   séparé plutôt que d'être compté ou perdu silencieusement. "Local vacant",
   lui, reste classé tel quel dans ce cas — ce n'est pas une anomalie.

**Exemple concret** (EFA Saint-Louis) : une bibliothèque de 40 m²
("Culture et spectacles") dans un bâtiment autrement composé de bureaux, de
salles de cours et de locaux vacants ne fait pas partie des 3 catégories
"utilisées" dominantes retenues — sa surface est répartie au prorata entre
les catégories "utilisées" retenues (salles de cours, bureaux…), jamais vers
"Local vacant", même si "Local vacant" est la plus grande surface directe du
bâtiment.

Le calcul est fait **bâtiment par bâtiment** puis sommé au niveau EFA — une
répartition au prorata sur l'agrégat de plusieurs bâtiments n'aurait pas de
sens, chaque bâtiment ayant sa propre composition de surfaces.

### Statuts thermiques

`Surface_Chaufee` et `Surface_Rafraichie` déterminent 4 statuts, chacun une
ligne séparée : Chauffée + rafraîchie, Chauffée (seule), Rafraîchie (seule),
Non chauffée / non rafraîchie. La redistribution ci-dessus est recalculée
séparément pour chaque statut, avec les mêmes poids (proportion de chaque
sous-catégorie "utilisée" retenue dans la surface totale "utilisée" du
bâtiment), appliqués au total de ce statut pour les catégories "utilisées" +
"à répartir" (hors périmètre exclu). "Local vacant" garde son propre statut
thermique réel, indépendamment de cette redistribution.

### Ce qui est exclu du calcul, et pourquoi

- **Bâtiments détruits ou en fin d'exploitation** (`Destruction` ou
  `Date_de_fin_d_exploitation` renseignée dans `BDD_Batiments`) : non actifs,
  hors scope OPERAT.
- **Salles dont le Site diverge de celui de leur bâtiment** dans
  `BDD_Salles` (incohérence de saisie déjà rencontrée sur ce document) :
  exclues et signalées nommément plutôt que comptées dans le mauvais site.
- **Salles à `Categorie_SCE_OPERAT` invalide** (valeur non numérique — une
  formule Grist en erreur dans le document source) : exclues et signalées
  nommément (numéro de salle) pour correction dans `BDD_Salles`.

Chaque avertissement liste jusqu'à 5 numéros de salle concernés ("et N
autres" au-delà), pour permettre de retrouver et corriger la donnée
source — jamais un simple compte abstrait.

## Utilisation

1. Ouvrez votre document SI Patrimoine dans Grist.
2. **Add New → Add Widget to Page**, choisissez **Custom** puis **Custom
   URL** :

   ```
   https://bigorneau15652.github.io/map/surfaces-operat-efa/index.html
   ```

3. Acceptez la demande d'autorisation **"Full document access"** (nécessaire
   car le widget lit plusieurs tables sans passer par "Select by").
4. Choisissez **Vue d'ensemble** pour les 5 EFA en une fois, ou un EFA précis
   dans le menu déroulant pour le détail par bâtiment. Le bouton
   **❓ Méthode de calcul** rappelle la logique ci-dessus dans le widget
   lui-même. Toutes les surfaces sont affichées arrondies au m² entier.
5. Les chapitres **"Sous-catégorie SCE OPERAT"** et **"Détail par bâtiment"**
   sont repliables (cliquez sur leur titre). Le bouton
   **🖶️ Imprimer / Export PDF** ouvre la boîte de dialogue d'impression du
   navigateur (qui permet d'enregistrer en PDF) ; les chapitres repliés sont
   temporairement dépliés le temps de l'impression pour que rien ne manque
   sur le papier, puis reprennent leur état à l'écran une fois la boîte de
   dialogue fermée.

Le dernier EFA consulté est mémorisé (via `grist.setOption`) et resélectionné
à la prochaine ouverture.

### Si vos tables/colonnes portent d'autres noms

Cliquez sur **⚙️ Colonnes utilisées** dans la barre d'outils : un panneau
liste, pour chacune des 5 tables utilisées (Sites, Bâtiments, Salles,
Catégories SCE OPERAT, Sous-catégories SCE OPERAT), un menu déroulant pour
choisir la table Grist à utiliser, puis un menu déroulant par colonne
attendue — chaque liste est peuplée à partir des tables/colonnes réellement
présentes dans votre document (via les tables internes Grist
`_grist_Tables` / `_grist_Tables_column`), pas de saisie libre. Cliquez
**Enregistrer et recalculer** : la config est mémorisée (`grist.setOption`)
et le widget relit les données aussitôt avec le nouveau mappage — pas besoin
de modifier `index.html`. **Réinitialiser aux valeurs par défaut** restaure
les noms du document "Bac à sable SIPI" d'origine (voir `DEFAULT_TABLES` /
`DEFAULT_COL` / `CONFIG_SCHEMA` en tête du `<script>` si vous voulez changer
ces valeurs par défaut elles-mêmes).

Symptôme typique d'une colonne renommée sans que la config n'ait été mise à
jour : une case "Chauffée + rafraîchie" ou "Chauffée (seule)" qui tombe à
0 m² partout alors qu'il y a réellement des locaux chauffés (la colonne
`Surface_Chaufee` — ou `Surface_Rafraichie` — n'est plus trouvée par le nom
attendu, donc traitée comme "non cochée" pour toutes les salles). Rouvrez
**⚙️ Colonnes utilisées** et repointez la colonne concernée.

Une table introuvable (mauvais nom, table supprimée) est toujours signalée
par un bandeau rouge qui la nomme, que la config vienne des valeurs par
défaut ou d'un mappage personnalisé.

## Développement / test local

Fichier unique, sans étape de build. `index.html?demo=1` charge un mock de
l'API Grist (`mock-grist.js`) pré-rempli avec un extrait réel et trimmé du
document (`demo-seed.js` — 10 bâtiments choisis pour couvrir : catégorie
dominante à 70%+, répartition à 2-3 catégories, bâtiment sans catégorie
dominante, salles à catégorie invalide, salles sans sous-catégorie), plus une
ligne de test synthétique pour l'avertissement "Site incohérent". `mock-grist.js`
reconstruit aussi `_grist_Tables` / `_grist_Tables_column` à partir des clés de
`demo-seed.js`, pour pouvoir tester le panneau **⚙️ Colonnes utilisées** en
local. Servez le dossier avec un serveur statique quelconque (`python3 -m
http.server`) et ouvrez `index.html?demo=1`.

Voir `/CLAUDE.md` à la racine du dépôt avant tout changement visuel
(lisibilité des bannières, contrôles de formulaire en mode sombre, test à
largeur de panneau étroite — déjà vérifiés pour ce widget).
