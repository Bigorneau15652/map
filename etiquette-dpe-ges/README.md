# Étiquette DPE / GES

Widget Grist autonome (un seul fichier `index.html`, pas de build) qui reproduit
l'étiquette « Performance énergétique et climatique » du Diagnostic de Performance
Énergétique (DPE) : l'étiquette énergie (A à G, consommation d'énergie primaire) et
l'étiquette gaz à effet de serre (A à G, émissions de GES), alignées côte à côte à la
même taille (classe A en face de classe A, fin de la barre G alignée avec la fin de la
barre G), avec la classe active mise en évidence sur chaque échelle.

## Fonctionnement

Le widget est lié à une table via le panneau **Colonnes** de Grist (comme n'importe
quel widget custom classique — pas besoin de « Full document access ») et affiche la
ligne actuellement sélectionnée. Deux colonnes sont à mapper :

- **Consommation énergie primaire (kWh/m²/an)**
- **Émissions de GES (kg CO2eq/m²/an)**

À partir de ces deux valeurs, le widget calcule la classe (A à G) sur chacune des deux
échelles et affiche l'étiquette correspondante, avec la classe active mise en
évidence (encart avec la valeur, barre agrandie), comme sur l'étiquette DPE papier.

## Installation dans Grist

1. Ouvrez votre document Grist.
2. Ajoutez un widget : **Add New → Add Widget to Page**, choisissez **Custom** puis
   **Custom URL**, et collez :

   ```
   https://bigorneau15652.github.io/map/etiquette-dpe-ges/index.html
   ```

3. Sélectionnez la table à utiliser.
4. Dans le panneau de droite, onglet **Colonnes**, associez :
   - `Consommation` → votre colonne de consommation d'énergie primaire (kWh/m²/an)
   - `Emissions` → votre colonne d'émissions de GES (kg CO2eq/m²/an)
5. Le widget affiche l'étiquette pour la ligne actuellement sélectionnée dans la
   table liée (curseur Grist).

Si les colonnes ne sont pas encore mappées, ou si la ligne sélectionnée n'a pas de
valeur numérique dans les colonnes choisies, un bandeau rouge explicite l'indique
(quoi faire, où aller) plutôt que d'afficher une étiquette vide ou une erreur.

## Seuils des classes (A à G), entièrement configurables

Bouton **⚙ Seuils des classes** dans la barre d'outils (également accessible depuis
l'icône de configuration du panneau Grist) : ouvre un panneau avec, pour chaque
échelle (énergie et GES), les 6 seuils de passage d'une classe à l'autre (A≤, B≤, C≤,
D≤, E≤, F≤ — la classe G s'applique au-delà du seuil F).

Les valeurs préremplies sont le barème réglementaire du DPE résidentiel en vigueur
depuis juillet 2021 :

| Classe | Énergie primaire (kWh/m²/an) | GES (kg CO2eq/m²/an) |
|--------|-------------------------------|------------------------|
| A      | ≤ 70                          | ≤ 6                    |
| B      | ≤ 110                         | ≤ 11                   |
| C      | ≤ 180                         | ≤ 30                   |
| D      | ≤ 250                         | ≤ 50                   |
| E      | ≤ 330                         | ≤ 70                   |
| F      | ≤ 420                         | ≤ 100                  |
| G      | > 420                         | > 100                  |

Ces seuils sont **entièrement modifiables** (autre réglementation, DPE tertiaire,
seuils internes propres à votre patrimoine, etc.) : vérifiez qu'ils correspondent
bien à votre cas d'usage avant de vous y fier. Un contrôle de saisie empêche
d'enregistrer des seuils non strictement croissants. Les seuils sont mémorisés avec
le widget (`grist.setOption`), donc persistants — ils survivent à un rafraîchissement
de la page ou à la réouverture du document, et sont propres à chaque instance du
widget (vous pouvez donc avoir des seuils différents sur deux vues différentes du
même document, par exemple résidentiel vs tertiaire).

## Développement / test local

Fichier HTML autonome, sans étape de build : toute modification est immédiatement
effective une fois publiée sur GitHub Pages.

Pour tester localement sans document Grist réel, un mock minimal de l'API Grist
(`mock-grist.js`) est fourni :

```bash
cd etiquette-dpe-ges
python3 -m http.server 8590
```

puis ouvrez `http://localhost:8590/index.html?demo=1` (valeurs de démo par défaut :
271 kWh/m²/an, classe E, comme l'étiquette de référence). Vous pouvez piloter les
valeurs de démo par l'URL :

- `?demo=1&cons=150&ges=20` — teste une autre classe (ici C)
- `?demo=1&empty=1` — teste le bandeau « colonnes non configurées »

Pour tester avec un vrai document Grist, ajoutez un widget avec l'URL
`http://localhost:8590/index.html` (fonctionne si votre instance Grist et votre
navigateur peuvent atteindre `localhost:8590`, ce qui est le cas pour
grist.getgrist.com ouvert depuis le même poste).

Avant de livrer un changement visuel, voir aussi `/CLAUDE.md` à la racine du dépôt
(bannières toujours lisibles, contraste des champs de formulaire en dark mode, pas de
`position: sticky`, test à largeur de panneau étroite).
