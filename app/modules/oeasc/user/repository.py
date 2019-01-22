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


def get_user_from_data(data):

    user_dict = as_dict(data)
    for d in data.app_users:
        u = as_dict(d)
        if u['id_application'] == config['ID_APP']:
            user_dict['id_droit_max'] = u['id_droit_max']

    if not user_dict.get('id_droit_max', None):
        return None

    # nb declaration
    data_nd = DB.engine.execute(
        text(
            "SELECT COUNT(*) FROM oeasc.t_declarations WHERE id_declarant=" + str(user_dict['id_role'])
        )
    ).first()

    if data_nd:
        print(data_nd, user_dict)
        user_dict['nb_declarations'] = data_nd[0]

    print('user_dict')

    return user_dict


def get_users():
    '''
        Retourne la liste des utilisateurs OEASC
        filtre selon l'utilisateur qui demande
    '''

    current_user = session['current_user']

    data = DB.session.query(User)
    v = [get_user_from_data(d) for d in data if get_user_from_data(d)]

    v_out = []

    for user in v:
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

    if not data:

        return None

    return get_user_from_data(data)


def get_user_form_email(email):
    '''
        Retourne l'utilisateur ayant pour id_role id_declarant
    '''

    data = DB.session.query(User).filter(User.email == email).first()
    if not data:
        return "None"

    return get_user_from_data(data)


def get_id_organismes(liste_nom):

    liste_nom_ = [nom.replace("'", "''") for nom in liste_nom]

    sql_text = "SELECT id_organisme \
        FROM utilisateurs.bib_organismes\
        WHERE nom_organisme in ('" + "','".join(liste_nom_) + "');"

    result = DB.engine.execute(text(sql_text))

    out = [res[0] for res in result]

    return out
