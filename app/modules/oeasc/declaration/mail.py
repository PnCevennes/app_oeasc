from flask_mail import Message

from app.utils.env import mail

from flask import render_template, session, current_app

from .repository import (
    get_user,
    f_create_or_update_declaration,
)

from .declaration_sample import declaration_dict_random_sample


config = current_app.config

# @TOCLEAN : NOT USE
def display_mail_test(destinataire):

    declaration = declaration_dict_random_sample()

    declaration = f_create_or_update_declaration(declaration)

    user = get_user(declaration["id_declarant"])

    return render_template(
        "modules/oeasc/mail/validation_declaration.html",
        destinataire=destinataire,
        declaration=declaration,
        user=user,
    )

# @TOCLEAN : NOT USE
def send_mail_test():

    declaration = declaration_dict_random_sample()

    declaration = f_create_or_update_declaration(declaration)

    return send_mail_validation_declaration(declaration, True)


def send_mail_validation_declaration(declaration, b_create):
    """
    Evoie un e-mail quand une declaration est validée
    """

    user = get_user(session["current_user"]["id_role"])

    email_user = user["email"]

    with mail.connect() as conn:

        # on envoie le message à l'utilisateur seulement si c'est une creation
        if b_create:
            msg = Message(
                "[OEASC] Votre déclaration a bien été prise en compte",
                sender=config["ANIMATEUR_APPLICATION_MAIL"],
                recipients=[email_user],
            )
            msg.html = render_template(
                "modules/oeasc/mail/validation_declaration.html",
                destinataire="user",
                declaration=declaration,
                user=user,
                b_create=b_create,
            )
            conn.send(msg)

        # test si utilisateur est l'animateur pas de mail
        if email_user in [
            config["ANIMATEUR_APPLICATION_MAIL"],
            config["ADMIN_APPLICATION_MAIL"],
        ]:
            return

        msg = Message(
            "[OEASC] [ANIMATEUR] Nouvelle déclaration"
            if b_create
            else "[OEASC] [ANIMATEUR] Modification de la déclaration "
            + str(declaration["id_declaration"]),
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=[
                config["ANIMATEUR_APPLICATION_MAIL"],
                config["ADMIN_APPLICATION_MAIL"],
            ],
        )

        msg.html = render_template(
            "modules/oeasc/mail/validation_declaration.html",
            destinataire="animateur",
            declaration=declaration,
            user=user,
            b_create=b_create,
        )

        conn.send(msg)
