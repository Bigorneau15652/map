# Créer les quatre tables dans Grist

Ce document décrit pas à pas la création des tables dans votre document Grist sur grist.numerique.gouv.fr. Les termes utilisés sont ceux de l'interface française.

## Avant de commencer

Ouvrez ou créez le document Grist qui accueillera la veille. Notez son identifiant, qui se lit dans la barre d'adresse du navigateur. Dans une adresse de la forme grist.numerique.gouv.fr/o/docs/aBcDeFgHiJkL/Veille, l'identifiant du document est la suite de caractères aBcDeFgHiJkL, située juste avant le nom du document.

## Table 1, Veille_Syntheses

Cliquez sur Ajouter, puis sur Ajouter une table vide. Renommez la table en Veille_Syntheses, en respectant la majuscule et le tiret bas.

Créez les colonnes suivantes, en respectant exactement les noms.

Mois, de type Texte. C'est la colonne qui identifie chaque ligne, au format AAAA-MM.

Titre, de type Texte.

Periode, de type Texte. Sans accent sur le e, il s'agit d'un nom technique.

Date_publication, de type Texte, au format AAAA-MM-JJ. Le type Texte est volontaire, il évite les problèmes de conversion de date entre le script et Grist tout en conservant un tri chronologique correct.

Synthese, de type Texte. Dans le panneau de droite, sous Type de colonne, cochez la case qui autorise le texte sur plusieurs lignes. C'est la colonne qui contient le texte complet de la veille.

Nb_articles, de type Numérique.

## Table 2, Veille_Articles

Ajoutez une table vide et renommez-la Veille_Articles. Créez les colonnes suivantes.

Cle, de type Texte. Colonne technique de rapprochement, remplie automatiquement. Vous pouvez la masquer une fois la mise en service terminée.

Mois, de type Texte.

Titre, de type Texte.

Theme, de type Texte.

Date_article, de type Texte, au format AAAA-MM-JJ.

Resume, de type Texte, sur plusieurs lignes.

Sources, de type Texte.

Lien_article, de type Texte. Vous pouvez ensuite passer cette colonne en type Lien hypertexte pour la rendre cliquable.

Lien_reglementaire, de type Texte, également passable en Lien hypertexte.

Impact_UMPV, de type Texte, sur plusieurs lignes.

Priorite, de type Texte. Vous pouvez la passer en type Choix avec les valeurs Haute, Moyenne et Basse, ce qui permet un filtrage par couleur.

## Table 3, Veille_Themes

C'est la table de pilotage qui définit ce que la veille doit chercher. Ajoutez une table vide et renommez-la Veille_Themes. Créez les colonnes suivantes.

Theme, de type Texte. C'est la colonne qui identifie chaque ligne.

Mots_cles, de type Texte. La liste des mots clés associés au thème, séparés par des virgules. Plus la liste est précise, meilleure est la recherche.

Priorite, de type Texte ou Choix, avec les valeurs Haute, Moyenne et Basse. Les thèmes de priorité haute sont traités en premier.

Actif, de type Bascule. Décocher un thème le retire de la veille du mois suivant sans le supprimer.

Commentaire, de type Texte. Consigne libre, par exemple une précision sur l'angle attendu.

## Table 4, Veille_Sources

C'est la table de pilotage qui définit où chercher. Ajoutez une table vide et renommez-la Veille_Sources. Créez les colonnes suivantes.

Nom, de type Texte.

Domaine, de type Texte. Le nom de domaine seul, sans https ni barre oblique, par exemple lemoniteur.fr. C'est la colonne qui identifie chaque ligne.

Type, de type Texte ou Choix, avec les valeurs Presse spécialisée, Veille réglementaire, Réglementaire et Institutionnel.

Abonnement, de type Bascule. À cocher pour les trois sites payants, ce qui indique au protocole que le contenu complet ne sera pas récupéré.

Actif, de type Bascule.

Commentaire, de type Texte.

## Créer la page de lecture

Une fois les quatre tables créées, cliquez sur Ajouter, puis sur Ajouter une page. Choisissez Fiche et sélectionnez la table Veille_Syntheses. La vue Fiche affiche une seule ligne à la fois, ce qui convient à la lecture d'un texte long.

Ajoutez ensuite une vue à cette même page. Cliquez sur Ajouter, puis sur Ajouter une vue à la table, choisissez Table et sélectionnez Veille_Articles. Dans le panneau de droite, sous l'onglet Données, liez cette vue à Veille_Syntheses par la colonne Mois. La liste des articles se filtrera alors automatiquement sur le mois affiché dans la fiche.

Créez enfin une page distincte nommée Pilotage, avec deux vues de type Table, l'une sur Veille_Themes et l'autre sur Veille_Sources. C'est la page sur laquelle vous interviendrez pour faire évoluer le périmètre de la veille.

## Créer la clé API

Cliquez sur votre nom d'utilisateur en haut à droite, puis sur Paramètres du profil. Dans la section Clé API, cliquez sur Créer pour générer une clé. Copiez-la immédiatement, elle ne sera plus affichée en entier ensuite.

Cette clé donne accès à vos documents Grist. Elle ne doit être saisie que dans les secrets du dépôt GitHub, jamais dans un fichier du dépôt ni dans un message.
