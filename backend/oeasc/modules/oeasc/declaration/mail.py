from flask_mail import Message

# from oeasc.utils.env import mail

from flask import render_template, session, current_app

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


from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_token(user_id, declaration_id):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id, "declaration_id": declaration_id})


def send_mail_actualisation_declaration(declaration):
    """ """

    user = get_user(declaration["id_declarant"])
    email_user = user["email"]
    token = generate_token(user.id, declaration.id)
    base_url = "https://ton-domaine.com/action-declaration"

    url_oui = f"{base_url}/{token}?action=oui"
    url_non = f"{base_url}/{token}?action=non"
    url_modifier = f"{base_url}/{token}?action=modifier"

    html = render_template(
        "modules/oeasc/mail/actualisation_declaration.html",
        user=user,
        declaration=declaration,
        url_oui=url_oui,
        url_non=url_non,
        url_modifier=url_modifier,
    )

    msg = Message(
        subject="Actualisation de votre déclaration", recipients=[email_user], html=html
    )

    mail.send(msg)
