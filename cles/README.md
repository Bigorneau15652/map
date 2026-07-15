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
| après `Materiaux` | `Cle_TypeCle` | Type de clé | Choice (SP1, SP2, SP3, SP (G02642), 303, SURF, VIP St Charles, Atrium - ALPHA, Atrium - SERIAL XP, Béziers, …) | Système de clé qui ouvre cette porte |
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

## 2. Nomenclature des clés — `Nomenclature_cles.xlsx`

Les fichiers XLSX fournis (exports du logiciel du serrurier, un fichier
par système de clé ou par chantier) sont des mises en page d'impression :
en-têtes de page/chantier répétés toutes les ~46 lignes, cellules
fusionnées sur plusieurs colonnes, pages d'historique de commandes et de
signatures mêlées aux données. Ils ont été reconstitués en tableaux
exploitables. Avec le fichier `303_2028_D02028.xlsx` (7 onglets), **les 7
types de clé actuellement suivis dans `Organigramme_Cles` sont maintenant
tous couverts** : SP1, SP2, SP3, SP (G02642), 303, SURF, VIP St Charles.

Le classeur `Nomenclature_cles.xlsx` contient :
- **Synthèse** : totaux par système/combinaison, avec le nombre de lignes
  déjà présentes dans `Organigramme_Cles` et le nombre de lignes trouvées
  dans le fichier source mais absentes de Grist.
- **SP1 / SP2 / SP3 / SP_G02642 / 303 / SURF** : format CISA SP (désignation
  locale, repère porte, n° de variure, nb de clés, référence cylindre,
  type O/V, longueur en mm, passes). `303` regroupe les deux combinaisons
  trouvées dans le fichier : `D02028` (onglet "Table 1") et `D02066`
  (onglet "Feuil1", ~2000 lignes, sans étiquette de combinaison visible
  mais dont le contenu correspond à 99.9% à ce qui est déjà importé sous
  `D02066` — c'est donc bien la même combinaison).
- **VIP_St_Charles** : format Vachette VIP, différent du format CISA SP
  (colonnes Ligne/Fonct/Qté/Désignation produit/Numérotation/Variure/Lot/
  Repère/Désignation locale). Combine les onglets `SC1` (plan 598331),
  `SC2` (plan 598331-ext) et `SC2-2` (un bon de commande du 12/09/2017,
  plan 598331, qui corrige/complète certaines portes — colonne "Onglet
  source" pour distinguer). Le rapprochement avec Grist se fait sur le
  n° de variure plutôt que sur la référence cylindre, car cette dernière
  est parfois tronquée dans les données déjà importées.
- **Bât_L_recles_2017** : table à part trouvée dans le même fichier,
  hors format nomenclature — voir section 4.

Les lignes surlignées en jaune ne sont pas encore dans `Organigramme_Cles`.

Écart constaté avec le contenu actuel de `Organigramme_Cles` :

| Type de clé | Combinaison | Lignes reconstituées | Déjà dans Grist | À ajouter |
|---|---|---|---|---|
| SP1 | G01214 | 408 | 389 | **19** |
| SP2 | G01623 | 523 | 522 | **1** |
| SP3 | G04883 | 144 | 144 | 0 |
| SP (G02642) | G02642 | 5 | 5 | 0 |
| 303 | D02028 | 61 | 61 | 0 |
| 303 | D02066 | 1185 | 1103 | **82** |
| SURF | V00812 | 116 | 116 | 0 |
| VIP St Charles | 598331 | 263 | 256 | **7** |
| VIP St Charles | 598331-ext | 127 | 127 | 0 |

Les 19 lignes SP1 manquantes correspondent à une plage contiguë de portes
(repères 130 à 139 et 173 à 176, plus la porte 5) — probablement une page
du document source qui n'avait pas été importée à l'origine. Les 82 lignes
303/D02066 et les 7 lignes VIP St Charles manquantes suivent le même
constat : identifiables directement dans les onglets correspondants (fond
jaune, colonne "Statut dans Grist").

## 3. Bât L — reclé Agence Comptable (2017)

L'onglet `Bât L` n'est pas une nomenclature mais une table de suivi de
chantier : remplacement de barillets pour l'agence comptable du bâtiment
L (R+2), daté du 24/01/2017. Elle liste, porte par porte, l'ancien
barillet (référençant les anciens systèmes SP2/303) et son remplaçant.
**Le nouveau système de barillet s'appelle `K070258`** et n'existe dans
aucun des 7 types de clé actuellement suivis dans `Organigramme_Cles` —
si ces portes du bâtiment L ont bien été recléées, la référence à utiliser
pour elles n'est plus celle de `Organigramme_Cles` mais celle de cet
onglet `Bât_L_recles_2017`. À vérifier avec vous si ce chantier a été
généralisé à d'autres salles/bâtiments, auquel cas il faudrait
probablement créer un 8ᵉ type de clé.

## 4. Atrium (BRICARD, site Route de Mende)

Nouveau bâtiment (`Bâtiment ATRIUM`, id 66, site Route de Mende) : aucune
ligne encore dans `Organigramme_Cles`. Les 2 fichiers `.xlsm` fournis ne
sont **pas** un brouillon et sa version finale d'un même organigramme,
mais **deux systèmes de clé distincts et complémentaires** pour le même
bâtiment (confirmé par le contenu des fichiers : gammes de cylindre,
numéros de schéma et portes couvertes totalement différents) :
- `Atrium_ALPHA` : organigramme **non protégé** (passe général courant),
  gamme BRICARD ALPHA, n° de schéma 2MN92B, 150 portes/cylindres.
- `Atrium_SerialXP` : organigramme **protégé** (zones sensibles), gamme
  BRICARD SERIAL XP, n° de schéma "CREATION T57J", 66 portes/cylindres.

Ces deux fichiers Excel sont natifs (pas d'impression/scan), donc fiables
à 100% — pas de risque de mauvaise lecture.

Comme il s'agit d'un nouveau bâtiment, il faudra un (ou deux) nouveau(x)
`Type_de_cle` dans `Organigramme_Cles` — proposition : `Atrium - ALPHA`
et `Atrium - SERIAL XP`.

## 5. Béziers (BRICARD, PDF scanné)

Nouveau site (`Béziers`, id 2) : aucune ligne encore dans
`Organigramme_Cles`. **Le PDF est lisible** : ce n'est pas un document de
150 pages mais un scan/fax de **11 pages** (le compteur de pages annoncé
par l'outil comptait autre chose — la lecture réelle du fichier en donne
11). Il combine plusieurs documents de nature différente :

- **Pages 1-2** : un inventaire simple et propre, **imprimé** (référence
  de clé / localisation / nombre de clés), sans la référence technique du
  cylindre. Entièrement fiable — transcrit dans l'onglet
  `Beziers_Inventaire` (108 lignes).
- **Pages 3-11** : plusieurs fax de schémas de combinaison BRICARD
  officiels (« Schéma de combinaison »), datés de 1998 à 2005, provenant
  de plusieurs agences BRICARD (Montpellier, Toulouse) — ce sont ces
  pages qui donnent la référence technique du cylindre (colonne REF.).
  Certaines sont **imprimées** (fiables à 100%), d'autres **entièrement
  manuscrites** (risque réel de mauvaise lecture d'un chiffre, ce qui est
  sensible pour une référence de sécurité physique).

Par prudence, `Beziers_REF_cylindres` ne contient que les **10 lignes
retrouvées sur des pages imprimées** (schéma AJC7, marquages RC01-RC07 et
80/81/82, référence cylindre "2 330 071" / "2 333 071"). Les pages
manuscrites restantes (schémas AJE9 et VA37D, plus un bâtiment
« extension » distinct daté de 1998 signé HARTIMASSO) contiennent
d'autres références cylindre pour le reste de l'inventaire (les portes
`LT01` à `LT22`, les bureaux, etc.) mais n'ont pas été retranscrites ici.

**Comment voulez-vous procéder pour ces pages manuscrites ?**
- je fais une transcription "au mieux" avec une colonne "à vérifier" pour
  chaque valeur lue sur une page manuscrite (rapide, mais vous devrez
  recontrôler ces valeurs avant tout usage) ;
- ou vous les ressaisissez vous-même à partir des pages scannées (plus
  sûr, mais plus de travail de votre côté) — vous pouvez me dire quelles
  pages précisément si vous préférez ne resaisir qu'une partie.

## 6. Suite

Les 7 types de clé déjà suivis dans `Organigramme_Cles`, plus les 2
systèmes Atrium et l'inventaire Béziers, sont désormais couverts. Reste
en attente : la transcription fiable des pages manuscrites du PDF
Béziers (voir section 5), et la confirmation du chantier de reclé du
bâtiment L (voir section 3 : sera-t-il généralisé, auquel cas il faudra
un 8ᵉ type de clé "K070258" ?).
