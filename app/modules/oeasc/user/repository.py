"""
    fonction acces DB pour la partie user
"""

from flask import current_app, session
from sqlalchemy import text
from pypnusershub.db.models import User
from .models import VUsers

config = current_app.config
DB = config["DB"]


def get_liste_organismes_oeasc():
    """
    Retourne la liste des organisme concernés par l'OEASC
    """

    sql_text = text(
        "SELECT o.id_organisme, o.nom_organisme \
        FROM utilisateurs.bib_organismes o \
        JOIN oeasc_commons.t_liste_organismes t \
            ON t.id_organisme = o.id_organisme \
            ORDER BY o.nom_organisme;"
    )

    result = DB.engine.execute(sql_text)

    v = []
    autre = None
    for row in result:
        if row[1] != "Autre (préciser)":
            v.append({"id_organisme": row[0], "nom_organisme": row[1]})
        else:
            autre = {"id_organisme": row[0], "nom_organisme": row[1]}
    if autre:
        v.append(autre)

    return v


def get_users():
    """
    Retourne la liste des utilisateurs OEASC
    filtre selon l'utilisateur qui demande
    """

    v_out = []
    current_user = get_user(session.get("current_user", {}).get("id_role"))

    v = DB.session.query(VUsers).all()

    for user in v:
        if (
            current_user["id_droit_max"] >= 5
            or current_user["id_organisme"] == user.id_organisme
            and current_user["organisme"] == current_user["organisme"]
        ):
            user_dict = user.as_dict()
            v_out.append(user_dict)

    return v_out


def get_user(id_declarant=None):
    """
    Retourne l'utilisateur ayant pour id_role id_declarant
    """

    if not id_declarant:
        # return as_dict(User())
        return User().as_dict()

    data = DB.session.query(VUsers).filter(VUsers.id_role == id_declarant).first()

    if not data:
        return None

    user_dict = data.as_dict()

    return user_dict


def get_user_form_email(email):
    """
    Retourne l'utilisateur ayant pour id_role id_declarant
    """

    data = DB.session.query(User).filter(User.email == email).first()
    if not data:
        return "None"

    return get_user(data.id_role)


def get_id_organismes(liste_nom):
    """
    retourne une liste d'id à partir d'une liste de noms
    """
    liste_nom_ = [nom.replace("'", "''") for nom in liste_nom]

    sql_text = (
        "SELECT id_organisme \
        FROM utilisateurs.bib_organismes\
        WHERE nom_organisme in ('"
        + "','".join(liste_nom_)
        + "');"
    )

    result = DB.engine.execute(text(sql_text))

    out = [res[0] for res in result]

    return out
