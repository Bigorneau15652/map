#!/usr/bin/env python3
"""Synchronisation entre le depot de veille et un document Grist.

Trois commandes :

  exporter-config      Grist  ->  depot. Relit les tables de pilotage
                       Veille_Themes et Veille_Sources et ecrit
                       protocole/themes.json et protocole/sources.json.

  initialiser-config   depot  ->  Grist. Envoie les themes et les sources
                       par defaut dans les tables de pilotage. A lancer
                       une seule fois, au demarrage.

  publier-veille       depot  ->  Grist. Envoie la synthese mensuelle et
                       la liste des articles dans Veille_Syntheses et
                       Veille_Articles.

Variables d'environnement attendues :

  GRIST_SERVER   par exemple https://grist.numerique.gouv.fr
  GRIST_DOC_ID   identifiant du document Grist
  GRIST_API_KEY  cle API du compte Grist

Le script n'utilise que la bibliotheque standard de Python.
"""

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TABLE_SYNTHESES = "Veille_Syntheses"
TABLE_ARTICLES = "Veille_Articles"
TABLE_THEMES = "Veille_Themes"
TABLE_SOURCES = "Veille_Sources"


def config_env():
    serveur = os.environ.get("GRIST_SERVER", "").rstrip("/")
    doc_id = os.environ.get("GRIST_DOC_ID", "")
    cle = os.environ.get("GRIST_API_KEY", "")
    manquants = [
        nom
        for nom, valeur in (
            ("GRIST_SERVER", serveur),
            ("GRIST_DOC_ID", doc_id),
            ("GRIST_API_KEY", cle),
        )
        if not valeur
    ]
    if manquants:
        raise SystemExit(
            "Variables d'environnement manquantes : " + ", ".join(manquants)
        )
    return serveur, doc_id, cle


def appel_grist(methode, chemin, cle, corps=None, parametres=None):
    serveur, doc_id, _ = config_env()
    url = "{0}/api/docs/{1}{2}".format(serveur, doc_id, chemin)
    if parametres:
        url = url + "?" + urllib.parse.urlencode(parametres)
    donnees = None
    if corps is not None:
        donnees = json.dumps(corps).encode("utf-8")
    requete = urllib.request.Request(url, data=donnees, method=methode)
    requete.add_header("Authorization", "Bearer " + cle)
    requete.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(requete, timeout=60) as reponse:
            brut = reponse.read().decode("utf-8")
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode("utf-8", errors="replace")
        raise SystemExit(
            "Erreur Grist {0} sur {1}\n{2}".format(erreur.code, url, detail)
        )
    except urllib.error.URLError as erreur:
        raise SystemExit("Grist injoignable sur {0} : {1}".format(url, erreur.reason))
    if not brut:
        return {}
    return json.loads(brut)


def lire_table(nom_table, cle):
    reponse = appel_grist("GET", "/tables/{0}/records".format(nom_table), cle)
    return reponse.get("records", [])


def upsert(nom_table, enregistrements, cle):
    """Ajoute ou met a jour des lignes. Chaque enregistrement porte une cle
    de rapprochement dans require et ses valeurs dans fields."""
    if not enregistrements:
        return 0
    lot = 100
    total = 0
    for debut in range(0, len(enregistrements), lot):
        tranche = enregistrements[debut : debut + lot]
        appel_grist(
            "PUT",
            "/tables/{0}/records".format(nom_table),
            cle,
            corps={"records": tranche},
            parametres={"onmany": "first", "noparse": "false"},
        )
        total = total + len(tranche)
    return total


def lire_front_matter(chemin):
    """Lit un en-tete YAML simple, en cle: valeur, delimite par des lignes ---."""
    with open(chemin, encoding="utf-8") as fichier:
        contenu = fichier.read()
    entete = {}
    corps = contenu
    if contenu.startswith("---"):
        lignes = contenu.split("\n")
        fin = None
        for index in range(1, len(lignes)):
            if lignes[index].strip() == "---":
                fin = index
                break
        if fin is not None:
            for ligne in lignes[1:fin]:
                if ":" in ligne:
                    nom, _, valeur = ligne.partition(":")
                    entete[nom.strip()] = valeur.strip()
            corps = "\n".join(lignes[fin + 1 :]).lstrip("\n")
    return entete, corps


def cle_article(mois, article):
    empreinte = "{0}|{1}|{2}".format(
        mois, article.get("Lien_article", ""), article.get("Titre", "")
    )
    return hashlib.sha1(empreinte.encode("utf-8")).hexdigest()[:16]


def commande_exporter_config():
    _, _, cle = config_env()

    themes = []
    for enregistrement in lire_table(TABLE_THEMES, cle):
        champs = enregistrement.get("fields", {})
        if not champs.get("Actif", True):
            continue
        themes.append(
            {
                "Theme": champs.get("Theme", ""),
                "Mots_cles": champs.get("Mots_cles", ""),
                "Priorite": champs.get("Priorite", "Moyenne"),
                "Commentaire": champs.get("Commentaire", ""),
            }
        )

    sources = []
    for enregistrement in lire_table(TABLE_SOURCES, cle):
        champs = enregistrement.get("fields", {})
        if not champs.get("Actif", True):
            continue
        sources.append(
            {
                "Nom": champs.get("Nom", ""),
                "Domaine": champs.get("Domaine", ""),
                "Type": champs.get("Type", ""),
                "Abonnement": bool(champs.get("Abonnement", False)),
                "Commentaire": champs.get("Commentaire", ""),
            }
        )

    if not themes:
        print("Aucun theme actif dans Grist, le fichier existant est conserve.")
    else:
        ecrire_json(os.path.join(RACINE, "protocole", "themes.json"), themes)
        print("{0} themes actifs exportes.".format(len(themes)))

    if not sources:
        print("Aucune source active dans Grist, le fichier existant est conserve.")
    else:
        ecrire_json(os.path.join(RACINE, "protocole", "sources.json"), sources)
        print("{0} sources actives exportees.".format(len(sources)))


def ecrire_json(chemin, donnees):
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        fichier.write("\n")


def lire_json(chemin):
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)


def commande_initialiser_config():
    _, _, cle = config_env()

    themes = lire_json(os.path.join(RACINE, "protocole", "themes-defaut.json"))
    enregistrements = [
        {"require": {"Theme": theme["Theme"]}, "fields": theme} for theme in themes
    ]
    nombre = upsert(TABLE_THEMES, enregistrements, cle)
    print("{0} themes envoyes dans {1}.".format(nombre, TABLE_THEMES))

    sources = lire_json(os.path.join(RACINE, "protocole", "sources-defaut.json"))
    enregistrements = [
        {"require": {"Domaine": source["Domaine"]}, "fields": source}
        for source in sources
    ]
    nombre = upsert(TABLE_SOURCES, enregistrements, cle)
    print("{0} sources envoyees dans {1}.".format(nombre, TABLE_SOURCES))


def commande_publier_veille(mois):
    _, _, cle = config_env()

    chemin_md = os.path.join(RACINE, "veilles", "{0}.md".format(mois))
    chemin_articles = os.path.join(RACINE, "veilles", "{0}.articles.json".format(mois))

    if not os.path.exists(chemin_md):
        raise SystemExit("Fichier introuvable : " + chemin_md)

    entete, synthese = lire_front_matter(chemin_md)
    articles = lire_json(chemin_articles) if os.path.exists(chemin_articles) else []

    ligne_synthese = {
        "require": {"Mois": mois},
        "fields": {
            "Mois": mois,
            "Titre": entete.get("titre", "Veille " + mois),
            "Periode": entete.get("periode", ""),
            "Date_publication": entete.get("date_publication", ""),
            "Synthese": synthese,
            "Nb_articles": len(articles),
        },
    }
    upsert(TABLE_SYNTHESES, [ligne_synthese], cle)
    print("Synthese du mois {0} publiee.".format(mois))

    enregistrements = []
    for article in articles:
        identifiant = cle_article(mois, article)
        champs = dict(article)
        champs["Cle"] = identifiant
        champs["Mois"] = mois
        enregistrements.append({"require": {"Cle": identifiant}, "fields": champs})
    nombre = upsert(TABLE_ARTICLES, enregistrements, cle)
    print("{0} articles publies.".format(nombre))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    commande = sys.argv[1]
    if commande == "exporter-config":
        commande_exporter_config()
    elif commande == "initialiser-config":
        commande_initialiser_config()
    elif commande == "publier-veille":
        if len(sys.argv) < 3:
            raise SystemExit("Usage : publier-veille AAAA-MM")
        commande_publier_veille(sys.argv[2])
    else:
        raise SystemExit("Commande inconnue : " + commande)


if __name__ == "__main__":
    main()
