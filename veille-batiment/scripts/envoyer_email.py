#!/usr/bin/env python3
"""Envoi de la synthese mensuelle par courrier electronique.

N utilise que la bibliotheque standard. L envoi n a lieu que si les
variables d environnement necessaires sont renseignees, sinon le script
s arrete sans erreur, ce qui permet de laisser l etape en place meme si
l envoi d email n est pas configure.

Variables d environnement attendues :

  SMTP_SERVEUR       par exemple smtp.gmail.com ou le relais de l universite
  SMTP_PORT          587 pour STARTTLS, 465 pour SSL, defaut 587
  SMTP_UTILISATEUR   identifiant de connexion au serveur
  SMTP_MOT_DE_PASSE  mot de passe applicatif
  EMAIL_EXPEDITEUR   adresse affichee en expediteur, defaut SMTP_UTILISATEUR
  EMAIL_DESTINATAIRE adresse professionnelle du destinataire
"""

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MOIS_EN_TOUTES_LETTRES = {
    "01": "janvier",
    "02": "fevrier",
    "03": "mars",
    "04": "avril",
    "05": "mai",
    "06": "juin",
    "07": "juillet",
    "08": "aout",
    "09": "septembre",
    "10": "octobre",
    "11": "novembre",
    "12": "decembre",
}


def libelle_mois(mois):
    annee, _, numero = mois.partition("-")
    return "{0} {1}".format(MOIS_EN_TOUTES_LETTRES.get(numero, numero), annee)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage : envoyer_email.py AAAA-MM")
    mois = sys.argv[1]

    serveur = os.environ.get("SMTP_SERVEUR", "")
    utilisateur = os.environ.get("SMTP_UTILISATEUR", "")
    mot_de_passe = os.environ.get("SMTP_MOT_DE_PASSE", "")
    destinataire = os.environ.get("EMAIL_DESTINATAIRE", "")

    if not (serveur and utilisateur and mot_de_passe and destinataire):
        print(
            "Envoi d email non configure, etape ignoree. "
            "Renseignez SMTP_SERVEUR, SMTP_UTILISATEUR, SMTP_MOT_DE_PASSE "
            "et EMAIL_DESTINATAIRE pour l activer."
        )
        return

    port = int(os.environ.get("SMTP_PORT", "587"))
    expediteur = os.environ.get("EMAIL_EXPEDITEUR", utilisateur)

    chemin = os.path.join(RACINE, "veilles", "{0}.md".format(mois))
    if not os.path.exists(chemin):
        raise SystemExit("Fichier introuvable : " + chemin)

    with open(chemin, encoding="utf-8") as fichier:
        contenu = fichier.read()

    corps = contenu
    if contenu.startswith("---"):
        lignes = contenu.split("\n")
        for index in range(1, len(lignes)):
            if lignes[index].strip() == "---":
                corps = "\n".join(lignes[index + 1 :]).lstrip("\n")
                break

    message = EmailMessage()
    message["Subject"] = "Veille batiment durable, " + libelle_mois(mois)
    message["From"] = expediteur
    message["To"] = destinataire
    message.set_content(corps)

    contexte = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(serveur, port, context=contexte, timeout=60) as session:
            session.login(utilisateur, mot_de_passe)
            session.send_message(message)
    else:
        with smtplib.SMTP(serveur, port, timeout=60) as session:
            session.starttls(context=contexte)
            session.login(utilisateur, mot_de_passe)
            session.send_message(message)

    print("Synthese du mois {0} envoyee a {1}.".format(mois, destinataire))


if __name__ == "__main__":
    main()
