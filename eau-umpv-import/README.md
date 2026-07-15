# Suivi consommation d'eau UMPV (5 sites) → Grist

5 sites, 2 fournisseurs d'eau, un seul document Grist :

| Site | Fournisseur | Portail | État de l'import auto |
|---|---|---|---|
| Béziers | SUEZ | toutsurmoneau.fr | ✅ en place (`import_suez_beziers.py`) |
| Route de Mende | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ à construire, voir plus bas |
| Boutonnet | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ à construire |
| Saint-Charles | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ à construire |
| Saint-Louis | Régie des Eaux 3M | ael.regiedeseaux3m.fr | ⏳ à construire |

⚠️ Ce sont des portails **eau**, pas énergie : les données importées sont des
volumes d'eau (litres/m³), pas de l'électricité ni du gaz.

## Principe

Ni SUEZ ni la Régie des Eaux 3M n'exposent d'API publique officielle pour les
particuliers/professionnels : ce sont leurs sites web "espace client" qui sont
interrogés (accès non officiel, "meilleur effort" — le site peut changer et
casser l'import, ce n'est pas garanti contractuellement). Les scripts ne font
que relire vos propres données de consommation.

Chaque site pousse ses relevés quotidiens dans **une seule table Grist
partagée** (`Releves_Journaliers`), avec des colonnes `Site` et `Compteur_ID`
pour pouvoir tout comparer (par site, par mois, d'une année sur l'autre) sans
avoir 5 documents séparés. Voir `grist-eau-umpv-template.xlsx` dans ce
dossier pour un modèle prêt à importer dans Grist (structure des tables,
détails dans le premier onglet "Lisez-moi" du fichier).

L'automatisation tourne sur **GitHub Actions**, gratuitement (quota très
largement suffisant pour un import nocturne de quelques secondes par site).
Aucun n8n, aucun serveur à louer.

## Béziers (SUEZ) — en place

Utilise la librairie open source [`toutsurmoneau`](https://github.com/laurent-martin/py-mon-eau)
(la même que l'intégration Home Assistant "Suez Water").

### 1. Table Grist

Utilisez la table `Releves_Journaliers` du modèle XLSX fourni (colonnes
`Date`, `Compteur_ID`, `Site`, `Source`, `Volume_L`, `Index_m3`).

### 2. Secrets GitHub à ajouter

**Settings → Secrets and variables → Actions → New repository secret** :

| Secret | Valeur |
|---|---|
| `SUEZ_USERNAME` | Identifiant toutsurmoneau.fr |
| `SUEZ_PASSWORD` | Mot de passe toutsurmoneau.fr |
| `GRIST_API_KEY` | Clé API Grist (avatar → *Paramètres du compte* → *API key*) |
| `GRIST_DOC_ID` | Id du document, dans l'URL `https://docs.getgrist.com/<DOC_ID>/...` |
| `GRIST_TABLE_ID` | Id de la table de relevés (ex: `Releves_Journaliers`) |
| `GRIST_SERVER` | *(optionnel)* seulement si Grist auto-hébergé |
| `SUEZ_METER_ID` | *(optionnel)* seulement si le compte a plusieurs compteurs |

Ne mettez **jamais** ces valeurs en clair dans le code : les secrets GitHub
Actions sont chiffrés et jamais affichés dans les logs.

### 3. Lancer

Le workflow `.github/workflows/eau-umpv-import.yml` tourne chaque nuit à
5h17 UTC (job `import-beziers`), et peut être lancé manuellement depuis
l'onglet **Actions** → *Import UMPV water consumption into Grist* → *Run
workflow*. Il réimporte les 40 derniers jours à chaque fois et **met à jour**
les lignes existantes au lieu d'en créer des doublons (upsert sur
`Date`+`Compteur_ID`) — utile car SUEZ publie parfois en retard.

## Route de Mende / Boutonnet / Saint-Charles / Saint-Louis (Régie des Eaux 3M) — à construire

Contrairement à SUEZ, il n'existe **aucune librairie ou intégration Home
Assistant connue** pour `ael.regiedeseaux3m.fr` — impossible de réutiliser du
code existant. Écrire un scraper fiable demande de connaître exactement les
requêtes que le site envoie pour se connecter et afficher l'historique, et
l'environnement dans lequel ces scripts sont préparés n'a pas accès à ce site
(politique réseau restreinte à quelques domaines connus) : impossible de
l'inspecter directement d'ici.

Deux façons de débloquer ça, au choix :

**A. Export HAR (le plus rapide, une seule itération)**
1. Connectez-vous à https://ael.regiedeseaux3m.fr/ dans Chrome/Firefox.
2. Ouvrez les outils développeur (F12) → onglet **Réseau/Network** → cochez
   "Preserve log".
3. Allez sur la page d'historique de consommation d'un compteur.
4. Clic droit dans la liste des requêtes → **Save all as HAR** (ou l'icône de
   téléchargement en haut de l'onglet Réseau).
5. Partagez ce fichier HAR (ou juste les requêtes vers des URLs contenant
   `login`, `conso`, `compteur`, `historique`, `api`) — **retirez/masquez
   votre mot de passe en clair s'il apparaît dans le corps d'une requête**,
   je n'ai besoin que des noms de champs et de la structure, pas de vos
   identifiants réels.

Avec ça, j'écris et livre un script `import_regie3m.py` directement
fonctionnel.

**B. Itération via les logs GitHub Actions (sans manipulation technique de votre côté)**
1. Ajoutez déjà les secrets `REGIE3M_USERNAME` / `REGIE3M_PASSWORD` dans le
   dépôt.
2. J'écris un scraper "meilleur effort" basé sur un navigateur automatisé
   (Playwright) qui reproduit un vrai login (remplit le formulaire, clique,
   navigue), puis je le fais tourner comme job GitHub Actions.
3. Je lis les logs d'exécution (échecs, sélecteurs introuvables) pour corriger
   et relancer, jusqu'à ce que ça fonctionne — compter 2 à 4 allers-retours,
   chacun demandant votre feu vert avant de relancer (car ça utilise vos
   vrais identifiants).

Une fois un des deux chemins choisi, le déploiement rejoindra le même
workflow `eau-umpv-import.yml` (un job `import-regie3m` par site ou un seul
job qui boucle sur les 4 sites x leurs compteurs), avec la même politique
d'upsert dans `Releves_Journaliers`.

### Fréquence de récupération automatique

- **Béziers (SUEZ)** : nocturne (déjà en place). Inutile d'interroger plus
  souvent — SUEZ ne publie qu'une valeur par jour, parfois avec 1-2 jours de
  retard (compensé par la fenêtre de réimport de 40 jours).
- **Régie des Eaux 3M** : dépendra de ce que le portail publie réellement.
  S'il s'agit de compteurs classiques (relevé manuel/périodique), ce sera
  probablement aussi une valeur par jour au mieux → import nocturne, comme
  Béziers. S'il s'agit de compteurs communicants ("télérelevés", avec un
  historique horaire), on pourra viser une fréquence plus fine — mais je ne
  peux le confirmer qu'une fois le portail inspecté (option A ou B ci-dessus).
  Dans tous les cas, "quasi temps réel" n'est pas réaliste avec ce genre de
  portail web (pas de webhook, pas de flux poussé) : on reste sur du
  interrogation périodique (polling), gratuit, au pire toutes les heures si
  la donnée elle-même est assez fine pour que ça vaille le coup.

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
