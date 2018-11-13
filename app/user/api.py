import requests

from flask_mail import Message

import random

from app.utils.env import mail

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for
)

from config import config

from app.utils.env import DB

from pypnusershub.db.models import Application, User

from app.utils.utilssqlalchemy import json_resp, as_dict

from .models import TempUser, CorRoleToken

bp = Blueprint('user', __name__)

s = requests.Session()

secret_key = '1234'


@bp.route('test', methods=['GET'])
@json_resp
def test():
    '''
        test dev create user
    '''

    id_app_usershub = DB.session.query(Application.id_application).filter(Application.nom_application == 'UsersHub').first()[0]

    if not id_app_usershub:

        return "Pas d'id app usersHub"

    data_test = {
        "email": "testdelesite@gmail.com",
        "groupe": False,
        "pn": True,
        "remarques": "utilisateur test OEASC",
        "desc_role": None,
        "nom_role": "API",
        "prenom_role": "test",
        "identifiant": "aa",
        "id_unite": -1,
        "id_organisme": -1,
        "password": "1234",
        "password_confirmation": "1234",
        # "applications": [
        #     {
        #         "id_app": 500,
        #         "id_droit": 1
        #     }
        # ]
    }

    r = s.post(config.URL_APPLICATION + "/" + "api/user/create_temp_user", json=data_test)

    return r.text


@bp.route('add_application_right_to_role', methods=['POST'])
@json_resp
def add_application_right_to_role():
    '''
        route pour faire une requete a l'application Usershub pour ajouter des droits à un utilisateur
    '''
    data = request.get_json()

    id_app_usershub = DB.session.query(Application.id_application).filter(Application.nom_application == 'UsersHub').first()[0]

    if not id_app_usershub:

        return "Pas d'id app usersHub"

    print(config.URL_USERHUB)

    r = s.post(config.URL_USERHUB + "/" + "pypn/auth/login", json={'login': config.USER_USERHUB, 'password': config.PWD_USERHUB, 'id_application': id_app_usershub})

    r = s.post(config.URL_USERHUB + "/" + "api_register/add_application_right_to_role", json=data)

    # r = s.post(config.URL_APPLICATION + "/" + "pypn/auth/login", json=data)

    return r.text, r.status_code


@bp.route('create_temp_user', methods=['POST'])
@json_resp
def create_temp_user():
    '''
        route pour creer un compte temporaire en attendait la confirmation de l'adresse mail
        les mot de passe seront stocké en crypté
        1. on stocke les variables qui seront utilisées par la création de compte
        2. on envoie un mail pour demander la confirmation du compte mail
    '''

    # recuperation des parametres
    data = request.get_json()

    temp_user = TempUser(**data)

    # verification des parametres

    (is_temp_user_valid, msg) = temp_user.is_valid()

    if not is_temp_user_valid:

        return msg, 500

    # verification si on a un utilisateur qui a le meme email et les memes droits

    user = DB.session.query(User).filter(User.identifiant == temp_user.identifiant).first()

    if not user:

        # dans ce cas on cree un nouveau utilisateur
        temp_user.token_role = str(random.getrandbits(128))

        # encryption des mdp
        print('avt', temp_user.password)
        temp_user.encrypt_password(secret_key)
        print('apr', temp_user.password)

        # sauvegarde en base
        DB.session.add(temp_user)
        DB.session.commit()

        # envoie du mail de confirmation

        print(temp_user.token_role, temp_user.email)

        url_validation = config.URL_APPLICATION + '/api/user/valid_temp_user/' + temp_user.token_role

        with mail.connect() as conn:

            msg = Message(
                '[OEASC] Votre demande de création de compte à bien été prise en compte',
                sender=config.DEFAULT_MAIL_SENDER,
                recipients=[temp_user.email])
            msg.html = render_template('modules/oeasc/mail/demande_validation_compte.html', url_validation=url_validation)

            conn.send(msg)

        return {'code': 0, 'msg': 'Un mail de verification de compte vous a été envoyé. Veuillez cliquer sur le lien de confirmation dans l''email afin de valider votre compte'}

    else:

        user_dict = as_dict(user, recursif=True)
        is_app_right = sum([user_app['id_application'] == config.ID_APP for user_app in user_dict.get('app_users', None)])
        print(is_app_right)

        if is_app_right:

            return "Un utilisateur avec l'identifiant '" + user_dict['identifiant'] + "' existe deja pour cette application", 500

            return {'code': 1, "msg": "l'utilisateur l'identifiant " + user_dict['identifiant'] + "existe déjà"}, 500

        else:

            return {'code': 1, 'msg': "Un utilisateur avec l'identifiant existe déjà pour une autre application."}


@bp.route('valid_temp_user/<string:temp_user_token>', methods=['GET'])
def valid_temp_user(temp_user_token):
    '''
        route pour valider un compte temporire et en faire un utilisateur (requete a userbub)
    '''

    id_app_usershub = DB.session.query(Application.id_application).filter(Application.nom_application == 'UsersHub').first()[0]

    print("ID users hub", id_app_usershub)

    if not id_app_usershub:

        return "Pas d'id app usersHub"

    # test de connexion à l'appli userhub
    # url_usershub_logout = config.URL_USERHUB + "/" + "pypn/auth/logout"
    # r = s.post(url_usershub_logout)

    url_usershub_login = config.URL_USERHUB + "/" + "pypn/auth/login"

    r = s.post(url_usershub_login, json={'login': config.USER_USERHUB, 'password': config.PWD_USERHUB, 'id_application': id_app_usershub})

    temp_user = DB.session.query(TempUser).filter(temp_user_token == TempUser.token_role).first()

    if not temp_user:

        return "pas d'utilisateur avec le token user demandé", 500

    print('avt', temp_user.password)
    temp_user.decrypt_password(secret_key)
    print('apr', temp_user.password)

    data = temp_user.as_dict()

    data["applications"] = [
        {
            "id_app": config.ID_APP,
            "id_droit": 1
        }
    ]

    r = s.post(config.URL_USERHUB + "/" + "api_register/role", json=data)
    print("test_inser role", r.text, r.status_code)

    DB.session.delete(temp_user)
    DB.session.commit()

    return redirect(url_for('oeasc.login', validation_compte="valid"))


@bp.route("reset_password", methods=['POST'])
def reset_password():

    data = request.get_json()

    token = data.get('token', None)

    if not token:

        return "token non defini dans paramètre POST", 500

    password = data.get('password', None)
    password_confirmation = data.get('password_confirmation', None)

    if not password_confirmation or not password:

        return "password non defini dans paramètres POST", 500

    if not password_confirmation == password:

        return "password et password_confirmation sont différents", 500

    res = DB.session.query(CorRoleToken.id_role).filter(CorRoleToken.token == token).first()

    if not res:

        return "pas d'id role associée au token", 500

    id_role = res[0]

    data_out = {'id_role': id_role, 'password': password}

    id_app_usershub = DB.session.query(Application.id_application).filter(Application.nom_application == 'UsersHub').first()[0]
    url_usershub_login = config.URL_USERHUB + "/" + "pypn/auth/login"
    r = s.post(url_usershub_login, json={'login': config.USER_USERHUB, 'password': config.PWD_USERHUB, 'id_application': id_app_usershub})

    print("login", r.text, r.status_code)

    r = s.post(config.URL_USERHUB + "/" + "api_register/change_password", json=data_out)

    # delete cors
    DB.session.query(CorRoleToken.id_role).filter(CorRoleToken.token == token).delete()
    DB.session.commit()

    print("chgpwd", r.text, r.status_code, config.URL_USERHUB + "/" + "api_register/change_password")

    return r.text, r.status_code

@bp.route("reset_password_send_mail", methods=['POST'])
@json_resp
def reset_password_send_mail():

    data = request.get_json()

    email = data.get('email')

    # si email on envoie un mail
    if not email:

        return "Email non renseigné", 500

    role = DB.session.query(User).filter(User.email == email).first()

    if not role:

        return "Pas d'utilisateur pour l'email " + email, 500

    token = str(random.getrandbits(128))

    DB.session.query(CorRoleToken).filter(CorRoleToken.id_role == role.id_role).delete()

    DB.session.commit()

    cor = CorRoleToken(**{'id_role': role.id_role, 'token': token})
    DB.session.add(cor)
    DB.session.commit()
    url_validation = config.URL_APPLICATION + '/oeasc/reset_password/' + token

    with mail.connect() as conn:

        msg = Message(
            '[OEASC] Changement de mot de passe',
            sender=config.DEFAULT_MAIL_SENDER,
            recipients=[role.email])
        msg.html = render_template('modules/oeasc/mail/changement_de_mot_de_passe.html', url_validation=url_validation)

        conn.send(msg)

    return "ok", 200


@bp.route('create_user', methods=['POST'])
def create_user():
    '''
        route pour gerer la creation des utilisateurs
    '''

    # données du formlaire de creation d'utilisateur
    data = request.get_json()

    # l'application se connecte a userhub

    return "ok"
