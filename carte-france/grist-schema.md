# Schéma Grist – Carte de France

## Table 1 : `Departements`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `code_dept` | Text | Code INSEE du département (ex: `01`, `75`, `971`) |
| `nom_dept` | Text | Nom complet (ex: `Ain`, `Paris`) |
| `code_region` | Text | Code INSEE de la région (ex: `84`) |
| `nom_region` | Text | Nom de la région (ex: `Auvergne-Rhône-Alpes`) |
| `visible` | Bool | `true` = couleur normale · `false` = département grisé |

> Importer les 101 lignes depuis le CSV fourni (`departements.csv`).

---

## Table 2 : `Categories`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `nom` | Text | Nom de la catégorie (ex: `Élevage bovin`) |
| `couleur` | Text | Couleur : nom FR (`rouge`, `bleu`…) ou HEX (`#e74c3c`) |
| `couleur_cumul` | Text | Couleur si ce dept est dans plusieurs catégories sélectionnées (optionnel, sinon couleur cumul globale du widget) |
| `selectionnee` | Bool | `true` = catégorie active sur la carte |

**Couleurs nommées disponibles :** bleu, rouge, vert, jaune, orange, violet, rose, marron, gris, noir, blanc, cyan

**Exemple :**
```
Élevage bovin     | rouge    |        | false
Élevage caprin    | vert     |        | false
Grande culture    | jaune    |        | false
Viticulture       | violet   |        | false
Population dense  | bleu     |        | false
```

---

## Table 3 : `Dept_Categories`

| Colonne | Type Grist | Description |
|---------|-----------|-------------|
| `dept` | Ref → Departements | Référence vers la ligne Departements |
| `categorie` | Ref → Categories | Référence vers la ligne Categories |
| `valeur` | Numeric | Valeur numérique (pour mode choroplèthe) |

**Exemple :**
```
dept=63 (Puy-de-Dôme) | categorie=Élevage bovin  | valeur=1240
dept=63 (Puy-de-Dôme) | categorie=Grande culture  | valeur=890
dept=15 (Cantal)      | categorie=Élevage bovin   | valeur=2100
```

---

## Configuration du widget dans Grist

1. Dans la vue, ajouter un **Custom Widget**
2. URL : `https://<votre-compte>.github.io/map/carte-france/`
3. Lier le widget à la table **`Categories`**
4. Accès requis : **Lire la table**

---

## Workflow d'utilisation

### Afficher une catégorie
→ Dans la table `Categories`, cocher `selectionnee = true` sur une ou plusieurs lignes  
→ La carte se met à jour automatiquement

### Griser des départements
→ Dans la table `Departements`, mettre `visible = false`  
→ Ces départements apparaissent en semi-transparent

### Mode choroplèthe
→ Sélectionner « Choroplèthe » dans la barre d'outils du widget  
→ Le dégradé de couleur est calculé sur la colonne `valeur` de `Dept_Categories`

### Sauvegarder le zoom
→ Cliquer « 💾 Sauver vue » dans la barre d'outils  
→ Le zoom et le centrage sont mémorisés pour toutes les sessions Grist futures
