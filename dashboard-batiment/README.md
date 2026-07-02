# Tableau de bord Bâtiment

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui reproduit,
pour n'importe quel bâtiment du SI Patrimoine, la fiche de synthèse utilisée pour
le bâtiment A du site route du Guesclin (`103_Bâtiment_A_13_11_20.pdf`) : mêmes
intitulés, mêmes sections, dans le même ordre — plus des graphiques à l'écran
(absents du PDF d'origine) qui disparaissent à l'impression pour que la fiche
imprimée tienne sur 2 pages A4 (recto-verso), comme le document de référence.

## Fonctionnement

Le widget se connecte au document Grist ouvert et lit directement les tables :

- `BDD_Sites`
- `BDD_Batiments`
- `BDD_Etages`
- `BDD_Salles`
- `Table_locaux_types_et_correspondance`
- `Table_d_occupation_fonctionnelle`
- `Table_Type_d_ERP`

Il n'est **pas** lié à une seule table via le panneau "Select by" : il embarque ses
propres menus déroulants **Site** puis **Bâtiment**, et recalcule tout côté
navigateur à chaque changement de sélection. Il faut donc lui accorder l'accès
**"Full document access"** lors de l'ajout (Grist le demande automatiquement,
voir ci-dessous).

## Installation dans Grist

1. Ouvrez votre document SI Patrimoine dans Grist.
2. Ajoutez une nouvelle page : **Add New → Add Widget to Page** (ou dans une vue existante,
   bouton **+** en haut à droite du widget).
3. Choisissez **Custom** puis **Custom URL**, et collez l'URL suivante :

   ```
   https://bigorneau15652.github.io/map/dashboard-batiment/index.html
   ```

4. Grist affiche une demande d'autorisation "Full document access" : acceptez-la.
   C'est nécessaire car le widget doit lire plusieurs tables à la fois (Sites,
   Bâtiments, Étages, Salles, Locaux types, Occupations, Types d'ERP), pas
   seulement la table sur laquelle il est posé.
5. Le widget affiche deux menus déroulants **Site** et **Bâtiment**. Le contenu
   du tableau de bord se met à jour automatiquement à chaque sélection.
6. Bouton **⟳ Actualiser** : recharge les données du document (utile après une
   modification de la base pendant que le widget est ouvert).
7. Bouton **🖶 Imprimer** : ouvre l'impression du navigateur avec une mise en page
   compacte (menus, avertissements et graphiques masqués), calée sur 2 pages A4.

## Structure de la page (stable d'une version à l'autre)

Pour que les futures demandes de modification puissent cibler un emplacement
précis, chaque section a un id HTML stable, dans l'ordre du PDF de référence :

**Page 1** (`#page1`)
- `#sec-batiment` — Numéro / Appellation / Nom du bâtiment / Année de construction / Commentaires
- `#sec-kpi` — les 6 indicateurs (Nombre de postes de travail, Effectif personnel, les 4 ratios)
- `#sec-reglementaire` — Informations réglementaires + Date visite/avis commission + Capacité d'accueil
- `#sec-surfaces-totales` — Emprise au sol + tableau Surfaces par niveau (SUN/SUB/SPC/SHON/SHOB) + graphique (écran uniquement)

**Page 2** (`#page2`, saut de page forcé à l'impression)
- `#sec-surfaces-fonctionnelles` — identité du bâtiment + tableau "Type de surface fonctionnelle" + graphique (écran uniquement)
- `#sec-repartition-bureau` — tableau "Répartition des surfaces de bureau et salles de cours"

Aucun indicateur n'a été ajouté au-delà de ce que contient le PDF : la section
"Répartition par catégorie de local" d'une version précédente (qui n'existait
pas dans le PDF) a été retirée.

## Correspondances utilisées avec les colonnes existantes

| Intitulé exact du PDF                 | Source dans Grist                                                        |
|----------------------------------------|---------------------------------------------------------------------------|
| Nombre de postes de travail            | Somme de `BDD_Salles.Nb_de_postes_de_travail` pour le bâtiment (hors salles au Site incohérent, voir plus bas) |
| Effectif personnel (administratif, technique, enseignants,…) | Aucune colonne équivalente identifiée dans le document ; affiché « — ». Dites-moi quelle colonne l'alimente si vous en avez une. |
| Capacité d'accueil                     | `BDD_Batiments.Effectif`                                                   |
| Ratio d'occupation SUN/Poste de travail (cible 12m²) | SUN bâtiment ÷ Nombre de postes de travail |
| Ratio d'optimisation de la capacité d'accueil SUN/SUB (cible > 67%) | SUN bâtiment ÷ SUB bâtiment |
| Ratio d'optimisation de la conception (SPC) SUB/SPC (cible > 85%) | SUB bâtiment ÷ SPC bâtiment |
| Ratio d'optimisation de la conception (SHON) SUB/SHON | SUB bâtiment ÷ SHON bâtiment |
| Type établissement principal / secondaire (1)(2)(3) | 1er, 2e, 3e, 4e élément de `BDD_Batiments.Type_d_ERP2` (liste), code repris depuis `Table_Type_d_ERP` |
| Catégorie d'établissement               | `BDD_Batiments.Categorie_d_ERP`                                            |
| Date visite commission / Avis commission / Date du dernier avis commission | `BDD_Batiments.Date_de_visite_de_commission` / `AvisCommission` / `Date_du_dernier_avis` |
| SUN/SUB/SPC/SHON/SHOB par niveau et total | Somme de `BDD_Etages.Surface_SUN_m2_` / `Surface_SUB_m2_` / `Surface_SP_m2_` / `Surface_SHON_m2_` / `Surface_SHOB_m2_2` (hors étages au Site incohérent) |
| Surfaces fonctionnelles (Administration, Enseignement, …) | `BDD_Salles` groupées par `Occupation`, filtrées sur `Type_d_usage.SUB = vrai` |
| Répartition des surfaces de bureau et salles de cours | `BDD_Salles` filtrées sur `Type_d_usage.Libellé` ∈ {Bureau, Salle de cours} et `SUB = vrai`, groupées par Occupation |

Les cibles affichées sur les indicateurs (SUN/poste ≤ 12-15-20 m², SUN/SUB > 67 %,
SUB/SPC > 85 %) pilotent uniquement le code couleur vert/orange/rouge ; ajustez les
seuils dans le script (`renderKpis`) si vos cibles internes diffèrent.

## Points de vigilance repérés dans le fichier `.grist` fourni

### 1. Lignes (salles ET étages) au `Site` incohérent avec leur `Bâtiment`

En comparant les surfaces recalculées avec celles du PDF de référence (bâtiment A,
103, route de Mende) étage par étage, on constate que SUB/SPC/SHON/SHOB collent au
PDF à ±5 % dès qu'on ne garde que les lignes dont le `Site` correspond au site du
bâtiment sélectionné. Sans ce filtre, les surfaces se retrouvent 3 à 11 fois plus
élevées que le PDF.

Le widget filtre donc désormais **à la fois** `BDD_Salles` et `BDD_Etages` par
`Bâtiment` **et** par `Site` (celui du bâtiment sélectionné), et affiche un
avertissement listant des exemples de numéros de local / id_etage à vérifier
pour chaque cas — pas seulement un décompte, pour que vous puissiez retrouver les
lignes en cause dans Grist.

Si le formulaire Grist lui-même doit rester correct indépendamment du widget,
alignez la colonne formule `Surface utile / étage en m²` de `BDD_Etages` sur ses
colonnes voisines (`Surface SUN/SUB/SP/SHOB`, qui filtrent déjà sur `Site=$Site`) :

```python
salles = BDD_Salles.lookupRecords(Batiment=$Batiment, Etage=rec, Site=$Site)
sum(salle.Surface_utile_m2_ for salle in salles if salle.Surface_utile_m2_ is not None)
```

### 2. SP (SPC) et SHOB : calcul par soustraction, pas par addition

Les colonnes `Surface SP (m²)` et `Surface SHOB (m²)` de `BDD_Etages` se calculent
en partant d'une surface de base saisie manuellement par étage
(`Surface_base_pour_SDP_m2_` et `Surface_base_pour_SHOB_m2_`) et en **retranchant**
la surface des locaux dont le type d'usage est `False` pour SP / SHOB dans
`Table_locaux_types_et_correspondance` — et non en additionnant les locaux à `True`
comme SUN/SUB. Le résultat est protégé par `max(0, ...)` pour ne jamais afficher de
surface négative (cas du toit-terrasse sans base SDP renseignée). Ce calcul est
entièrement fait côté Grist ; le widget se contente de lire les colonnes déjà
calculées `Surface_SP_m2_` et `Surface_SHOB_m2_2`, donc aucune modification du
widget n'est nécessaire si vous ajustez encore cette formule.

### 3. SUN toujours un peu élevée après filtrage : à vérifier dans `Table_locaux_types_et_correspondance`

Même en filtrant correctement par `Site`, la surface **SUN** peut rester au-dessus
du PDF sur certains étages alors que SUB/SPC/SHON/SHOB collent bien sur les mêmes
étages — ce qui écarte un problème de filtrage. Cause probable : plusieurs types de
locaux « Circulation » (Circulation interne, Circulation primaire, Accueil/Attente,
Palier d'étage, Vérandas, Galerie non technique) ont l'indicateur `SUN` coché à vrai
dans `Table_locaux_types_et_correspondance`, alors que la Surface Utile Nette exclut
normalement les circulations. Choix de paramétrage métier qui vous revient — non
modifié automatiquement.

### 4. Doublons de lignes d'étage sur un même site (rare)

Le widget affiche un avertissement uniquement si un même bâtiment a, **pour le même
site**, plusieurs lignes d'étage portant le même nom (ex. deux "RDC" toutes deux
rattachées à Route de Mende). Avoir plusieurs étages *différents* (RDC, R+1, R+2…)
est normal et ne déclenche jamais cet avertissement.

## Développement / modification

Le widget est un unique fichier HTML autonome (`index.html`), sans étape de build :
toute modification du fichier est immédiatement effective une fois publiée sur
GitHub Pages. Les bibliothèques externes (API Grist, Chart.js) sont chargées depuis
un CDN, il n'y a rien à installer localement pour l'éditer.

Avant de livrer un changement visuel, voir aussi `/CLAUDE.md` à la racine du dépôt
(leçons apprises sur les widgets Grist : lisibilité des bannières, mise en page à
l'impression, fidélité à un document de référence).

Pour tester localement avant de pousser :

```bash
cd dashboard-batiment
python3 -m http.server 8590
```

puis, dans Grist, ajoutez un widget avec l'URL `http://localhost:8590/index.html`
(cela ne fonctionne que si votre instance Grist et votre navigateur peuvent
atteindre `localhost:8590`, ce qui est le cas pour grist.getgrist.com ouvert
depuis le même poste).
