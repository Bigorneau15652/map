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
| `visible` | Bool | `true` = couleur normale · `false` = bâtiment grisé |

> **Important** : les valeurs de `Site` et `Bâtiment` doivent reprendre **exactement** les
> intitulés ci-dessous (accents compris) pour que le widget retrouve la bonne forme sur le plan.
> C'est directement la liste de votre fichier `Site et bâtiment.xlsx` — vous pouvez l'importer telle quelle.

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
| `active` | Bool | `true` = catégorie affichée sur la carte |

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

## Table 3 : `Batiment_categories`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `batiment` | Ref → Batiments | Référence vers la ligne Batiments |
| `categorie` | Ref → Categories | Référence vers la ligne Categories |

Cette table peut être laissée **vide** : le widget la remplit automatiquement quand vous
cliquez sur les pastilles de couleur dans le panneau "Bâtiments".

---

## Configuration du widget dans Grist

1. Dans la vue, ajouter un **Custom Widget**
2. URL : `https://bigorneau15652.github.io/map/carte-batiments/`
3. Accès requis : **Accès complet au document** (obligatoire pour lire/écrire les 3 tables)
4. Ouvrir ⚙️ dans le widget et choisir vos 3 tables (Bâtiments / Catégories / Affiliations)

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
