# Veille bâtiment durable et décarbonation

Veille mensuelle automatisée sur l'isolation, la thermique du bâtiment, l'énergie, les pompes à chaleur, les fluides frigorigènes, les chaudières et le chauffage, le DPE, le décret tertiaire, l'ADEME, les menuiseries, l'audit énergétique, le bilan carbone, la GTB et le financement.

Sources suivies : Kheox, Le Moniteur, les Cahiers Techniques du Bâtiment, complétés par Légifrance, l'ADEME et le ministère de la Transition écologique.

## Principe de fonctionnement

Le 5 de chaque mois, une session automatisée lit le périmètre de recherche dans le dépôt, effectue la veille, rédige une synthèse unique dédoublonnée et écrit deux fichiers dans le dossier veilles. Le commit de ces fichiers déclenche une GitHub Action qui publie le résultat dans un document Grist.

Le périmètre de recherche n'est pas écrit dans le code. Il est piloté depuis deux tables Grist, Veille_Themes et Veille_Sources, relues automatiquement le 4 de chaque mois. Pour élargir la veille à un nouveau thème ou à un nouveau site, il suffit d'ajouter une ligne dans Grist.

## Organisation du dépôt

Le dossier protocole contient la consigne de veille et le périmètre de recherche. Les fichiers themes.json et sources.json sont générés depuis Grist, les fichiers themes-defaut.json et sources-defaut.json servent d'amorçage initial.

Le dossier veilles contient les synthèses mensuelles, un fichier Markdown pour le texte et un fichier JSON pour la liste structurée des sujets.

Le dossier scripts contient le seul programme du projet, grist_sync.py, qui assure les échanges avec Grist dans les deux sens.

Le dossier grist contient la documentation de création des tables.

Le dossier .github/workflows contient les trois automatisations.

## Les trois automatisations

Le workflow Initialiser les tables de pilotage Grist se lance manuellement, une seule fois, pour remplir Veille_Themes et Veille_Sources avec les valeurs par défaut.

Le workflow Relire les tables de pilotage Grist se lance le 4 de chaque mois. Il relit vos deux tables de pilotage et met à jour le dépôt si vous les avez modifiées.

Le workflow Publier la veille dans Grist se lance à chaque ajout d'une synthèse dans le dossier veilles. Il écrit dans Veille_Syntheses et Veille_Articles.

## Secrets à renseigner dans le dépôt

Trois secrets sont nécessaires, à créer dans Settings, puis Secrets and variables, puis Actions.

GRIST_SERVER vaut https://grist.numerique.gouv.fr

GRIST_DOC_ID est l'identifiant du document Grist, lisible dans la barre d'adresse.

GRIST_API_KEY est la clé API du compte Grist, générée depuis les paramètres du profil.

Aucun identifiant d'abonnement de presse n'est utilisé, ni demandé, ni stocké.

## Envoi de la synthese par email

L envoi est facultatif. Il ne se declenche que si les secrets correspondants sont renseignes, sinon l etape est ignoree sans provoquer d erreur.

SMTP_SERVEUR est l adresse du serveur d envoi, par exemple le relais de l universite.

SMTP_PORT vaut 587 pour une connexion STARTTLS, 465 pour une connexion SSL. Valeur par defaut 587.

SMTP_UTILISATEUR et SMTP_MOT_DE_PASSE sont les identifiants de connexion au serveur. Avec une adresse Gmail, utiliser un mot de passe applicatif et non le mot de passe du compte.

EMAIL_EXPEDITEUR est l adresse affichee en expediteur, par defaut celle de SMTP_UTILISATEUR.

EMAIL_DESTINATAIRE est l adresse professionnelle qui recoit la synthese. Elle est conservee en secret du depot plutot que dans un fichier, afin de ne pas la faire figurer dans l historique de version.

## Méthode et limites

La veille est construite à partir des titres, des accroches et des références réglementaires publiquement indexés des sites suivis, complétés par les sources ouvertes. Le contenu intégral des articles sous abonnement n'est pas récupéré, ce qui serait contraire aux conditions d'utilisation des éditeurs. Les liens fournis permettent d'ouvrir l'article complet avec l'abonnement de l'université.

Les numéros et les dates de texte doivent être vérifiés sur Légifrance avant tout usage engageant.
