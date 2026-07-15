# Suivi consommation d'eau UMPV → Grist

Ce dossier alimente **votre document Grist existant** (`REPORT__EAU`, sur
`grist.numerique.gouv.fr`, org `dpmi-umpv`) avec une nouvelle table
`Releves_Journaliers` à maille journalière, en complément de la table
`Consommations` déjà en place (saisie manuelle, maille semestrielle, avec
coût en €). On ne remplace rien de ce qui existe.

| Site | Fournisseur | Portail | État de l'import auto |
|---|---|---|---|
| Béziers | SUEZ | toutsurmoneau.fr | ✅ en place (`import_suez_beziers.py`) |
| Route de Mende | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ en cours (reconnaissance) |
| Boutonnet | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ en cours |
| Saint-Charles | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ en cours |
| Saint-Louis | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ en cours |
| Du Guesclin | ? | ? | ⚠️ présent dans `Consommations` mais jamais mentionné à date — à clarifier |

⚠️ Ce sont des portails **eau**, pas énergie : les données importées sont des
volumes d'eau (litres/m³), pas de l'électricité ni du gaz.

## Principe

Ni SUEZ ni la Régie des Eaux 3M n'exposent d'API publique officielle pour les
particuliers/professionnels : ce sont leurs sites web "espace client" qui sont
interrogés (accès non officiel, "meilleur effort" — le site peut changer et
casser l'import, ce n'est pas garanti contractuellement). Les scripts ne font
que relire vos propres données de consommation.

`Releves_Journaliers` reprend volontairement les **mêmes conventions de
colonnes** que votre table `Consommations` existante (`Site` et `Nom_du_CPT`
en simples colonnes Choice — pas de table de référence séparée), pour rester
cohérent avec ce que vous avez déjà et pouvoir comparer facilement les deux.
Voir `ajout-releves-journaliers.xlsx` dans ce dossier pour le fichier à
importer dans votre document existant (onglet "Lisez-moi" = instructions
détaillées).

L'automatisation tourne sur **GitHub Actions**, gratuitement (quota très
largement suffisant pour un import nocturne de quelques secondes par site).
Aucun n8n, aucun serveur à louer.

## Béziers (SUEZ) — en place

Utilise la librairie open source [`toutsurmoneau`](https://github.com/laurent-martin/py-mon-eau)
(la même que l'intégration Home Assistant "Suez Water").

### 1. Ajouter la table à votre document Grist

Importez `ajout-releves-journaliers.xlsx` **dans le document existant**
(pas un nouveau document) — voir son onglet "Lisez-moi" pour la marche à
suivre exacte et les types de colonnes à régler après import. Vous devrez
notamment ajouter `"Beziers"` à la liste de choix de la colonne `Site`
(actuellement : Boutonnet, Du Guesclin, Route de Mende, Saint-Charles,
Saint-Louis).

### 2. Secrets GitHub à ajouter

**Settings → Secrets and variables → Actions → New repository secret** :

| Secret | Valeur |
|---|---|
| `SUEZ_USERNAME` | Identifiant toutsurmoneau.fr |
| `SUEZ_PASSWORD` | Mot de passe toutsurmoneau.fr |
| `GRIST_API_KEY` | Clé API Grist (avatar → *Paramètres du compte* → *API key*, sur grist.numerique.gouv.fr) |
| `GRIST_DOC_ID` | Id du document, dans l'URL `https://grist.numerique.gouv.fr/o/dpmi-umpv/<DOC_ID>/...` |
| `GRIST_TABLE_ID` | Id de la table de relevés (normalement `Releves_Journaliers`) |
| `GRIST_SERVER` | *(optionnel)* seulement si différent de `https://grist.numerique.gouv.fr` (déjà la valeur par défaut du script) |
| `SUEZ_METER_ID` | *(optionnel)* seulement si le compte SUEZ a plusieurs compteurs |

Ne mettez **jamais** ces valeurs en clair dans le code : les secrets GitHub
Actions sont chiffrés et jamais affichés dans les logs, ni récupérables par
qui que ce soit après coup (voir aussi la question de la visibilité du dépôt
plus bas).

### 3. Lancer

Le workflow `.github/workflows/eau-umpv-import.yml` tourne chaque nuit à
5h17 UTC (job `import-beziers`), et peut être lancé manuellement depuis
l'onglet **Actions** → *Import UMPV water consumption into Grist* → *Run
workflow*. Il réimporte les 40 derniers jours à chaque fois et **met à jour**
les lignes existantes au lieu d'en créer des doublons (upsert sur
`Date`+`Nom_du_CPT`) — utile car SUEZ publie parfois en retard.

## Route de Mende / Boutonnet / Saint-Charles / Saint-Louis (Régie des Eaux 3M) — en cours

Contrairement à SUEZ, il n'existe **aucune librairie ou intégration Home
Assistant connue** pour `ael.regiedeseaux3m.fr` — impossible de réutiliser du
code existant. Écrire un scraper fiable demande de connaître exactement les
requêtes que le site envoie pour se connecter et afficher l'historique, et
l'environnement dans lequel ces scripts sont préparés n'a pas accès à ce site
(politique réseau restreinte à quelques domaines connus) : impossible de
l'inspecter directement d'ici.

**Approche retenue : itération via les logs GitHub Actions.** Un premier
script `discover_regie3m.py` est déjà en place : il pilote un vrai navigateur
(Playwright) pour se connecter, tente de repérer les champs identifiant/mot
de passe et le bouton de connexion par plusieurs heuristiques (type de champ,
libellé, placeholder), essaie de cliquer sur un lien "consommation /
historique", et surtout **capture tous les appels d'API JSON** vus pendant la
session (URL, méthode, statut, extrait du corps de réponse) — c'est ça qui va
révéler la vraie structure du site. À chaque étape il continue même en cas
d'échec partiel pour maximiser les diagnostics récupérés (captures d'écran +
HTML + `api-calls.json` + `log.txt`).

Sa mécanique (détection de champs, soumission, capture réseau, navigation par
texte) a été testée contre une fausse page de connexion locale avant d'être
committée — ce qui n'a pas pu être vérifié, faute d'accès au vrai site
d'ici, ce sont les sélecteurs/libellés réels d'`ael.regiedeseaux3m.fr`.

### Mise en place

1. Ajoutez les secrets `REGIE3M_USERNAME` / `REGIE3M_PASSWORD` dans le dépôt
   (**Settings → Secrets and variables → Actions**).
2. Lancez le workflow **Regie 3M portal discovery (manual, diagnostic
   only)** depuis l'onglet **Actions** (déclenchement manuel uniquement,
   jamais planifié — pas de raison de retenter un login automatiquement tant
   que le scraper n'est pas fini).
3. Une fois le run terminé, il produit un artefact `regie3m-discover-output`
   (captures d'écran avant/après connexion, HTML de la page, et surtout
   `api-calls.json`) que je récupère et lis pour écrire l'extraction réelle
   des données — remplaçant les heuristiques génériques de
   `discover_regie3m.py` par le vrai endpoint de consommation.
4. Cela prendra probablement 2 à 4 allers-retours (relance après chaque
   correctif), chacun avec votre feu vert avant de relancer puisque ça
   utilise vos vrais identifiants.

Une fois fonctionnel, le script rejoindra le même workflow
`eau-umpv-import.yml` (un job `import-regie3m` par site, ou un seul job qui
boucle sur les 4 sites x leurs compteurs), avec la même politique d'upsert
dans `Releves_Journaliers`, en réutilisant les colonnes `Site`/`Nom_du_CPT`
déjà en place.

### Fréquence de récupération automatique

- **Béziers (SUEZ)** : nocturne (déjà en place). Inutile d'interroger plus
  souvent — SUEZ ne publie qu'une valeur par jour, parfois avec 1-2 jours de
  retard (compensé par la fenêtre de réimport de 40 jours).
- **Régie des Eaux 3M** : dépendra de ce que le portail publie réellement. Le
  fait que `Consommations` soit aujourd'hui alimentée à la main, deux fois
  par an, via un formulaire, suggère que la Régie 3M ne fournit peut-être pas
  de relevé en libre-service à maille fine — mais je ne le saurai qu'après
  la reconnaissance du portail (ci-dessus). Si c'est le cas, on restera sur
  un import nocturne comme Béziers ; si les compteurs sont télérelevés
  (historique horaire), on pourra viser plus fin. Dans tous les cas, "quasi
  temps réel" n'est pas réaliste avec ce genre de portail web (pas de
  webhook, pas de flux poussé) : on reste sur du interrogation périodique
  (polling), gratuit.

## Tester en local (optionnel)

Nécessite **Python 3.12 ou plus récent** (la librairie `toutsurmoneau` 0.0.27
contient une syntaxe qui ne fonctionne pas sur Python 3.11 et antérieur).

```bash
cd eau-umpv-import
pip install -r requirements.txt
export SUEZ_USERNAME=... SUEZ_PASSWORD=...
export GRIST_API_KEY=... GRIST_DOC_ID=... GRIST_TABLE_ID=...
python import_suez_beziers.py
```
