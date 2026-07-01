# Tableau de bord Bâtiment

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui reproduit,
pour n'importe quel bâtiment du SI Patrimoine, le type de fiche de synthèse
utilisé pour le bâtiment A du site route du Guesclin (ratios SUN/SUB/SPC/SHON/SHOB,
surfaces par niveau, surfaces fonctionnelles, avec graphiques).

## Fonctionnement

Le widget se connecte au document Grist ouvert et lit directement les tables :

- `BDD_Sites`
- `BDD_Batiments`
- `BDD_Etages`
- `BDD_Salles`
- `Table_locaux_types_et_correspondance`
- `Table_d_occupation_fonctionnelle`

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

   (GitHub Pages sert le contenu de la branche `master`/`main` du dépôt ; l'URL ne sera
   donc active qu'une fois ce dossier fusionné sur cette branche. En attendant, pour
   tester depuis la branche de travail, vous pouvez utiliser l'URL jsDelivr suivante,
   qui pointe directement sur la branche `claude/grist-building-dashboard-0zluzs` :

   ```
   https://cdn.jsdelivr.net/gh/Bigorneau15652/map@claude/grist-building-dashboard-0zluzs/dashboard-batiment/index.html
   ```
   )

4. Grist affiche une demande d'autorisation "Full document access" : acceptez-la.
   C'est nécessaire car le widget doit lire plusieurs tables à la fois (Sites,
   Bâtiments, Étages, Salles, Locaux types), pas seulement la table sur laquelle
   il est posé.
5. Le widget affiche deux menus déroulants **Site** et **Bâtiment**. Le contenu
   du tableau de bord se met à jour automatiquement à chaque sélection.
6. Bouton **⟳ Actualiser** : recharge les données du document (utile après une
   modification de la base pendant que le widget est ouvert).
7. Bouton **🖶 Imprimer** : ouvre l'impression du navigateur avec une mise en page
   nettoyée (masque les menus), pratique pour exporter la fiche en PDF, comme le
   document `103_Bâtiment_A_13_11_20.pdf` fourni en référence.

## Correspondances utilisées avec les colonnes existantes

Le calcul des indicateurs réutilise les formules déjà présentes dans votre document
plutôt que de les recalculer indépendamment, afin de rester cohérent avec le
paramétrage de `Table_locaux_types_et_correspondance` :

| Indicateur du PDF de référence      | Source dans Grist                                                        |
|--------------------------------------|---------------------------------------------------------------------------|
| Nombre de postes de travail           | Somme de `BDD_Salles.Nb_de_postes_de_travail` pour le bâtiment            |
| Capacité d'accueil                    | `BDD_Batiments.Effectif`                                                   |
| SUN par niveau / total                | Somme de `BDD_Etages.Surface_SUN_m2_`                                      |
| SUB par niveau / total                | Somme de `BDD_Etages.Surface_SUB_m2_`                                      |
| SPC par niveau / total                | Somme de `BDD_Etages.Surface_SP_m2_`                                       |
| SHON par niveau / total               | Somme de `BDD_Etages.Surface_SHON_m2_` (saisie manuelle par étage)         |
| SHOB par niveau / total               | Somme de `BDD_Etages.Surface_SHOB_m2_2` (formule, cohérente avec SUN/SUB/SPC) |
| Surfaces fonctionnelles (Administration, Enseignement, …) | `BDD_Salles` groupées par `Occupation`, filtrées sur `Type_d_usage.SUB = vrai` |
| Répartition par catégorie de local    | `BDD_Salles` groupées par `Type_d_usage.CategorieSurface`                  |

Les cibles affichées sur les indicateurs (SUN/poste ≥ 12 m², SUN/SUB > 67 %,
SUB/SPC > 85 %) sont indicatives (codes couleur vert/orange/rouge) et reprennent
les mêmes seuils que le document de référence ; ajustez les seuils dans le script
(`renderKpis`) si vos cibles internes diffèrent.

## Point de vigilance repéré dans le fichier `.grist` fourni

En analysant le fichier `Bac à sable SIPI.grist` transmis pour la maquette, une
incohérence a été repérée dans `BDD_Etages` : plusieurs lignes d'étages ont leur
colonne `Bâtiment` pointant vers le bâtiment "Bâtiment A" (id 1), alors que leurs
champs calculés `Nom_complet` / `Numéro bâtiment` affichent encore "Bâtiment
Enseignement" / 601. Cela peut indiquer une ligne d'étage réaffectée par erreur au
mauvais bâtiment, ou un cache de formule pas encore recalculé. Il est recommandé
de vérifier ces lignes dans `BDD_Etages` avant de faire confiance aux totaux par
bâtiment, sans quoi certains étages d'un bâtiment "voisin" pourraient se retrouver
comptés dans un autre. Ce point n'a pas été corrigé automatiquement : il s'agit
d'une donnée métier que seul vous pouvez trancher.

## Développement / modification

Le widget est un unique fichier HTML autonome (`index.html`), sans étape de build :
toute modification du fichier est immédiatement effective une fois publiée sur
GitHub Pages. Les bibliothèques externes (API Grist, Chart.js) sont chargées depuis
un CDN, il n'y a rien à installer localement pour l'éditer.

Pour tester localement avant de pousser :

```bash
cd dashboard-batiment
python3 -m http.server 8590
```

puis, dans Grist, ajoutez un widget avec l'URL `http://localhost:8590/index.html`
(cela ne fonctionne que si votre instance Grist et votre navigateur peuvent
atteindre `localhost:8590`, ce qui est le cas pour grist.getgrist.com ouvert
depuis le même poste).
