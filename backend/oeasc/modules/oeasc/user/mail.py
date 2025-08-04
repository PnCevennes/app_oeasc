from flask import Blueprint, render_template, current_app
from flask_mail import Message
from sqlalchemy import select

from pypnusershub.db.models import Application, User, Organisme
from pypnusershub.db.models_register import TempUser


config = current_app.config
DB = config["DB"]

MAIL = config.get("MAIL", None)
# DB = config.get("DB", None)

bp = Blueprint("oeasc_api_mail", __name__)


# Fonction pour envoyer un email via Flask-Mail
# Utilisée par les autres fonctions pour notifier les utilisateurs ou administrateurs
def send_mail(recipients, subject, msg_html):
    # Vérifie que la configuration du mail est correcte
    if not MAIL and config.get("ANIMATEUR_APPLICATION_MAIL", None):
        return {
            "msg": "les paramètres d'envoi de mail ne sont pas correctement définis"
        }

    # Récupère les informations de l'application pour personnaliser le sujet du mail
    stmt_application = select(Application).where(
        Application.id_application == config["ID_APP"]
    ).limit(1)
    application = DB.session.execute(stmt_application).scalars().first()

    # Envoi du mail
    with MAIL.connect() as conn:
        msg = Message(
            "[" + application.nom_application + "] " + subject,
            sender=config["ANIMATEUR_APPLICATION_MAIL"],
            recipients=recipients,
        )
        msg.html = msg_html
        conn.send(msg)

    return {"msg": "ok"}


def create_temp_user(data):
    """
    Crée un utilisateur temporaire à partir des données fournies.

    Cette fonction est utilisée lors de la demande de création d'un compte temporaire. 
    Elle vérifie si le token fourni dans les données correspond à un utilisateur temporaire existant.
    Si le token est valide, elle envoie un email à l'adresse associée à cet utilisateur temporaire 
    pour poursuivre la procédure de création de compte.

    Args:
        data (dict): Dictionnaire contenant les informations nécessaires, notamment le token sous la clé "token".

    Returns:
        dict or bool: 
            - Si le token n'est pas associé à un utilisateur temporaire, retourne un dictionnaire contenant un message d'erreur.
            - Sinon, retourne le résultat de la fonction send_mail (généralement un booléen indiquant le succès de l'envoi).

    Exemple d'utilisation:
        Cette fonction est appelée lors de la soumission d'un formulaire de demande de création de compte temporaire.
    """
    token = data.get("token", None)

    stmt_role = select(TempUser).where(TempUser.token_role == token).limit(1)
    role = DB.session.execute(stmt_role).scalars().first()


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
    """
    Fonction permettant de valider la création d'un utilisateur temporaire et d'envoyer un mail de notification.

    Args:
        data (dict): Dictionnaire contenant les informations de l'utilisateur temporaire à valider. 
            Doit inclure les clés suivantes :
                - "id_organisme" : identifiant de l'organisme auquel l'utilisateur est rattaché
                - "identifiant" : identifiant de l'utilisateur
                - "email" : adresse email de l'utilisateur
                - "nom_role" : nom de l'utilisateur
                - "prenom_role" : prénom de l'utilisateur

    Returns:
        dict ou None: Retourne le résultat de la fonction send_mail si l'envoi du mail est effectué,
        sinon retourne un dictionnaire contenant un message d'erreur.

    Utilisation:
        Cette fonction est utilisée lors de l'enregistrement d'un nouvel utilisateur temporaire dans l'application.
        Elle permet de récupérer le nom de l'organisme associé à l'utilisateur, de compléter les informations,
        puis d'envoyer un mail aux animateurs et administrateurs pour les prévenir de la création du nouvel utilisateur.

    Commentaires détaillés:
        - La fonction commence par récupérer le nom de l'organisme à partir de l'identifiant fourni dans les données.
        - Si l'organisme existe, son nom est ajouté aux données de l'utilisateur.
        - Si les données de l'utilisateur sont invalides ou manquantes, la fonction retourne un message d'erreur.
        - Les destinataires du mail sont définis dans la configuration de l'application.
        - Le sujet et le contenu HTML du mail sont générés à partir des informations de l'utilisateur.
        - Enfin, la fonction utilise send_mail pour envoyer la notification aux destinataires concernés.
    """
    role = data

    stmt_organisme = (select(Organisme.nom_organisme)
        .where(Organisme.id_organisme == str(role["id_organisme"]))
        .limit(1)
    )
    organisme = DB.session.execute(stmt_organisme).scalars().first()    


    if organisme:
        role["organisme"] = organisme[0]

    if not role:
        return {"msg": "Pas de role pour valid_temp_user"}

    recipients = [
        config["ANIMATEUR_APPLICATION_MAIL"],
        config["ADMIN_APPLICATION_MAIL"],
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
    """
    Modifie le niveau de droit d'un utilisateur et envoie un email de notification.

    Cette fonction est utilisée lorsqu'il est nécessaire d'informer un utilisateur
    que son niveau de droit dans l'application a été modifié. Elle prend en entrée
    un dictionnaire `data` contenant les informations du rôle et l'identifiant du droit.

    Args:
        data (dict): Un dictionnaire contenant :
            - "role" (dict): Les informations du rôle de l'utilisateur, incluant son email.
            - "id_droit" (int/str): L'identifiant du nouveau niveau de droit.

    Returns:
        dict: Un dictionnaire contenant le message d'erreur si le rôle est absent.
        Sinon, le résultat de la fonction `send_mail` qui envoie l'email de notification.

    Cas d'utilisation :
        - Lorsqu'un administrateur modifie les droits d'accès d'un utilisateur.
        - Lorsqu'un utilisateur temporaire obtient un nouveau niveau de droit.

    Commentaires :
        - La fonction vérifie d'abord la présence du rôle dans les données.
        - Elle prépare ensuite le destinataire, le sujet et le contenu HTML de l'email.
        - Enfin, elle utilise la fonction `send_mail` pour envoyer la notification.
    """
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
    """
    Cette fonction génère et envoie un email de changement de mot de passe à l'utilisateur correspondant à un rôle donné.

    Args:
        data (dict): Un dictionnaire contenant les informations nécessaires, notamment :
            - "token" (str) : Le jeton de validation pour le changement de mot de passe.
            - "id_role" (int) : L'identifiant du rôle de l'utilisateur concerné.

    Returns:
        bool: Retourne True si l'email a été envoyé avec succès, False sinon.

    Utilisation :
        Cette fonction est utilisée lorsqu'un utilisateur demande à changer son mot de passe. 
        Elle récupère l'utilisateur associé au rôle spécifié, prépare le contenu de l'email avec le jeton de validation, 
        puis envoie l'email à l'adresse de l'utilisateur.

    Commentaires détaillés :
        - La fonction commence par extraire le jeton et l'identifiant du rôle depuis le dictionnaire 'data'.
        - Elle effectue une requête pour récupérer l'utilisateur correspondant à l'identifiant de rôle.
        - L'adresse email du rôle est utilisée comme destinataire de l'email.
        - Le sujet et le contenu HTML de l'email sont préparés à l'aide d'un template.
        - Enfin, la fonction appelle 'send_mail' pour envoyer l'email de changement de mot de passe.
    """
    token = data["token"]
    id_role = data["id_role"]


    stmt_role = select(User).where(User.id_role == id_role).limit(1)
    role = DB.session.execute(stmt_role).scalars().first()


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
    "create_temp_user": create_temp_user,  # créé un temp_user dans la base de donnée et envoi un mail pour confirmer l'adresse mail
    "valid_temp_user": valid_temp_user,  # envoi d'un mail a l'animateur pour prévenir d'un nouvel utlisateurs
    "change_application_right": change_application_right,  # envoi d'un mail a l'utilisateur pour lui dire qu'il a changé de droit
}
