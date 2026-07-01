# Schéma Grist – Carte des Bâtiments

Ce widget reprend le principe de `carte-france`, mais colorie les **bâtiments** de vos 5 sites
au lieu des départements. Les formes de chaque bâtiment ont été tracées à partir du plan
"Plan classement énergétique des bâtiments" et sont embarquées dans `buildings-data.js`
(aucune requête réseau nécessaire pour la géométrie).

## Table 1 : `Batiments`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `Site` | Text | Nom du site (voir liste exacte ci-dessous) |
| `Bâtiment` | Text | Nom du bâtiment (voir liste exacte ci-dessous) |
| `note` (ou le nom que vous voulez) | Text | **Optionnel.** Nom de la catégorie active pour ce bâtiment (doit correspondre exactement au `nom` d'une ligne de la table `Categories`, ex : `Très bon`). Laisser vide = bâtiment non coloré. |
| `visible` (ou le nom que vous voulez) | Bool | **Optionnel.** `true`/coché = couleur normale · `false`/décoché = bâtiment grisé. Laisser ce menu vide dans ⚙️ → tous les bâtiments sont toujours visibles. |

> Comme pour la table Catégories, les noms `note`/`visible` sont juste indicatifs : dans ⚙️, vous
> choisissez la colonne exacte de **votre** table (ex : `Categories_energie`, `Active`…).

> **Important** : les valeurs de `Site` et `Bâtiment` doivent reprendre **exactement** les
> intitulés ci-dessous (accents compris) pour que le widget retrouve la bonne forme sur le plan.
> C'est directement la liste de votre fichier `Site et bâtiment.xlsx` — vous pouvez l'importer telle quelle.

> La colonne `note` doit être de type **Texte** (pas Référence) pour que le widget puisse y écrire
> directement le nom de la catégorie quand vous cliquez une pastille de couleur.

<details>
<summary>Liste complète des 51 lignes (cliquer pour déplier)</summary>

| Site | Bâtiment |
|------|----------|
| Route de Mende | Amphis 1 2 3 |
| Route de Mende | Amphis 5 6 7 |
| Route de Mende | Bâtiment A |
| Route de Mende | Bâtiment ATRIUM |
| Route de Mende | Bâtiment B |
| Route de Mende | Bâtiment C |
| Route de Mende | Bâtiment D |
| Route de Mende | Bâtiment E |
| Route de Mende | Bâtiment F |
| Route de Mende | Bâtiment G |
| Route de Mende | Bâtiment H |
| Route de Mende | Bâtiment I |
| Route de Mende | Bâtiment J |
| Route de Mende | Bâtiment K |
| Route de Mende | Bâtiment L |
| Route de Mende | Bâtiment M |
| Route de Mende | Bâtiment N |
| Route de Mende | Maison des Personnels |
| Route de Mende | Bâtiment O |
| Route de Mende | Bâtiment P |
| Route de Mende | Préfa 1-2-3 |
| Route de Mende | P4 |
| Route de Mende | P5 |
| Route de Mende | P6 |
| Route de Mende | P7 |
| Route de Mende | P8 |
| Route de Mende | P9 |
| Route de Mende | P10 |
| Route de Mende | P11 |
| Route de Mende | P12 |
| Route de Mende | P13 |
| Route de Mende | P14 |
| Route de Mende | Bâtiment Q |
| Route de Mende | Kiosque |
| Route de Mende | Bâtiment R |
| Route de Mende | Bâtiment S |
| Route de Mende | Bâtiment T |
| Route de Mende | Bâtiment U |
| Route de Mende | Bâtiment V |
| Route de Mende | Bâtiment W |
| Route de Mende | Bâtiment Z |
| Béziers | Du Guesclin |
| Béziers | Préfa |
| Béziers | Projet d'extension |
| Boutonnet | Bâtiment A |
| Boutonnet | Bâtiment H |
| Boutonnet | Bâtiment I |
| Boutonnet | Bâtiment J |
| Saint-Charles | Saint-Charles 1 |
| Saint-Charles | Saint-Charles 2 |
| Saint-Louis | Saint-Louis |

</details>

### ⚠️ Points à vérifier avec vous

- **`P12`** est maintenant tracé (petit bâtiment bleu entre `Kiosque` et `G`), d'après votre
  dernier plan.
- **`Préfa 1-2-3`** est une **seule ligne / un seul bâtiment** dans Grist : les 3 rectangles
  visibles sur le plan changent tous de couleur ensemble quand vous colorez cette ligne (ce n'est
  pas 3 bâtiments distincts, conformément à votre remarque).
- **`Projet d'extension`** (Béziers) est tracé mais **volontairement sans catégorie par défaut**
  (le bâtiment n'existe pas encore) — vous choisirez sa couleur/catégorie vous-même le moment venu.
- **Zones non maîtrisées / hangars** (partie hachurée à Saint-Charles, 2 hangars à Boutonnet) ne
  sont **pas des lignes Grist** — ce sont des zones fixes, verrouillées, non cliquables, affichées
  automatiquement par le widget (voir plus bas). Vous n'avez rien à ajouter dans Grist pour elles.
- **Saint-Charles** retracé à partir de votre nouveau plan (zone verrouillée plus petite, forme
  affinée). Aucun changement de votre côté dans Grist.
- **Correction interne** : plusieurs bâtiments avec une cour intérieure/fenêtre (`L`, `S`, `K`,
  `H`, `Bâtiment ATRIUM`) s'affichaient à tort comme des blocs pleins — leurs découpes internes
  s'affichent maintenant correctement. Aucun changement de votre côté dans Grist.
- **`Projet d'extension`** (Béziers) retracé selon votre dernier plan — c'est maintenant un
  rectangle détaché de `Du Guesclin` (au lieu de la forme en croix précédente).
- **Configuration simplifiée** : le widget accepte maintenant directement une table Bâtiments
  avec une colonne "note/catégorie" (une seule catégorie par bâtiment), sans avoir besoin de la
  table `Batiment_categories`. Voir "Configuration du widget" ci-dessous pour le détail des
  menus déroulants.
- **Boutonnet (A / H / I / J)** : confirmé sur votre dernier plan (labels visibles) — `A` est le
  grand bâtiment en M, `H`/`I`/`J` les 3 petits blocs séparés. Les 2 hangars adjacents sont
  verrouillés (voir point ci-dessus).
- Les bâtiments `A`, `H`, `I`, `J` existent à la fois sur **Route de Mende** et **Boutonnet** :
  le widget les distingue bien via la colonne `Site` (clé `Site|Bâtiment`).

---

## Table 2 : `Categories`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `nom` | Text | Nom de la catégorie (ex : `Très bon`) |
| `couleur` | Text | Couleur : nom FR (`rouge`, `bleu`…) ou HEX (`#e74c3c`) |
| `active` | Bool | **Optionnel.** `true` = catégorie affichée sur la carte. Si votre table n'a pas cette colonne (ou si vous ne la configurez pas dans ⚙️), **toutes les catégories sont considérées actives** par défaut. |

> Les noms de colonnes ci-dessus (`nom`, `couleur`, `active`) sont juste les noms **par défaut**.
> Dans ⚙️, vous pouvez faire correspondre ces 3 rôles à **n'importe quel nom de colonne** de votre
> table Catégories (ex : `Catégorie`, `Couleur`, `Niveau`…) via les menus "Colonne 'nom'/'couleur'/'active'
> dans la table Catégories".

**Exemple reprenant l'échelle du plan d'origine (libre à vous de la modifier/étendre) :**
```
Très bon                          | vert   | true
À améliorer                       | bleu   | true
Rénovation énergétique            | orange | true
Restructuration globale           | rouge  | true
Bâtiment provisoire (pas de rénov)| gris   | true
```

**Couleurs nommées disponibles :** bleu, rouge, vert, jaune, orange, violet, rose, marron, gris, noir, blanc, cyan, turquoise, emeraude, brique

---

## Table 3 (optionnelle) : `Batiment_categories`

**N'existe que si vous voulez qu'un même bâtiment puisse cumuler plusieurs catégories à la fois.**
Si vous utilisez la colonne `note` de la table `Batiments` (une seule catégorie par bâtiment,
cas le plus courant), vous n'avez **pas besoin** de cette table — ignorez cette section.

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `batiment` | Ref → Batiments | Référence vers la ligne Batiments |
| `categorie` | Ref → Categories | Référence vers la ligne Categories |

Cette table peut être laissée **vide** : le widget la remplit automatiquement quand vous
cliquez sur les pastilles de couleur dans le panneau "Bâtiments" (uniquement si "Colonne
Catégorie / Note" n'est pas configurée).

---

## Configuration du widget dans Grist — pas à pas

1. Dans la vue, ajouter un **Custom Widget**.
2. URL : `https://bigorneau15652.github.io/map/carte-batiments/`.
3. Accès requis : **Accès complet au document** (sinon le widget ne peut ni lire ni écrire vos tables).
4. Ouvrir ⚙️ dans le widget. Voici **exactement** ce que chaque menu déroulant attend. Exemple
   avec une table `INFOENERGIE` (Site, Bâtiment, une colonne catégorie, une colonne active) et
   une table `Table_Categories_Infoenergie` (nom, couleur, éventuellement un niveau) :

| Menu déroulant | Que choisir |
|---|---|
| **Table des Bâtiments** | votre table qui liste les bâtiments (ex : `INFOENERGIE`) |
| **Colonne "Site" dans la table Bâtiments** | la colonne qui contient le nom du site (`Route de Mende`, `Béziers`…) |
| **Colonne "Bâtiment" dans la table Bâtiments** | la colonne qui contient le nom du bâtiment (`Bâtiment A`, `Amphis 1 2 3`…) |
| **Colonne "Catégorie / Note" (optionnel)** | la colonne qui contient **la catégorie actuelle de chaque bâtiment**. Sa valeur doit être le nom exact d'une ligne de votre table Catégories (ex : `Très bon`) |
| **Colonne "Visible / Active" (optionnel)** | la colonne booléenne qui grise un bâtiment (laisser vide si vous n'en avez pas → tout reste visible) |
| **Table des Catégories** | votre table catégorie ↔ couleur (ex : `Table_Categories_Infoenergie`) |
| **Colonne "nom" dans la table Catégories** | la colonne avec le nom de chaque catégorie (ex : `Catégorie`, `Niveau`…) |
| **Colonne "couleur" dans la table Catégories** | la colonne avec la couleur (ex : `Couleur`) |
| **Colonne "active" dans Catégories (optionnel)** | laissez vide si votre table n'a pas de colonne "active"/"sélection" — dans ce cas **toutes les catégories sont affichées par défaut** |
| **Table des Affiliations** | **laissez sur "— choisir —" / vide** si vous utilisez la colonne "Catégorie / Note" ci-dessus (cas le plus courant) |
| **Colonne "bâtiment" / "catégorie" dans Affiliations** | n'apparaissent que si vous avez rempli "Table des Affiliations" — ignorez-les sinon |

5. Cliquez **💾 Enregistrer**.

Après l'enregistrement, chaque bâtiment doit se colorer selon la valeur de votre colonne
"Catégorie / Note". Cliquer une pastille de couleur dans le panneau "Bâtiments" **écrit
directement** le nom de la catégorie dans cette colonne (et un second clic sur la même pastille
l'efface).

> **Le calage (position/échelle/rotation du plan sur le satellite) et le fond de carte ne sont
> jamais perdus** en changeant/ré-enregistrant cette configuration : chaque sauvegarde ne modifie
> que les réglages qu'elle concerne, le reste est conservé.

> ⚠️ Si après avoir enregistré, la liste "Bâtiments" reste vide (`0/0`) ou qu'un message
> d'avertissement orange apparaît en haut du widget, vérifiez que vos colonnes "Site" et
> "Bâtiment" sont bien de type **Texte** dans Grist (pas *Référence*). Une colonne Référence
> renvoie un identifiant numérique et non le texte affiché, ce que le widget ne sait pas
> interpréter pour retrouver la forme du bâtiment sur le plan.

## Fonds de carte

Un sélecteur 🗺️ en bas à gauche de la carte permet de changer de fond à la volée (aucune clé API
requise) :

| Fond | Usage recommandé |
|------|-------------------|
| **OpenStreetMap Standard** *(par défaut)* | le plus précis pour positionner les bâtiments (rues, emprises au sol) |
| **Esri Satellite** | vue aérienne réelle — pratique pour voir la végétation / le bâti existant |
| Esri Street Map, Esri World Topo, CartoDB Positron, CartoDB Voyager | variantes plus sobres selon le rendu souhaité |

Le curseur de transparence à droite du sélecteur s'applique au fond actif. Le choix de fond est
mémorisé (options du widget) pour tous les utilisateurs du document.

## Zones verrouillées (non sélectionnables)

Ces zones sont affichées avec une **trame hachurée grise et un contour pointillé rouge**, en
permanence, quel que soit le mode d'affichage. Elles n'ont pas de ligne dans la table `Batiments`
et ne réagissent pas au clic — elles servent uniquement de repère visuel :

- **Saint-Charles** : partie du bâtiment que vous ne possédez pas.
- **Boutonnet** : les 2 hangars (non modifiables).

Si d'autres sites ont des zones similaires, indiquez-les-moi et je les ajoute de la même façon
(fichier `buildings-data.js`, variable `LOCKED_ZONES`).

## Calage du plan sur le satellite

Le dessin de chaque site est positionné par défaut sur le centre GPS réel du site (à partir des
liens Google Maps fournis), avec une échelle approximative. **Ce calage de départ est une
estimation** — un plan PowerPoint n'est pas géoréférencé nativement.

Pour l'affiner :
1. Cliquez **📐 Caler le plan** dans la barre du haut (pour le site actuellement affiché).
2. **Glissez** le dessin directement sur la carte pour le positionner sur les vrais bâtiments.
3. Ajustez les curseurs **Échelle** et **Rotation** jusqu'à ce que chaque forme corresponde
   au bâtiment réel visible sur l'image satellite.
4. Cliquez **💾 Enregistrer** — le calage est mémorisé (via les options du widget) pour tous
   les utilisateurs du document, pas seulement votre session.

Répétez l'opération pour chacun des 5 sites (le calage est indépendant par site).
