# Import automatique des consommations d'eau SUEZ → Grist

⚠️ **Précision importante** : toutsurmoneau.fr est le portail **eau** de SUEZ
(relevés de compteur d'eau), pas un fournisseur d'énergie. Ce dossier importe
donc des consommations d'**eau** (litres / m³), pas d'électricité ni de gaz.

## Principe

SUEZ n'expose pas d'API publique officielle pour les particuliers. Ce script
utilise la librairie open source [`toutsurmoneau`](https://github.com/laurent-martin/py-mon-eau)
(la même que celle utilisée par l'intégration Home Assistant "Suez Water")
pour se connecter à votre espace client et récupérer l'historique de
consommation jour par jour, puis pousse ces valeurs dans une table Grist via
l'API REST de Grist.

L'automatisation tourne sur **GitHub Actions**, gratuitement (le quota
gratuit — 2 000 minutes/mois sur dépôt privé, illimité sur dépôt public — est
très largement suffisant pour une exécution quotidienne de quelques
secondes). Aucun n8n, aucun serveur à louer.

Comme c'est un accès non officiel (scraping du site web), gardez en tête que
**SUEZ peut changer son site à tout moment et casser l'import** — c'est du
"meilleur effort", pas une garantie contractuelle. Il s'agit uniquement de
relire vos propres données de consommation, pour votre usage personnel.

## Mise en place (une seule fois)

### 1. Créer la table dans Grist

Dans votre document Grist, créez (ou choisissez) une table avec au moins ces
3 colonnes :

| Nom de colonne | Type Grist |
|---|---|
| `Date`         | Date |
| `Volume_L`     | Numérique (entier) — consommation du jour, en litres |
| `Index_m3`     | Numérique — relevé cumulé du compteur ce jour-là, en m³ |

Notez l'**id machine** de la table (Clic droit sur l'onglet de la table →
*Renommer la table* affiche le nom technique, ou regardez dans le panneau
"Code View" / l'URL de l'API). Par défaut Grist nomme la première table
`Table1`.

### 2. Récupérer vos identifiants Grist

- **Clé API** : cliquez sur votre avatar (en haut à droite dans Grist) →
  *Paramètres du compte* → *API key* → *Créer une clé*.
- **Doc ID** : dans l'URL de votre document,
  `https://docs.getgrist.com/<DOC_ID>/Nom-du-doc`, la partie `<DOC_ID>`.
- **Serveur** : si vous utilisez `docs.getgrist.com` (l'offre gratuite SaaS),
  vous n'avez rien à configurer. Si votre Grist est auto-hébergé, notez son
  URL de base (ex: `https://grist.mondomaine.fr`).

### 3. Ajouter les secrets dans le dépôt GitHub

Dans ce dépôt GitHub : **Settings → Secrets and variables → Actions → New
repository secret**, ajoutez :

| Nom du secret | Valeur |
|---|---|
| `SUEZ_USERNAME` | Votre identifiant de connexion toutsurmoneau.fr |
| `SUEZ_PASSWORD` | Votre mot de passe toutsurmoneau.fr |
| `GRIST_API_KEY` | La clé API créée à l'étape 2 |
| `GRIST_DOC_ID` | L'id du document Grist |
| `GRIST_TABLE_ID` | L'id de la table (ex: `Table1`) |
| `GRIST_SERVER` | *(optionnel)* seulement si Grist auto-hébergé |
| `SUEZ_METER_ID` | *(optionnel)* seulement si votre compte a plusieurs compteurs — le script vous le dira en cas d'erreur |

Ne mettez **jamais** ces valeurs en clair dans le code ou dans un widget : les
secrets GitHub Actions sont chiffrés et ne sont jamais affichés dans les
logs.

### 4. Lancer

Le workflow `.github/workflows/suez-import.yml` tourne automatiquement
chaque nuit à 5h17 UTC. Vous pouvez aussi le lancer manuellement : onglet
**Actions** du dépôt → *Import SUEZ water consumption into Grist* → *Run
workflow*.

À chaque exécution, il réimporte les 40 derniers jours (réglable via le
secret/variable `LOOKBACK_DAYS`) et **met à jour** les lignes existantes au
lieu d'en créer des doublons (upsert sur la colonne `Date`) — utile car SUEZ
publie parfois les relevés avec un ou deux jours de retard.

## Tester en local (optionnel)

Nécessite **Python 3.12 ou plus récent** (la librairie `toutsurmoneau` 0.0.27
contient une syntaxe qui ne fonctionne pas sur Python 3.11 et antérieur).

```bash
pip install -r requirements.txt
export SUEZ_USERNAME=... SUEZ_PASSWORD=...
export GRIST_API_KEY=... GRIST_DOC_ID=... GRIST_TABLE_ID=...
python import_suez.py
```
