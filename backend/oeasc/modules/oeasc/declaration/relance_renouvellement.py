#####################################################################################
####### Recherches toutes les déclaration à renouveler et envoie un mail avec
####### un lien de renouvellement ou de clôture de la déclaration
####### Ce script est lancé par une tâche cron tous les mois
#####################################################################################
import pandas as pd
from oeasc.utils.apiResponse import ApiResponse
from flask import current_app, render_template
from flask_mail import Message
from smtplib import SMTPRecipientsRefused
from oeasc.modules.oeasc.declaration.mail import generate_token
from oeasc.modules.oeasc.declaration.mail import mail
from oeasc.modules.oeasc.declaration.models import TDeclaration
from oeasc.modules.oeasc.declaration.all_stmt import (
    stmt_liste_declarations_a_renouveler,
)
import json

from sqlalchemy import func, update

import time
from flask.cli import with_appcontext
from datetime import datetime, timedelta


def get_config():
    return current_app.config


def get_db():
    return current_app.config["DB"]


# Fonctions PostgreSQL custom (appelées via func)
def get_nomenclature_label(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_label(arg), "")


def get_nomenclature_mnemonique(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemonique(arg), "")


def get_nomenclature_code(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_code(arg), "")


def get_nomenclature_labels(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_labels(arg), "")


def get_nomenclature_mnemoniques(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemoniques(arg), "")


def get_nomenclature_codes(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_codes(arg), "")


def get_area_names(id_declaration, area_type):
    return func.coalesce(
        func.oeasc_declarations.get_area_names(id_declaration, area_type), ""
    )


def get_id_areas(id_declaration, area_type):
    return func.coalesce(
        func.oeasc_declarations.get_area_ids(id_declaration, area_type), ""
    )


def get_variables_declaration():
    config = current_app.config
    return json.load(
        open(str(config["ROOT_DIR"]) + "/config/variables/declaration.json")
    )


@with_appcontext
def relance_toutes_declarations():
    """Envoie les emails de relance aux déclarations concernées"""

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

        # pour les test on limite à 2 mails pour éviter d'en envoyer trop
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
