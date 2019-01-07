from flask import current_app, session
from sqlalchemy import text
from pypnusershub.db.models import User, AppUser
from app.utils.utilssqlalchemy import as_dict


config = current_app.config
DB = config['DB']


def get_liste_organismes_oeasc():
    '''
        Retourne la liste des organisme concernés par l'OEASC
    '''

    sql_text = text("SELECT b.id_organisme, b.nom_organisme \
  FROM utilisateurs.cor_organism_tag as c, utilisateurs.bib_organismes as b, utilisateurs.t_tags as t \
  WHERE c.id_tag = t.id_tag AND b.id_organisme = c.id_organism AND t.tag_code = 'ORG_OEASC' \
  ORDER BY b.nom_organisme;")

    result = DB.engine.execute(sql_text)

    v = []
    for row in result:
        if row[1] != "Autre (préciser)":
            v.append({'id_organism': row[0], 'nom_organisme': row[1]})
        else:
            autre = {'id_organism': row[0], 'nom_organisme': row[1]}
    v.append(autre)

    return v


def get_users():
    '''
        Retourne la liste des utilisateurs OEASC
        filtre selon l'utilisateur qui demande
    '''

    current_user = session['current_user']

    data = DB.session.query(User)
    v = [as_dict(d) for d in data]

    data_app = DB.session.query(AppUser).filter(AppUser.id_application == config['ID_APP'])
    v_app = [as_dict(d) for d in data_app]

    v_out = []

    for user in v:
        for user_app in v_app:
            if user['id_role'] == user_app['id_role']:
                user['id_droit_max'] = user_app['id_droit_max']
                user['id_application'] = user_app['id_application']
                if(current_user['id_droit_max'] >= 5 or (current_user['id_organisme'] == user['id_organisme'])):
                    v_out.append(user)

    return v_out


def get_user(id_declarant=None):
    '''
        Retourne l'utilisateur ayant pour id_role id_declarant
    '''

    if not id_declarant:
        return as_dict(User())

    data = DB.session.query(User).filter(User.id_role == id_declarant).first()
    data_app = DB.session.query(AppUser).filter(id_declarant == AppUser.id_role).first()

    if not data or not data_app:

        return None

    user = as_dict(data)
    user_app = as_dict(data_app)

    user['id_droit_max'] = user_app['id_droit_max']
    user['id_application'] = user_app['id_application']

    return user


def get_id_organismes(liste_nom):

    liste_nom_ = [nom.replace("'", "''") for nom in liste_nom]

    sql_text = "SELECT id_organisme \
        FROM utilisateurs.bib_organismes\
        WHERE nom_organisme in ('" + "','".join(liste_nom_) + "');"

    result = DB.engine.execute(text(sql_text))

    out = [res[0] for res in result]

    return out
