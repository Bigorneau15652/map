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
<summary>Liste complète des 47 lignes (cliquer pour déplier)</summary>

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
| Route de Mende | Préfa 1-2-3 *(non tracé, voir note)* |
| Route de Mende | P4 *(non tracé, voir note)* |
| Route de Mende | P5 |
| Route de Mende | P6 *(non tracé, voir note)* |
| Route de Mende | P7 |
| Route de Mende | P8 |
| Route de Mende | P9 *(non tracé, voir note)* |
| Route de Mende | P10 |
| Route de Mende | P11 |
| Route de Mende | P12 *(non tracé, voir note)* |
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
| Boutonnet | Bâtiment A |
| Boutonnet | Bâtiment H |
| Boutonnet | Bâtiment I |
| Boutonnet | Bâtiment J |
| Saint-Charles | Saint-Charles 1 |
| Saint-Charles | Saint-Charles 2 |
| Saint-Louis | Saint-Louis |

</details>

### ⚠️ Points à vérifier avec vous

- **5 bâtiments sans forme dessinée** : `Préfa 1-2-3`, `P4`, `P6`, `P9`, `P12` (Route de Mende)
  n'apparaissent pas sur le plan PDF fourni — la ligne existe donc dans Grist mais ne
  s'affiche pas sur la carte (elle reste listée dans le panneau "Bâtiments", marquée ⚠︎).
  Si vous avez leur emplacement, je peux les ajouter.
- **Boutonnet (A / H / I / J)** : le plan ne nomme pas individuellement ces 4 bâtiments
  (contrairement à Route de Mende). J'ai fait une **hypothèse raisonnable** sur la correspondance
  forme ↔ nom (le plus grand bloc = A, les 3 autres = H / I / J). Si ce n'est pas le bon
  découpage, dites-moi lequel est lequel et je corrige la table `SITE_SHAPES` dans
  `buildings-data.js` (pas besoin de retracer les formes).
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

## Fond satellite

Le fond de carte utilise **Esri World Imagery** (satellite, gratuit, sans clé API). Le curseur
🛰️ en bas à gauche de la carte règle sa transparence.

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
