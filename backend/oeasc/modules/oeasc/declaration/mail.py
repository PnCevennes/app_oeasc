from flask_mail import Message

# from oeasc.utils.env import mail

from flask import render_template, session, current_app
from oeasc.modules.oeasc.declaration.models import (TDeclaration)
from sqlalchemy import update
from itsdangerous import URLSafeTimedSerializer
from smtplib import SMTPRecipientsRefused
from flask import current_app
import json

from .repository import (
    get_user,
)

config = current_app.config
mail = config["MAIL"]


def send_mail_validation_declaration(declaration, b_create):
    """
    Envoie un e-mail lors de la validation d'une déclaration.

    Cette fonction est utilisée dans les cas suivants :
        - Lorsqu'une nouvelle déclaration est créée (b_create=True).
        - Lorsqu'une déclaration existante est modifiée (b_create=False).
    Elle envoie un email à l'utilisateur ayant effectué la déclaration (si ce n'est pas l'animateur ou l'administrateur),
    puis un email d'information à l'animateur et à l'administrateur.

    Args:
        declaration (dict): Dictionnaire contenant les informations de la déclaration.
        b_create (bool): Indique s'il s'agit d'une création (True) ou d'une modification (False).

    Returns:
        None
    """

    # Récupère l'utilisateur à partir de la session (id_role)
    user = get_user(session["current_user"]["id_role"])

    # Récupère l'adresse email de l'utilisateur
    email_user = user["email"]

    # Ouverture de la connexion au serveur mail
    with mail.connect() as conn:
        # Envoie le message à l'utilisateur uniquement si c'est une création
        if b_create:
            msg = Message(
                "[OEASC] Votre déclaration a bien été prise en compte",
                sender=config["ANIMATEUR_APPLICATION_MAIL"],
                recipients=[email_user],
            )
            # Génère le contenu HTML du mail à partir du template
            msg.html = render_template(
                "modules/oeasc/mail/validation_declaration.html",
                destinataire="user",
                declaration=declaration,
                user=user,
                b_create=b_create,
            )
            conn.send(msg)  # Envoie le mail à l'utilisateur

        # Si l'utilisateur est l'animateur ou l'administrateur, on n'envoie pas de mail à ces adresses
        if email_user in [
            config["ANIMATEUR_APPLICATION_MAIL"],
            config["ADMIN_APPLICATION_MAIL"],
        ]:
            return  # Sortie de la fonction, pas d'envoi supplémentaire

        # Prépare le message à destination de l'animateur et de l'administrateur
        msg = Message(
            (
                "[OEASC] [ANIMATEUR] Nouvelle déclaration"
                if b_create
                else "[OEASC] [ANIMATEUR] Modification de la déclaration "
                + str(declaration["id_declaration"])
            ),
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=[
                config["ANIMATEUR_APPLICATION_MAIL"],
                config["ADMIN_APPLICATION_MAIL"],
            ],
        )

        # Génère le contenu HTML du mail à partir du template
        msg.html = render_template(
            "modules/oeasc/mail/validation_declaration.html",
            destinataire="animateur",
            declaration=declaration,
            user=user,
            b_create=b_create,
        )

        conn.send(msg)  # Envoie le mail à l'animateur et à l'administrateur





def generate_token(user_id, declaration_id):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id, "declaration_id": declaration_id})


def send_mail_actualisation_declaration(declaration):
    """ Envoie un mail au déclarant pour lui proposer de renouveler sa déclaration ou de la clôturer.
     On créé un token de renouvellement qui sera vérifié lors du clic sur les liens du mail.
     Le token est valide 1 mois.
     info_declaration doit contenir au moins : id_declaration, id_declarant, email, nom_role, prenom_role, accept_email
     Cela correspond à une ligne de la requête liste_declarations_a_renouveler()
     """

    variables_declaration = json.load(open(str(config['ROOT_DIR']) + "/config/variables/declaration.json"))
    statut_declaration = variables_declaration["STATUT_DECLARATION"]
    nb_jours_renouvellement = variables_declaration["NB_JOURS_RELANCE_MAIL"]
    nb_max_renouvellement = variables_declaration["NB_RELANCES_MAX"]
    liste_mails_animateurs = variables_declaration["LISTE_MAILS_ANIMATEURS"]

    
    token = generate_token(declaration["id_declarant"], declaration["id_declaration"])
    base_url = str(config["URL_FRONTEND"] +"#/declaration/actualisation_declaration")
    url_oui = f"{base_url}?token={token}&id={declaration['id_declaration']}&action=oui"
    url_non = f"{base_url}?token={token}&id={declaration['id_declaration']}&action=non"


    #enregistrement du token de renouvellement dans la base de données avec marshallow pour la validation
    import datetime
    date_fin_token = datetime.datetime.now() + datetime.timedelta(days=nb_jours_renouvellement)
    str_date_fin_token = date_fin_token.strftime("%Y-%m-%d")
    
    statut_actuel = declaration["statut"]
    # print (statut_actuel)
    if statut_actuel == statut_declaration["Active"]:
        # si la déclaration est "Active", on passe son statut à "Relance"
        new_statut = statut_declaration["Relance"]
    elif statut_actuel >= statut_declaration['Relance'] + nb_max_renouvellement:
        print(f"Nombre de relances max atteint pour la déclaration {declaration['id_declaration']}. Aucune relance envoyée.")
        new_statut = statut_declaration['Archivée sans réponse']
    elif ((statut_actuel >= statut_declaration['Relance']) and (statut_actuel != statut_declaration['Active'])):
        # si la déclaration est déjà en statut de relance, on incrémente son statut
        new_statut = statut_declaration['Relance'] + (statut_actuel - statut_declaration['Relance']) + 1
    
    with mail.connect() as conn:

        html = render_template(
            "modules/oeasc/mail/actualisation_declaration.html",
            info_declaration=declaration,
            user=declaration['id_declarant'],
            url_oui=url_oui,
            url_non=url_non,
            # url_modifier=url_modifier,
        )

        msg = Message(
                "[OEASC] Actualisation de votre déclaration",
                sender=config["ANIMATEUR_APPLICATION_MAIL"],
                recipients=[declaration['email']],
                cc=liste_mails_animateurs,
                html=html
            )
        # print("Envoi du mail à : ", msg.html)
        

        try:
            conn.send(msg)
            # Update de la declaration directement en bdd pour enregistrer le token de renouvellement et la date de fin de validité du token, ainsi que le nouveau statut
            # sans utiliser marshmallow pour éviter les problèmes de validation liés au token qui n'est pas un champ de la déclaration
            stmt_update = (
                update(TDeclaration)
                .where(TDeclaration.id_declaration == declaration["id_declaration"])
                .values(
                    token_renouvellement=token,
                    date_fin_token=str_date_fin_token,
                    statut=new_statut
                )
            )
            current_app.config["DB"].session.execute(stmt_update)
            current_app.config["DB"].session.commit()

        except SMTPRecipientsRefused:
            current_app.config["DB"].session.rollback()  # Annule la transaction en cas d'erreur d'envoi du mail
            print("Adresse invalide")
        except Exception as e:
            current_app.config["DB"].session.rollback()  # Annule la transaction en cas d'erreur d'envoi du mail
            print("Erreur lors de l'envoi du mail : ", e)



