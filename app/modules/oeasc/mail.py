from flask_mail import Message

from app.utils.env import mail

from flask import (
    render_template, session
)

from config import config

from .repository import (
    get_user,
    f_create_or_update_declaration,
)

from .declaration_sample import declaration_dict_random_sample


def display_mail_test(destinataire):

    declaration = declaration_dict_random_sample()

    declaration = f_create_or_update_declaration(declaration)

    user = get_user(declaration['id_declarant'])

    email_user = user['email']

    return render_template('modules/oeasc/mail/validation_declaration.html', destinataire=destinataire, declaration=declaration, user=user)


def send_mail_test():

    declaration = declaration_dict_random_sample()

    declaration = f_create_or_update_declaration(declaration)

    return send_mail_validation_declaration(declaration)


def send_mail_validation_declaration(declaration):
    '''
        Evoie un email quand une declaration est validée
    '''
    user = get_user(session['current_user']['id_role'])

    email_user = user['email']

    print(user, declaration['id_declaration'])

    with mail.connect() as conn:

        msg = Message(
            '[OEASC] Votre déclaration a bien été prise en compte',
            sender=config.DEFAULT_MAIL_SENDER,
            recipients=[email_user])
        msg.html = render_template('modules/oeasc/mail/validation_declaration.html', destinataire='user', declaration=declaration, user=user)

        conn.send(msg)

        msg = Message(
            '[OEASC] Nouvelle déclaration',
            sender=config.DEFAULT_MAIL_SENDER,
            recipients=[config.MAIL_ANIMATEUR])
        msg.html = render_template('modules/oeasc/mail/validation_declaration.html', destinataire='animateur', declaration=declaration, user=user)

        conn.send(msg)
