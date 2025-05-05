"""
fonction acces DB pour la partie user
"""

from flask import current_app, session
from sqlalchemy import text, select, join
from sqlalchemy.orm import Session
from pypnusershub.db.models import User, Organisme
from ..commons.models import TListeOrganismes
from .models import VUsers

config = current_app.config
DB = config["DB"]


def get_liste_organismes_oeasc():
    """
    Retourne la liste des organisme concernés par l'OEASC
    """

    stmt_organismes = (
        select(Organisme.id_organisme, Organisme.nom_organisme)
        .join(
            TListeOrganismes,
            Organisme.id_organisme == TListeOrganismes.id_organisme,
        )
        .order_by(Organisme.nom_organisme)
    )
    result = DB.session.execute(stmt_organismes).all()


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
    stmt_v = (
        select(VUsers)
    )
    v = DB.session.execute(stmt_v).scalars().all()

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

    stmt_vusers = (
        select(VUsers)
        .where(VUsers.id_role == id_declarant)
        .limit(1)
    )
    data = DB.session.execute(stmt_vusers).scalars().first()


    if not data:
        return None

    user_dict = data.as_dict()

    return user_dict


def get_user_form_email(email):
    """
    Retourne l'utilisateur ayant pour id_role id_declarant
    """

    stmt_user_email = (
        select(User)
        .where(User.email == email)
        .limit(1)
    )
    data = DB.session.execute(stmt_user_email).scalars().first()

    if not data:
        return "None"

    return get_user(data.id_role)


def get_id_organismes(liste_nom):
    """
    retourne une liste d'id à partir d'une liste de noms
    """
    liste_nom_ = [nom.replace("'", "''") for nom in liste_nom]


    stmt_organisme = (
        select(Organisme.id_organisme)
        .where(Organisme.nom_organisme.in_(liste_nom_))
    )
    out = DB.session.execute(stmt_organisme).scalars().all()
    # out = [res for res in out]
    return out
