# Volet clés — SI Patrimoine

Notes de travail pour le futur module "clés" du Grist SI Patrimoine :
proposition de colonne(s) sur `BDD_Portes` pour porter la référence du
cylindre (barillet), et nomenclature des clés SP reconstituée en XLSX.

## 1. Colonnes proposées sur `BDD_Portes`

`BDD_Portes` et `Organigramme_Cles` (la table qui contient déjà 2729 lignes
de nomenclature de clés, colonnes `Cyl_REF`, `Cyl_Type_OV`, `Cyl_LG_mm`,
`Passes`, etc.) n'ont **aucune clé commune aujourd'hui** : `BDD_Portes.Nom`
est construit à partir des identifiants de salles (ex.
`Ci001/Ci002_1`), alors que `Organigramme_Cles.Repere_porte` reprend la
numérotation propre au serrurier (ex. `001`, `1A1-1`, `300A1`, `A1`,
`S08`...), qui ne recoupe ni les noms de salle ni les noms de porte du
Grist. Un simple lookup automatique par le nom n'est donc pas possible :
il faut une colonne de correspondance en plus de la colonne d'affichage.

Proposition : **3 colonnes**, insérées entre `Materiaux` et `Commentaire`
(elles complètent la description physique de la porte avant le champ de
commentaire libre) :

| Ordre | colId | Label | Type | Rôle |
|---|---|---|---|---|
| après `Materiaux` | `Cle_TypeCle` | Type de clé | Choice (SP1, SP2, SP3, SP (G02642), 303, SURF, VIP St Charles, …) | Système de clé qui ouvre cette porte |
| | `Cle_RepereOrganigramme` | Repère porte (organigramme clés) | Text | Le repère du serrurier pour cette porte — à saisir une fois lors du rapprochement terrain, sert de clé de rapprochement |
| | `ReferenceCylindre` | Référence cylindre (barillet) | Formula (Any) | `=Organigramme_Cles.lookupOne(Type_de_cle=$Cle_TypeCle, Repere_porte=$Cle_RepereOrganigramme).Cyl_REF` — se remplit automatiquement dès que les deux colonnes précédentes sont saisies |

`ReferenceCylindre` peut être complétée par 1-2 formules sœurs si utile
(`Cyl_Type_OV`, `Cyl_LG_mm`) en reprenant le même `lookupOne`.

Concrètement : `Cle_TypeCle` + `Cle_RepereOrganigramme` sont à saisir une
fois par porte (au clavier ou par import CSV si un tableau de
correspondance porte→repère existe déjà quelque part) ; `ReferenceCylindre`
se déduit ensuite tout seul, sans double-saisie de la référence.

Si vous préférez ne pas exposer les 2 colonnes techniques (par ex. pour ne
pas surcharger la vue par défaut), elles peuvent être ajoutées normalement
puis masquées dans les vues où elles ne sont pas utiles — Grist affiche
les colonnes masquées par vue, pas par table.

## 2. Nomenclature des clés SP — `Nomenclature_cles_SP.xlsx`

Les 4 fichiers XLSX fournis (exports du logiciel du serrurier, un fichier
par système SP) sont des mises en page d'impression : en-têtes de
page/chantier répétés toutes les ~46 lignes, cellules fusionnées sur
plusieurs colonnes, pages d'historique de commandes et de signatures
mêlées aux données. Ils ont été reconstitués en tableaux exploitables.

Le classeur `Nomenclature_cles_SP.xlsx` contient :
- **Synthèse** : totaux par système de clé, avec le nombre de lignes déjà
  présentes dans `Organigramme_Cles` et le nombre de lignes trouvées dans
  le fichier source mais absentes de Grist.
- **SP1 / SP2 / SP3 / SP_G02642** : une ligne par porte/cylindre
  (désignation locale, repère porte, n° de variure, nb de clés, référence
  cylindre, type O/V, longueur en mm, passes). Les lignes surlignées en
  jaune ne sont pas encore dans `Organigramme_Cles`.

Écart constaté avec le contenu actuel de `Organigramme_Cles` :

| Type de clé | Lignes reconstituées | Déjà dans Grist | À ajouter |
|---|---|---|---|
| SP1 | 408 | 389 | **19** |
| SP2 | 523 | 522 | **1** |
| SP3 | 144 | 144 | 0 |
| SP (G02642) | 5 | 5 | 0 |

Les 19 lignes SP1 manquantes correspondent à une plage contiguë de portes
(repères 130 à 139 et 173 à 176, plus la porte 5) — probablement une page
du document source qui n'avait pas été importée à l'origine. Elles sont
identifiables directement dans l'onglet SP1 (fond jaune, colonne "Statut
dans Grist").

## 3. Suite

Les autres nomenclatures de clés (303, SURF, VIP St Charles — déjà
partiellement présentes dans `Organigramme_Cles`, 303 avec 1156 lignes,
SURF 116, VIP St Charles 402) pourront être passées par la même méthode
dès que les fichiers XLSX correspondants seront fournis.
