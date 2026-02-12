from flask_mail import Message

# from oeasc.utils.env import mail

from flask import render_template, session, current_app

from .repository import (
    get_user,
    f_create_or_update_declaration,
)


from .declaration_sample import declaration_dict_random_sample

config = current_app.config
mail = config["MAIL"]


def display_mail_test(destinataire):
    """
    Affiche un mail de test pour la validation d'une déclaration.

    Cette fonction est principalement utilisée pour générer et afficher un exemple d'email de validation de déclaration,
    à des fins de test ou de démonstration. Elle crée une déclaration aléatoire, la sauvegarde ou la met à jour,
    récupère l'utilisateur associé à la déclaration, puis rend le template d'email correspondant.

    Args:
        destinataire (str): Adresse email du destinataire à qui le mail de test sera affiché.

    Returns:
        str: Le contenu HTML du mail généré à partir du template 'validation_declaration.html'.

    Utilisation typique :
        - Tests d'affichage des emails de validation de déclaration.
        - Vérification du rendu du template d'email avant envoi réel.
    """
    declaration = declaration_dict_random_sample()

    declaration = f_create_or_update_declaration(declaration)

    user = get_user(declaration["id_declarant"])

    return render_template(
        "modules/oeasc/mail/validation_declaration.html",
        destinataire=destinataire,
        declaration=declaration,
        user=user,
    )


def send_mail_test():
    """
    Envoie un email de test pour la validation d'une déclaration.

    Cette fonction est principalement utilisée pour tester l'envoi d'un email de validation de déclaration.
    Elle génère une déclaration aléatoire, la sauvegarde ou la met à jour dans la base de données,
    puis utilise la fonction send_mail_validation_declaration pour envoyer l'email de validation
    comme si une nouvelle déclaration venait d'être créée.

    Cas d'utilisation :
        - Vérification du bon fonctionnement de l'envoi d'emails.
        - Tests automatisés ou manuels pour s'assurer que le template et l'envoi sont corrects.
        - Démonstration de l'envoi d'un email sans intervention réelle d'un utilisateur.

    Returns:
        None
    """
    declaration = declaration_dict_random_sample()  # Génère une déclaration aléatoire

    declaration = f_create_or_update_declaration(
        declaration
    )  # Sauvegarde ou met à jour la déclaration

    return send_mail_validation_declaration(
        declaration, True
    )  # Envoie l'email comme pour une création


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
