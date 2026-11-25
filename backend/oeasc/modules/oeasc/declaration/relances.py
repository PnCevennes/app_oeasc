"""
Suivi des relances automatiques des déclarations.

- interrupteur global (activer / désactiver la commande `flask send-relance`), stocké dans
  oeasc_declarations.t_parametres sous la clé "relances_auto_actives" ;
- historique des relances envoyées (oeasc_declarations.t_relances_declaration) ;
- liste affichée dans la page d'administration « Relances automatiques ».

Module sans dépendance sur mail.py / api.py pour éviter les imports circulaires.
"""

from datetime import datetime

from sqlalchemy import select, func, exists
from sqlalchemy.orm import aliased

from oeasc.utils.env import db as DB
from .models import (
    TDeclaration,
    TForet,
    TParametreDeclaration,
    TRelanceDeclaration,
)
from oeasc.modules.oeasc.user.models import VUsers
from .variables import get_variables_declaration

CLE_RELANCES_AUTO = "relances_auto_actives"


def get_relances_auto_actives():
    """True si les relances automatiques sont actives.
    Pas de ligne en base = DÉSACTIVÉES : après une installation, un administrateur doit
    les activer explicitement depuis Administration > Relances automatiques."""
    valeur = DB.session.execute(
        select(TParametreDeclaration.valeur).where(
            TParametreDeclaration.cle == CLE_RELANCES_AUTO
        )
    ).scalar_one_or_none()
    return valeur is not None and valeur.strip().lower() == "true"


def set_relances_auto_actives(actif):
    """Active (True) ou désactive (False) les relances automatiques."""
    param = DB.session.get(TParametreDeclaration, CLE_RELANCES_AUTO)
    valeur = "true" if actif else "false"
    if param is None:
        DB.session.add(TParametreDeclaration(cle=CLE_RELANCES_AUTO, valeur=valeur))
    else:
        param.valeur = valeur
    DB.session.commit()
    return actif


def enregistre_relance(id_declaration, statut_relance=None, manuelle=False):
    """Enregistre dans l'historique une relance envoyée.
    - automatique : statut_relance = statut de la déclaration après la relance
      (100 = relance n°1, 101 = n°2...) ;
    - manuelle (bouton de l'administrateur) : manuelle=True, pas de numéro.
    Ne commit pas : le commit est fait par l'appelant avec la mise à jour du statut."""
    numero = None
    if not manuelle:
        statut_base = get_variables_declaration()["STATUT_DECLARATION"]["Relance"]
        numero = int(statut_relance) - statut_base + 1
    DB.session.add(
        TRelanceDeclaration(
            id_declaration=int(id_declaration),
            numero_relance=numero,
            date_relance=datetime.now(),
            manuelle=bool(manuelle),
        )
    )


def get_liste_relances():
    """Une ligne par déclaration ayant reçu au moins une relance (automatique ou manuelle) :
    dernière relance (date), dernier numéro de relance automatique et nombre de relances
    restantes avant la clôture automatique (vides si seulement manuelles), nombre de relances
    manuelles, déclaration renouvelée / clôturée."""
    vars_declaration = get_variables_declaration()
    statut = vars_declaration["STATUT_DECLARATION"]
    nb_max = vars_declaration["NB_RELANCES_MAX"]

    # dernière relance de chaque déclaration
    derniere = (
        select(
            TRelanceDeclaration.id_declaration,
            func.max(TRelanceDeclaration.numero_relance).label("numero_relance"),
            func.max(TRelanceDeclaration.date_relance).label("date_relance"),
            func.count().filter(TRelanceDeclaration.manuelle).label("nb_manuelles"),
        )
        .group_by(TRelanceDeclaration.id_declaration)
        .subquery("derniere")
    )

    suivante = aliased(TDeclaration, name="suivante")
    renouvelee = exists().where(suivante.id_declaration_originale == TDeclaration.id_declaration)

    stmt = (
        select(
            TDeclaration.id_declaration,
            TDeclaration.statut,
            TDeclaration.date_fin,
            TForet.label_foret,
            VUsers.nom_complet.label("declarant"),
            derniere.c.numero_relance,
            derniere.c.date_relance,
            derniere.c.nb_manuelles,
            renouvelee.label("renouvelee"),
        )
        .join(derniere, derniere.c.id_declaration == TDeclaration.id_declaration)
        .join(TForet, TForet.id_foret == TDeclaration.id_foret)
        .outerjoin(VUsers, VUsers.id_role == TDeclaration.id_declarant)
        .order_by(derniere.c.date_relance.desc())
    )

    liste = []
    for row in DB.session.execute(stmt).mappings().all():
        archivee = row["statut"] in (
            statut["Archivée"],
            statut["Archivée sans réponse"],
        )
        # la clôture automatique a lieu au passage suivant la relance n° NB_RELANCES_MAX
        # (cf. send_mail_actualisation_declaration) : il reste NB_RELANCES_MAX - numéro relances
        numero = row["numero_relance"]
        restantes = None if numero is None else max(0, nb_max - numero)
        nb_manuelles = row["nb_manuelles"]
        if numero is None:
            libelle = "-"
        else:
            libelle = f"{numero} ({restantes})"
        liste.append(
            {
                "id_declaration": row["id_declaration"],
                "label_foret": row["label_foret"],
                "declarant": row["declarant"],
                "date_derniere_relance": row["date_relance"].strftime("%d/%m/%Y"),
                "numero_relance": numero,
                "relances_restantes": restantes,
                "libelle_relance": libelle,
                "nb_manuelles": nb_manuelles,
                "renouvelee": bool(row["renouvelee"]),
                "cloturee": archivee and not row["renouvelee"],
            }
        )
    return liste
