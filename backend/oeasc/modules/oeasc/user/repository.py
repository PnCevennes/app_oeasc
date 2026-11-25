"""
fonction acces DB pour la partie user
"""

from flask import current_app, session
from oeasc.utils.current_user import get_current_user
from sqlalchemy import select, func

# from sqlalchemy.orm import Session
from pypnusershub.db.models import User, Organisme
from pypnusershub.schemas import UserSchema
from ..commons.models import TListeOrganismes

# from ..commons.schema import TListeOrganismesSchema
from .models import VUsers
from .schema import VUsersShema

from oeasc.utils.env import db as DB


def get_liste_organismes_oeasc():
    """
    Retourne la liste des organisme concernés par l'OEASC
    Cette fonction est utilisée pour obtenir la liste des organismes qui sont liés à l'OEASC,
    en effectuant une jointure entre la table Organisme et TListeOrganismes.
    Elle trie les organismes par nom et place l'organisme "Autre (préciser)" à la fin de la liste.
    """

    # Création de la requête SQL pour sélectionner les id et noms des organismes
    stmt_organismes = (
        select(Organisme.id_organisme, Organisme.nom_organisme)
        .join(
            TListeOrganismes,
            Organisme.id_organisme == TListeOrganismes.id_organisme,
        )
        .order_by(Organisme.nom_organisme)
    )
    # Exécution de la requête et récupération des résultats
    result = DB.session.execute(stmt_organismes).all()

    v = []
    autre = None
    # Parcours des résultats pour séparer "Autre (préciser)" des autres organismes
    for row in result:
        if row[1] != "Autre (préciser)":
            v.append({"id_organisme": row[0], "nom_organisme": row[1]})
        else:
            autre = {"id_organisme": row[0], "nom_organisme": row[1]}
    # Ajout de "Autre (préciser)" à la fin de la liste si présent
    if autre:
        v.append(autre)

    # Retourne la liste finale des organismes
    return v


def get_users():
    """
    Retourne la liste des utilisateurs OEASC.
    Cette fonction filtre les utilisateurs selon les droits et l'organisme de l'utilisateur courant.
    Elle est typiquement utilisée pour afficher la liste des utilisateurs dans l'interface d'administration,
    en respectant les droits d'accès de l'utilisateur connecté.
    """

    v_out = []  # Liste qui contiendra les utilisateurs filtrés à retourner

    # Récupère l'utilisateur courant à partir de la session (id_role)
    # (pas de current_user en session pour un utilisateur temporaire, ex: renouvellement par token)
    id_role = get_current_user().get("id_role")
    current_user = get_user(id_role) if id_role else None
    if not current_user:
        return v_out

    # Prépare la requête pour récupérer tous les utilisateurs de la vue VUsers
    stmt_v = select(VUsers)
    # Exécute la requête et récupère tous les utilisateurs
    v = DB.session.execute(stmt_v).scalars().all()

    # Parcours tous les utilisateurs récupérés
    for user in v:
        # Filtre selon les droits :
        # - Si l'utilisateur courant a un droit max >= 5 (admin ou super utilisateur)
        # - OU si l'utilisateur courant appartient au même organisme que l'utilisateur parcouru
        #   et que le nom de l'organisme correspond (double vérification)
        if current_user["id_droit_max"] >= 5 or (
            current_user["id_organisme"] == user.id_organisme
            and current_user["organisme"] == user.organisme
        ):
            # Sérialise l'utilisateur avec le schéma VUsersShema
            user_dict = VUsersShema().dump(user)
            v_out.append(user_dict)  # Ajoute l'utilisateur filtré à la liste de sortie

    # Retourne la liste des utilisateurs filtrés
    return v_out


def get_user(id_declarant=None):
    """
    Retourne l'utilisateur ayant pour id_role id_declarant.
    Cette fonction est utilisée pour récupérer les informations d'un utilisateur spécifique
    à partir de son identifiant de rôle (id_role). Elle est typiquement appelée lors de la
    connexion d'un utilisateur, ou pour afficher/modifier ses informations dans l'interface.
    """

    if not id_declarant:
        # Si aucun id_declarant n'est fourni, retourne un utilisateur vide sérialisé.
        # Utile pour initialiser un formulaire ou gérer le cas où aucun utilisateur n'est sélectionné.
        return UserSchema().dump(User())

    # Prépare la requête pour récupérer l'utilisateur dans la vue VUsers selon son id_role.
    stmt_vusers = select(VUsers).where(VUsers.id_role == id_declarant).limit(1)
    # Exécute la requête et récupère le premier résultat.
    data = DB.session.execute(stmt_vusers).scalars().first()

    if not data:
        # Si aucun utilisateur n'est trouvé, retourne None.
        # Permet de gérer le cas où l'id_role n'existe pas en base.
        return None

    # Sérialise l'utilisateur trouvé avec le schéma VUsersShema.
    user_dict = VUsersShema().dump(data)

    # Retourne le dictionnaire représentant l'utilisateur.
    return user_dict


def get_user_form_email(email):
    """
    Retourne l'utilisateur ayant pour email donné.
    Cette fonction permet de récupérer les informations d'un utilisateur à partir de son adresse email.
    Elle est typiquement utilisée lors de la connexion, de la récupération de mot de passe, ou pour
    vérifier l'existence d'un utilisateur dans la base à partir de son email.
    """

    # Prépare la requête pour sélectionner l'utilisateur dont l'email correspond à celui fourni
    stmt_user_email = (
        select(User)
        .where(User.email == email)
        .limit(1)  # Limite à un seul résultat (le premier trouvé)
    )
    # Exécute la requête et récupère le premier utilisateur correspondant
    data = DB.session.execute(stmt_user_email).scalars().first()

    if not data:
        # Si aucun utilisateur n'est trouvé avec cet email, retourne "None"
        # Permet de gérer le cas où l'email n'existe pas en base
        return "None"

    # Si un utilisateur est trouvé, récupère ses informations détaillées via son id_role
    # Utilise la fonction get_user pour sérialiser et retourner l'utilisateur
    return get_user(data.id_role)


def get_id_organismes(liste_nom):
    """
    Retourne une liste d'identifiants d'organismes à partir d'une liste de noms d'organismes.
    Cette fonction est utile lorsqu'on souhaite récupérer les id_organisme correspondant à une sélection
    de noms, par exemple pour filtrer des utilisateurs ou des données selon certains organismes.
    Elle est typiquement utilisée dans les cas où l'on dispose d'une liste de noms d'organismes
    (par exemple sélectionnés dans un formulaire ou issus d'une autre requête) et que l'on a besoin
    de leurs identifiants pour effectuer des opérations en base de données.
    """

    # Remplace les apostrophes simples par des doubles dans les noms pour éviter les erreurs SQL
    # (sécurisation basique contre les problèmes d'apostrophe dans les noms)
    liste_nom_ = [nom.replace("'", "''") for nom in liste_nom]

    # Prépare la requête SQL pour sélectionner les id_organisme dont le nom figure dans la liste
    stmt_organisme = select(Organisme.id_organisme).where(
        Organisme.nom_organisme.in_(liste_nom_)
    )

    # Exécute la requête et récupère tous les identifiants correspondants
    out = DB.session.execute(stmt_organisme).scalars().all()

    # Retourne la liste des id_organisme trouvés
    return out


def admin_update_user(id_role, data, current_id_role):
    """
    Met à jour par un administrateur l'email, l'organisme et/ou le rôle (desc_role) d'un utilisateur.
    L'email est aussi l'identifiant de connexion : les deux champs sont modifiés ensemble
    dans utilisateurs.t_roles (base locale).

    Retourne (utilisateur_mis_à_jour, None) ou (None, (message, code_http)).
    """
    target = get_user(id_role)
    caller = get_user(current_id_role)
    if not target:
        return None, ("Utilisateur introuvable", 404)
    if not caller or caller["id_droit_max"] < 4 or caller["id_droit_max"] <= target["id_droit_max"]:
        return None, ("Droits insuffisants pour modifier cet utilisateur", 403)

    user = DB.session.get(User, id_role)

    if "email" in data:
        email = (data["email"] or "").strip()
        if not email or "@" not in email:
            return None, ("Adresse e-mail invalide", 400)
        doublon = DB.session.execute(
            select(User.id_role).where(
                User.id_role != id_role,
                (func.lower(User.email) == email.lower())
                | (func.lower(User.identifiant) == email.lower()),
            )
        ).first()
        if doublon:
            return None, ("Cette adresse e-mail est déjà utilisée par un autre compte", 400)
        user.email = email
        user.identifiant = email  # l'e-mail sert d'identifiant de connexion

    if "id_organisme" in data:
        organisme = DB.session.get(Organisme, data["id_organisme"])
        if not organisme:
            return None, ("Organisme inconnu", 400)
        user.id_organisme = organisme.id_organisme
        champs = dict(user.champs_addi or {})
        if "Autre" in (organisme.nom_organisme or "") and data.get("autre_organisme"):
            champs["organisme"] = data["autre_organisme"]
        else:
            champs.pop("organisme", None)
        user.champs_addi = champs

    if "desc_role" in data:
        user.desc_role = data["desc_role"]

    DB.session.commit()
    return get_user(id_role), None
