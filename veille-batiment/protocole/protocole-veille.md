# Protocole de veille mensuelle

Ce document est la consigne suivie par la session automatisée qui produit la veille chaque mois. Il est volontairement précis pour que le résultat reste comparable d'un mois sur l'autre.

## Périmètre

Le périmètre est défini par deux fichiers du dépôt, qui sont eux-mêmes le reflet de deux tables Grist que vous remplissez.

Le fichier protocole/themes.json reprend les lignes actives de la table Veille_Themes. Chaque ligne porte un thème, une liste de mots clés, une priorité et un commentaire libre.

Le fichier protocole/sources.json reprend les lignes actives de la table Veille_Sources. Chaque ligne porte un nom, un nom de domaine, un type et l'indication d'un abonnement.

Ces deux fichiers sont mis à jour automatiquement le 4 de chaque mois par le workflow de synchronisation, qui relit les tables Grist. Pour élargir ou restreindre la veille, il suffit donc d'ajouter, de modifier ou de décocher une ligne dans Grist, sans jamais toucher au code.

## Déroulement de la recherche

Première étape, lire protocole/themes.json et protocole/sources.json. Ne jamais utiliser une liste de thèmes ou de sources codée en dur.

Deuxième étape, pour chaque thème actif, lancer une recherche restreinte aux domaines des sources sous abonnement, en construisant la requête à partir des mots clés du thème et du mois écoulé. Traiter les thèmes de priorité haute en premier, afin que le budget de recherche soit consommé d'abord sur ce qui compte.

Troisième étape, pour chaque thème actif, lancer une seconde recherche restreinte aux domaines des sources réglementaires et institutionnelles, afin de récupérer les références de textes et les dispositifs de financement.

Quatrième étape, lancer une recherche transverse sur les sélections de textes officiels du mois écoulé, qui constituent le filet de sécurité contre les sujets non couverts par les thèmes.

## Règles de rédaction

Un sujet traité par plusieurs sources donne lieu à un seul développement. Les différents articles sont cités ensemble à la fin du développement, en indiquant la source de chacun.

Chaque développement indique la référence du texte réglementaire lorsqu'elle existe, avec son numéro et sa date, et un lien vers Légifrance ou EUR-Lex. Le lien vers l'article de presse est fourni séparément, l'accès dépendant de l'abonnement.

Chaque développement se termine par une phrase indiquant ce que le sujet implique concrètement pour le patrimoine de l'université. C'est cette phrase qui distingue une veille utile d'une revue de presse.

Une information annoncée mais non encore publiée au Journal officiel est signalée comme telle, sans être présentée comme acquise.

La synthèse s'ouvre sur le sujet le plus urgent du mois, c'est-à-dire celui qui porte l'échéance la plus proche, et se referme sur les trois actions à retenir.

## Contraintes de forme

Pas d'émoji. Pas de traits horizontaux de séparation, un saut de ligne suffit. Pas de tiret cadratin au milieu d'une phrase. Pas de virgule avant la conjonction et. Le texte doit se copier directement dans un document Word, ce qui suppose des paragraphes rédigés plutôt que des listes à puces.

L'université se nomme Université de Montpellier Paul Valéry, en abrégé UMPV. L'ancienne dénomination Paul Valéry Montpellier 3 ne doit jamais être employée.

## Fichiers produits

La session écrit deux fichiers dans le dossier veilles, nommés d'après le mois au format AAAA-MM.

Le fichier AAAA-MM.md contient un en-tête de quatre lignes entre deux délimiteurs, puis la synthèse rédigée. L'en-tête porte le mois, le titre, la période couverte et la date de publication.

Le fichier AAAA-MM.articles.json contient la liste structurée des sujets. Chaque entrée porte les champs Titre, Theme, Date_article, Resume, Sources, Lien_article, Lien_reglementaire, Impact_UMPV et Priorite. Le champ Theme reprend exactement un libellé de la table Veille_Themes. Le champ Sources énumère les sources ayant traité le sujet, séparées par une virgule.

Le commit de ces deux fichiers sur la branche main déclenche la publication dans Grist.

## Limites assumées

La veille est construite à partir des titres, des accroches et des références publiquement indexés des sites sous abonnement, complétés par les sources réglementaires ouvertes. Le contenu intégral des articles n'est pas récupéré, ce qui serait contraire aux conditions d'utilisation des éditeurs. Aucun identifiant d'abonnement n'est utilisé ni stocké.

En conséquence, les dates et les numéros de texte doivent être vérifiés sur Légifrance avant tout usage engageant. La veille sert à repérer et à hiérarchiser, la lecture de l'article et du texte reste nécessaire pour décider.
