from flask import Blueprint, render_template, current_app, url_for
from flask_mail import Message

from sqlalchemy import text
from pypnusershub.db.models import Application, User
from pypnusershub.db.models_register import TempUser


config = current_app.config
MAIL = config.get("MAIL", None)
DB = config.get("DB", None)

bp = Blueprint("oeasc_api_mail", __name__)


def send_mail(recipients, subject, msg_html):

    if not MAIL and config.get("ANIMATEUR_APPLICATION_MAIL", None):

        return {
            "msg": "les paramètres d'envoi de mail ne sont pas correctement définis"
        }

    application = (
        DB.session.query(Application)
        .filter(Application.id_application == config["ID_APP"])
        .one()
    )

    with MAIL.connect() as conn:
        msg = Message(
            "[" + application.nom_application + "] " + subject,
            sender=config.get("ANIMATEUR_APPLICATION_MAIL"),
            recipients=recipients,
        )

        msg.html = msg_html
        conn.send(msg)

    return {"msg": "ok"}


def create_temp_user(data):

    token = data.get("token", None)

    role = DB.session.query(TempUser).filter(TempUser.token_role == token).first()

    if not role:

        return {"msg": token + " : ce token n'est pas associé à un compte temporaire"}

    recipients = [role.email]
    subject = "demande de création de compte"
    msg_html = render_template(
        "modules/oeasc/mail/create_temp_user.html",
        token=token,
        identifiant=role.identifiant,
    )

    return send_mail(recipients, subject, msg_html)


def valid_temp_user(data):

    role = data
    organisme = DB.engine.execute(
        text(
            "SELECT nom_organisme FROM utilisateurs.bib_organismes WHERE id_organisme="
            + str(role["id_organisme"])
        )
    ).first()

    if organisme:
        role["organisme"] = organisme[0]

    if not role:

        return {"msg": "Pas de role pour valid_temp_user"}

    recipients = [
        config.get("ANIMATEUR_APPLICATION_MAIL"),
        config.get("ADMIN_APPLICATION_MAIL"),
    ]
    subject = " [ANIMATEUR] création d" " un nouvel utilisateur"

    msg_html = "<p>Un nouvel utilisateur vient de s'enregister</p>"
    msg_html += "<hr><p>Identifiant : {}</p><p>E-mail : {}</p><p>Nom : {}</p><p>Prenom : {}</p><p>Organisme : {}</p>".format(
        role["identifiant"].strip(),
        role["email"].strip(),
        role["nom_role"].strip(),
        role["prenom_role"].strip(),
        role["organisme"].strip(),
    )

    return send_mail(recipients, subject, msg_html)


def change_application_right(data):

    role = data["role"]

    id_droit = data["id_droit"]

    if not role:

        return {"msg": "Pas de role pour valid_temp_user"}

    recipients = [role["email"]]
    subject = " modification de votre niveau de droit "

    msg_html = render_template(
        "modules/oeasc/mail/change_application_right.html", role=role, id_droit=id_droit
    )

    return send_mail(recipients, subject, msg_html)


def create_cor_role_token(data):

    token = data["token"]
    id_role = data["id_role"]

    role = DB.session.query(User).filter(id_role == User.id_role).first()

    # url_validation = config['URL_APPLICATION'] + url_for('user.change_password', token=token)
    recipients = [role.email]

    subject = "changement de mot de passe"
    msg_html = render_template(
        "modules/oeasc/mail/change_password.html",
        token=token,
    )

    return send_mail(recipients, subject, msg_html)


function_dict = {
    "create_cor_role_token": create_cor_role_token,
    "create_temp_user": create_temp_user,
    "valid_temp_user": valid_temp_user,
    "change_application_right": change_application_right,
}
