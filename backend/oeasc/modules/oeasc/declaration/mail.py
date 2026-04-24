from flask_mail import Message
import pandas as pd

# from oeasc.utils.env import mail
from oeasc.utils.apiResponse import ApiResponse
from flask import render_template, session, current_app
from oeasc.modules.oeasc.declaration.models import TDeclaration
from sqlalchemy import update
from itsdangerous import URLSafeTimedSerializer
from smtplib import SMTPRecipientsRefused
from werkzeug.local import LocalProxy

from .repository import (
    get_user,
    get_variables_declaration,
)
from oeasc.modules.oeasc.declaration.all_stmt import (
    stmt_liste_declarations_a_renouveler,
)
import time
from flask.cli import with_appcontext
from datetime import datetime, timedelta

config = LocalProxy(lambda: current_app.config)
mail = LocalProxy(lambda: config["MAIL"])


def get_config():
    return current_app.config


def get_db():
    return current_app.config["DB"]


def generate_token(user_id, declaration_id):
    """Génère un token de renouvellement pour une déclaration.
    Le token contient l'id de l'utilisateur et l'id de la déclaration, et est signé avec la clé secrète de l'application.
    Le token est valide pendant 1 mois."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id, "declaration_id": declaration_id})


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


def send_mail_alerte_renouvellement_declaration(declaration):
    """Envoie un mail à l'animateur pour l'informer qu'une déclaration est en attente de renouvellement.
    Cela correspond à une ligne de la requête liste_declarations_a_renouveler()
    Il faudra qu'il valide cette nouvelle déclaration.
    """

    variables_declaration = get_variables_declaration()
    liste_mails_animateurs = variables_declaration["LISTE_MAILS_ANIMATEURS"]

    with mail.connect() as conn:

        html = render_template(
            "modules/oeasc/mail/alerte_renouvellement_declaration.html",
            info_declaration=declaration,
        )

        msg = Message(
            "[OEASC] [ANIMATEUR] Une déclaration a été renouvelée",
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=liste_mails_animateurs,
            html=html,
        )

        try:
            conn.send(msg)
        except SMTPRecipientsRefused:
            print("Adresse invalide")
        except Exception as e:
            print("Erreur lors de l'envoi du mail : ", e)


def send_mail_echec_renouvellement_declaration(declaration):
    """Envoie un mail à l'animateur pour l'informer qu'une déclaration a échoué à être renouvelée.
    Pour qu'il puisse contacter le déclarant pour une alternative.
    Aussi pour qu'il contact le dév pour corriger le problème si besoin.
    Cela correspond à une ligne de la requête liste_declarations_a_renouveler()
    """

    variables_declaration = get_variables_declaration()
    liste_mails_animateurs = variables_declaration["LISTE_MAILS_ANIMATEURS"]

    liste_mails_animateurs = liste_mails_animateurs.append(
        config["ADMIN_APPLICATION_MAIL"]
    )

    with mail.connect() as conn:

        html = render_template(
            "modules/oeasc/mail/alerte_echec_renouvellement_declaration.html",
            info_declaration=declaration,
        )

        msg = Message(
            "[OEASC] [ANIMATEUR] Une déclaration a échoué à être renouvelée",
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=liste_mails_animateurs,
            html=html,
        )

        try:
            conn.send(msg)
        except SMTPRecipientsRefused:
            print("Adresse invalide")
        except Exception as e:
            print("Erreur lors de l'envoi du mail : ", e)


@with_appcontext
def relance_toutes_declarations():
    """Envoie les emails de relance aux déclarations concernées
    cette fonction est appelée par la commande send-relance qui est exécutée tous les mois par le cron du serveur
    """

    response = ApiResponse(log_file="send_all_mails_renouvellement.log", session=None)

    vars_declaration = get_variables_declaration()
    statut_declaration = vars_declaration["STATUT_DECLARATION"]
    DB = get_db()

    stmt_renew = stmt_liste_declarations_a_renouveler(statut_declaration)

    result = DB.session.execute(stmt_renew)

    rows = result.mappings().all()
    if not rows:
        response.add_log(
            "Aucune déclaration à traiter", type_log="INFO", with_timestamp=True
        )
        response.write_in_log_file()
        return response

    df_declaration = pd.DataFrame(rows)

    # pour les test on limite à 2 mails pour éviter d'en envoyer trop
    df_declaration = df_declaration.head(2)

    if isinstance(df_declaration, pd.Series):
        df_declaration = pd.DataFrame([df_declaration])

    if "declaration_date" in df_declaration.columns:
        df_declaration["declaration_date"] = pd.to_datetime(
            df_declaration["declaration_date"], errors="coerce"
        )
        df_declaration["date_declaration_visible"] = df_declaration[
            "declaration_date"
        ].dt.strftime("%d/%m/%Y")
    else:
        # sinon on met la date d'il y a 3 ans
        df_declaration["date_declaration_visible"] = (
            datetime.now() - pd.DateOffset(years=3)
        ).strftime("%d/%m/%Y")

    if df_declaration.shape[0] == 0:
        response.add_log(
            "Aucune déclaration à traiter", type_log="INFO", with_timestamp=True
        )
    else:
        response.add_log(
            f"Début de l'envoi des mails de renouvellement pour {df_declaration.shape[0]} déclarations",
            type_log="INFO",
            with_timestamp=True,
        )

        # pour les test on limite à 2 mails pour éviter d'en envoyer trop. A commenter pour la production
        df_declaration = df_declaration.head(2)

        for index, declaration in df_declaration.iterrows():
            try:
                send_mail_actualisation_declaration(declaration)
                response.add_log(
                    f"Mail envoyé pour la déclaration {declaration['id_declaration']}",
                    type_log="INFO",
                )
            except Exception as e:
                response.add_log(
                    f"Erreur lors de l'envoi du mail pour la déclaration {declaration['id_declaration']} : {str(e)}",
                    type_log="ERROR",
                )

            # attente de 1 seconde entre chaque mail pour éviter les problèmes de saturation du serveur de mail
            print(
                f"Attente de 1 seconde avant d'envoyer le mail pour la déclaration {declaration['id_declaration']}..."
            )
            time.sleep(1)

        response.add_log("Fin de l'envoi des mails de renouvellement", type_log="INFO")

    response.write_in_log_file()

    return response


@with_appcontext
def send_mail_actualisation_declaration(declaration):
    """Envoie un mail au déclarant pour lui proposer de renouveler sa déclaration ou de la clôturer.
    On créé un token de renouvellement qui sera vérifié lors du clic sur les liens du mail.
    Le token est valide 1 mois.
    info_declaration doit contenir au moins : id_declaration, id_declarant, email, nom_role, prenom_role, accept_email
    Cela correspond à une ligne de la requête liste_declarations_a_renouveler()
    """

    config = get_config()
    vars_declaration = get_variables_declaration()
    nb_jours_renouvellement = vars_declaration["NB_JOURS_RELANCE_MAIL"]
    nb_max_renouvellement = vars_declaration["NB_RELANCES_MAX"]
    statut_declaration = vars_declaration["STATUT_DECLARATION"]
    liste_mails_animateurs = vars_declaration["LISTE_MAILS_ANIMATEURS"]
    DB = get_db()

    token = generate_token(
        int(declaration["id_declarant"]), int(declaration["id_declaration"])
    )
    base_url = str(config["URL_FRONTEND"] + "#/declaration/actualisation_declaration")
    url_oui = f"{base_url}?token={token}&id={declaration['id_declaration']}&action=oui"
    url_non = f"{base_url}?token={token}&id={declaration['id_declaration']}&action=non"

    # enregistrement du token de renouvellement dans la base de données avec marshallow pour la validation
    date_fin_token = datetime.now() + timedelta(days=nb_jours_renouvellement)
    str_date_fin_token = date_fin_token.strftime("%Y-%m-%d")

    statut_actuel = declaration["statut"]
    # print (statut_actuel)
    if statut_actuel == statut_declaration["Active"]:
        # si la déclaration est "Active", on passe son statut à "Relance"
        new_statut = statut_declaration["Relance"]
    elif statut_actuel >= statut_declaration["Relance"] + nb_max_renouvellement:
        print(
            f"Nombre de relances max atteint pour la déclaration {declaration['id_declaration']}. Aucune relance envoyée."
        )
        new_statut = statut_declaration["Archivée sans réponse"]
    elif (statut_actuel >= statut_declaration["Relance"]) and (
        statut_actuel != statut_declaration["Active"]
    ):
        # si la déclaration est déjà en statut de relance, on incrémente son statut
        new_statut = (
            statut_declaration["Relance"]
            + (statut_actuel - statut_declaration["Relance"])
            + 1
        )
    else:
        new_statut = statut_actuel

    # transformation de declaration en dictionnaire pour pouvoir accéder aux champs dans le template du mail
    declaration_dict = dict(declaration)

    with mail.connect() as conn:
        html = render_template(
            "modules/oeasc/mail/actualisation_declaration.html",
            info_declaration=declaration_dict,
            user=declaration_dict["id_declarant"],
            url_oui=url_oui,
            url_non=url_non,
            # url_modifier=url_modifier,
        )

        msg = Message(
            "[OEASC] Actualisation de votre déclaration",
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=[declaration["email"]],
            cc=liste_mails_animateurs,
            html=html,
        )

        try:
            conn.send(msg)

            stmt_update = (
                update(TDeclaration)
                .where(TDeclaration.id_declaration == declaration["id_declaration"])
                .values(
                    token_renouvellement=token,
                    date_fin_token=str_date_fin_token,
                    statut=new_statut,
                )
            )
            print(
                f"Mise à jour du statut de la déclaration {declaration['id_declaration']} dans la BDD avec le statut {new_statut}"
            )
            DB.session.execute(stmt_update)
            DB.session.commit()
        except SMTPRecipientsRefused:
            print("Adresse invalide")
        except Exception as e:
            print("Erreur lors de l'envoi du mail : ", e)
