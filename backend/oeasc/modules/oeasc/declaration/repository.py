"""
Fonctions de traitement de données pour les déclarations
"""

from oeasc.utils.apiResponse import ApiResponse
from datetime import datetime, date, timedelta
from sqlalchemy import (
    false,
    select,
    text,
    and_,
)
import json
from flask import current_app, session

from oeasc.modules.oeasc.declaration.models import (
    TDeclaration,
    TForet,
)
from oeasc.modules.oeasc.user.models import VUsers

from .schema import (
    TDeclarationSchema,
    TForetSchema,
)
from .variables import get_variables_declaration
from .all_stmt import (
    get_stmt_liste_declaration,
    stmt_one_declaration_a_renouveler,
    get_stmt_fiche_declaration,
    get_stmt_degats,
)
from oeasc.modules.oeasc.nomenclature import (
    get_area_from_id,
    get_nomenclature_from_id,
    get_nomenclature,
)
from oeasc.modules.oeasc.user.repository import get_user, get_id_organismes

config = current_app.config
DB = config["DB"]


def get_config():
    return current_app.config


def get_db():
    return get_config()["DB"]


def get_label_statut_declaration(code_statut):
    """Récupère le label d'un statut de déclaration depuis le fichier JSON de configuration."""
    declaration_variables = get_variables_declaration()
    # "STATUT_DECLARATION" : {
    #     "Non validée": 0,
    #     "Active": 1,
    #     "Archivée": 2,
    #     "Archivée sans réponse": 3,
    #     "Relance": 100
    # },

    label = None

    if code_statut >= declaration_variables["STATUT_DECLARATION"]["Relance"]:
        label = "Relance numéro " + str(
            code_statut - declaration_variables["STATUT_DECLARATION"]["Relance"] + 1
        )
        return label
    for label_statut, code in declaration_variables["STATUT_DECLARATION"].items():
        if code == code_statut:
            label = label_statut
            break
    return label


def get_fiche_declaration(id_declaration, type_export=None, session=None):
    """Les données pour l'affichage d'une déclaration. Page voir_declaration."""

    response = ApiResponse(log_file="declarations.log", session=session)
    user = session.get("current_user", None) if session else None
    if user == None:
        response.add_error(
            user_message="Utilisateur non authentifié",
            system_error="Aucun utilisateur dans la session",
            status_code=401,
        )
        return response

    stmt = get_stmt_fiche_declaration(id_declaration)

    # Restriction selon les droits de l'utilisateur
    for filtre in get_filtres_droits_declarations(user):
        stmt = stmt.where(filtre)

    result = get_db().session.execute(stmt).fetchone()

    if result is None:
        dict_result = {}
        dict_result["id_declaration"] = id_declaration
        dict_result["degats"] = []
    else:
        # Use the RowMapping to get a dict keyed by column labels

        dict_result = dict(result._mapping)

        dict_result["statut_label"] = get_label_statut_declaration(
            dict_result["statut"]
        )

        stmt_degats = get_stmt_degats(id_declaration)
        degats_declarations = get_db().session.execute(stmt_degats).fetchall()

        # on rassemble tous les dégats essence qui ont le même id_degat
        degats_dict = {}
        for degat in degats_declarations:
            degat = dict(degat._mapping)
            id_degat = degat["id_degat"]
            if id_degat not in degats_dict:
                degats_dict[id_degat] = {
                    "id_declaration_degat": degat["id_declaration_degat"],
                    "id_degat": id_degat,
                    "degat_type_mnemo": degat["degat_type_mnemo"],
                    "degat_type_label": degat["degat_type_label"],
                    "degat_type_code": degat["degat_type_code"],
                    "essences": [],
                }
            if degat["id_degat_essence"] is not None:
                degats_dict[id_degat]["essences"].append(
                    {
                        "id_degat_essence": degat["id_degat_essence"],
                        "degat_essence_mnemo": degat["degat_essence_mnemo"],
                        "degat_gravite_mnemo": degat["degat_gravite_mnemo"],
                        "degat_etendue_mnemo": degat["degat_etendue_mnemo"],
                        "degat_anteriorite_mnemo": degat["degat_anteriorite_mnemo"],
                        "degat_essence_label": degat["degat_essence_label"],
                        "degat_gravite_label": degat["degat_gravite_label"],
                        "degat_etendue_label": degat["degat_etendue_label"],
                        "degat_anteriorite_label": degat["degat_anteriorite_label"],
                        "degat_essence_code": degat["degat_essence_code"],
                        "degat_gravite_code": degat["degat_gravite_code"],
                        "degat_etendue_code": degat["degat_etendue_code"],
                        "degat_anteriorite_code": degat["degat_anteriorite_code"],
                    }
                )

        dict_result["degats"] = list(degats_dict.values())

        response.data = dict_result

    return response


def get_form_declaration(id_declaration=None, session={}):
    """
    Récupère toutes les informations pour afficher les formulaire de déclaration. Pour la création, modification et renouvellement.
    Si aucun id n'est spécifié on retourne les schémas vides.
    """
    apiResponse = ApiResponse(log_file="declarations.log", session=session)
    if not id_declaration:
        schemaDeclaration = TDeclarationSchema()
        apiResponse.data = schemaDeclaration.dump(TDeclaration())
        return apiResponse

    # Récupère la déclaration, la forêt et le propriétaire associés à l'identifiant donné
    declaration, foret, proprietaire = get_declaration(id_declaration)
    # Si aucune déclaration n'est trouvée, retourne une réponse vide
    if not declaration:
        apiResponse.add_error(
            user_message="Déclaration non trouvée",
            system_error=f"Aucune déclaration trouvée pour l'id {id_declaration}",
            status_code=200,
        )
        return apiResponse

    # Sérialise l'objet déclaration en dictionnaire
    declaration_dict = TDeclarationSchema().dump(declaration)

    # Sérialise l'objet forêt en dictionnaire et fusionne avec la déclaration
    foret_dict = TForetSchema().dump(foret) if foret else {}
    # Renommage des champs propriétaire de t_forets vers les noms attendus par le frontend
    foret_dict["telephone"] = foret_dict.pop("tel_proprietaire", None)
    foret_dict["email"] = foret_dict.pop("email_proprietaire", None)
    foret_dict["adresse"] = foret_dict.pop("adresse_proprietaire", None)
    foret_dict["s_commune_proprietaire"] = foret_dict.pop("commune_proprietaire", None)
    foret_dict["s_code_postal"] = foret_dict.pop("cp_proprietaire", None)
    declaration_dict.update(foret_dict)

    # Ajoute l'identifiant du déclarant dans le dictionnaire de la déclaration
    id_declarant = declaration.id_declarant
    declaration_dict["id_declarant"] = id_declarant

    # Pour chaque clé du dictionnaire, si la valeur est une liste d'objets contenant "id_nomenclature",
    # on transforme cette liste en une liste d'identifiants de nomenclature uniquement.
    # Cela permet de simplifier la structure des données retournées.

    for key in declaration_dict:
        if key == "centroid":  # les centroid sont en array et non en list
            declaration_dict[key] = {
                "x": declaration_dict[key][0],
                "y": declaration_dict[key][1],
            }
        else:  # pour les list on applatit les nomenclatures
            if (
                isinstance(declaration_dict[key], list)
                and len(declaration_dict[key]) > 0
                and "id_nomenclature" in declaration_dict[key][0]
            ):
                # regroupe les id_nomenclature dans une liste simple.
                declaration_dict[key] = [
                    e["id_nomenclature"] for e in declaration_dict[key]
                ]

    # Récupère et classe les zones ("areas") de la forêt selon leur type
    areas_foret = [
        get_area_from_id(area["id_area"])
        for area in declaration_dict.get("areas_foret", [])
    ]
    declaration_dict["areas_foret_onf"] = get_id_area(areas_foret, ["OEASC_ONF_FRT"])
    declaration_dict["areas_foret_dgd"] = get_id_area(areas_foret, ["OEASC_DGD"])
    declaration_dict["areas_foret_communes"] = get_id_areas(
        areas_foret, ["OEASC_COMMUNE"]
    )
    declaration_dict["areas_foret_sections"] = get_id_areas(
        areas_foret, ["OEASC_SECTION"]
    )

    # Récupère et classe les zones ("areas") de la déclaration selon leur type
    areas_localisation = [
        get_area_from_id(area["id_area"])
        for area in declaration_dict.get("areas_localisation", [])
    ]
    declaration_dict["areas_localisation_cadastre"] = get_id_areas(
        areas_localisation, ["OEASC_CADASTRE"]
    )
    declaration_dict["areas_localisation_onf_prf"] = get_id_areas(
        areas_localisation, ["OEASC_ONF_PRF"]
    )
    declaration_dict["areas_localisation_onf_ug"] = get_id_areas(
        areas_localisation, ["OEASC_ONF_UG"]
    )
    declaration_dict["areas_localisation"] = [
        a for a in areas_localisation if a is not None
    ]

    # Cache les informations personnelles du propriétaire si l'utilisateur n'est pas le déclarant
    # ou si son niveau d'accès est inférieur à 4 (donc pas administrateur).
    # Ceci permet de protéger la vie privée du propriétaire.
    if session is not None:
        current_user = session.get("current_user", None)
        if (
            (current_user is not None)
            and (current_user["max_level_profil"] < 4)
            and (current_user["id_role"] != declaration_dict["id_declarant"])
        ):
            hide_proprietaire(declaration_dict)

    # Retourne le dictionnaire de la déclaration complète au format JSON
    apiResponse.data = declaration_dict
    return apiResponse


def create_or_update_declaration(post_data):
    """
    Fonction principale pour la création ou la modification d'une déclaration de dégât en forêt.
    Elle adapte les données reçues (post_data) pour les rendre compatibles avec les schémas Marshmallow,
    puis crée ou met à jour les instances en base (propriétaire, forêt, déclaration).

    Utilisation :
    - Cette fonction est appelée lors de la soumission ou modification d'un formulaire de déclaration.
    - Elle gère les cas de création de nouveaux propriétaires/forêts (petits propriétaires) ou la sélection
      d'une forêt existante (gestion durable).
    """

    response = ApiResponse(log_file="declarations.log", session=session)

    # arranged_post_data ne contiendra que les champs nécessaires à la création/modification de la déclaration, adaptés pour Marshmallow
    # Champs de la déclaration repris tels quels depuis post_data
    CHAMPS_DECLARATION = (
        "id_declarant",
        "id_foret",
        "id_nomenclature_peuplement_type",
        "id_nomenclature_peuplement_acces",
        "id_nomenclature_peuplement_essence_principale",
        "meta_create_date",
        "b_peuplement_protection_existence",
        "b_peuplement_paturage_presence",
        "b_autorisation",
        "b_valid",
        "id_nomenclature_proprietaire_declarant",
        "id_nomenclature_peuplement_origine",
        "id_nomenclature_foret_type",
        "id_nomenclature_peuplement_paturage_frequence",
        "id_nomenclature_peuplement_paturage_statut",
        "peuplement_surface",
        "autre_protection",
        "precision_localisation",
        "commentaire",
        "degats",
        "id_declaration_originale",
        "date_fin",
        "statut",
        "token_renouvellement",
        "date_fin_token",
    )
    arranged_post_data = {champ: post_data.get(champ) for champ in CHAMPS_DECLARATION}
    arranged_post_data["meta_update_date"] = None  # sera mis à jour dans la bdd

    # Gestion des relations de nomenclatures : on adapte le format pour Marshmallow
    # Chaque clé "nomenclatures_*" devient une liste de dictionnaires avec l'id de la nomenclature
    for key in post_data:
        if "nomenclatures_" in key:
            arranged_post_data[key] = [
                {
                    # "id_declaration": post_data.get("id_declaration"),
                    "id_nomenclature": id_nomenclature,
                }
                for id_nomenclature in post_data[key]
            ]

    # Regroupement des zones de localisation (aires) pour la déclaration
    post_data["areas_localisation"] = (
        []
        + post_data["areas_localisation_cadastre"]
        + post_data["areas_localisation_onf_prf"]
        + post_data["areas_localisation_onf_ug"]
    )
    # suppression des éventuels doublons
    post_data["areas_localisation"] = list(set(post_data["areas_localisation"]))

    # On adapte le format des aires pour Marshmallow (sans id_declaration)
    arranged_post_data["areas_localisation"] = [
        {"id_area": id_area} for id_area in post_data["areas_localisation"]
    ]

    # Cas 1 : La parcelle n'a pas de document de gestion durable (petit propriétaire)
    # On crée ou met à jour la forêt avec les données propriétaire directement
    if not post_data["b_document"]:

        # On récupère la nomenclature du propriétaire déclarant
        nomenclature = post_data[
            "id_nomenclature_proprietaire_declarant"
        ] and get_nomenclature_from_id(
            post_data["id_nomenclature_proprietaire_declarant"]
        )

        # Si la nomenclature n'est pas "P_D_O_NP", on retire le déclarant
        if nomenclature and nomenclature["cd_nomenclature"] != "P_D_O_NP":
            post_data["id_declarant"] = None

        try:
            new_foret = create_or_update_foret(post_data)
        except Exception as e:
            DB.session.rollback()
            response.add_error(
                user_message="Erreur lors de la création/modification de la forêt",
                system_error=str(e),
                status_code=200,
            )
            return arranged_post_data, response

        arranged_post_data["id_foret"] = new_foret.id_foret

    else:
        # Cas 2 : La parcelle a un document de gestion durable (forêt existante)
        # On récupère la forêt existante à partir de l'aire de forêt sélectionnée.
        id_area_foret = (
            post_data.get("areas_foret_onf")
            if post_data.get("b_statut_public") == True
            else post_data.get("areas_foret_dgd")
        )

        if not id_area_foret:
            # La forêt n'est pas modifiable dans le formulaire lorsqu'il y a un
            # document de gestion durable. En modification, si le frontend n'a pas
            # fourni l'aire de forêt (ex : cor_areas_forets incomplet après un
            # refresh ref_geo, l'intersect ne retrouve plus la forêt parente), on
            # conserve la forêt déjà rattachée à la déclaration.
            if post_data.get("id_foret"):
                arranged_post_data["id_foret"] = post_data["id_foret"]
            else:
                response.add_error(
                    user_message="Aire de forêt manquante pour les forêts avec document de gestion durable",
                    status_code=200,
                )
                return arranged_post_data, response
        else:
            code_foret = get_area_from_id(id_area_foret)["area_code"]

            try:
                foret = (
                    DB.session.execute(
                        select(TForet.id_foret)
                        .where(TForet.code_foret == code_foret)
                        .limit(1)
                    )
                    .scalars()
                    .first()
                )
            except Exception as e:
                DB.session.rollback()
                response.add_error(
                    user_message="Erreur lors de la récupération de la forêt existante",
                    system_error=str(e),
                    status_code=200,
                )
                return arranged_post_data, response
            arranged_post_data["id_foret"] = foret

    # Création ou modification de la déclaration
    declarationSchema = TDeclarationSchema()

    # Si modification d'une déclaration existante
    if post_data.get("id_declaration"):
        arranged_post_data["id_declaration"] = post_data.get("id_declaration")
        declaration_bdd = DB.session.get(TDeclaration, post_data.get("id_declaration"))

        declaration = declarationSchema.load(
            arranged_post_data,
            instance=declaration_bdd,
            partial=True,  # Mise à jour partielle
            session=DB.session,
        )
        # declaration.degats = arranged_post_data.get("degats", [])
    else:
        # Création d'une nouvelle déclaration

        # Calcule la date de fin de validité si elle n'est pas fournie par l'appelant
        # (le formulaire de création ne l'envoie pas ; le renouvellement la fournit déjà).
        if not arranged_post_data.get("date_fin"):
            variables_declaration = get_variables_declaration()
            nb_jours_validite = variables_declaration.get(
                "NB_JOURS_VALIDITE_DECLARATION"
            )
            if nb_jours_validite:
                arranged_post_data["date_fin"] = str(
                    datetime.now().date() + timedelta(days=nb_jours_validite)
                )

        # Statut par défaut d'une nouvelle déclaration : "Non validée" (en attente de validation)
        if arranged_post_data.get("statut") is None:
            arranged_post_data["statut"] = get_variables_declaration()[
                "STATUT_DECLARATION"
            ]["Non validée"]

        declaration = declarationSchema.load(
            arranged_post_data, session=DB.session, partial=True
        )
        DB.session.add(declaration)

    try:
        DB.session.commit()
    except Exception as e:
        DB.session.rollback()
        response.add_error(
            user_message="Erreur lors de la création/modification de la déclaration",
            system_error=str(e),
            status_code=200,
        )
        return arranged_post_data, response

    # On renseigne l'id réel de la déclaration (création comme modification) :
    # en modification, le frontend n'envoie pas toujours id_declaration dans le
    # post_data, et les consommateurs du retour (envoi de mail, réponse frontend)
    # en ont besoin.
    arranged_post_data["id_declaration"] = declaration.id_declaration

    # Mise à jour des aires liées à la déclaration (communes, secteurs, sections)
    try:
        patch_areas_declarations(declaration.id_declaration)
    except Exception as e:
        DB.session.rollback()
        return arranged_post_data, response.add_error(
            user_message="Erreur lors de la mise à jour des aires liées à la déclaration",
            system_error=str(e),
            status_code=200,
        )

    # On retourne les données arrangées (utiles pour debug ou pour affichage)
    response.data = declarationSchema.dump(declaration)
    return arranged_post_data, response


def create_or_update_foret(post_data):
    """
    Fonction pour créer ou mettre à jour une forêt avec ses données propriétaire.
    Utilisée dans le cas où la déclaration concerne un petit propriétaire sans document de gestion durable.

    Args:
        post_data (dict): Dictionnaire contenant les données de la déclaration, y compris les informations de la forêt et du propriétaire.
    Returns:
        TForet: Instance de la forêt créée ou mise à jour.
    """

    # Formatage du téléphone si présent
    telephone = post_data.get("telephone")
    if telephone:
        telephone = telephone.replace(" ", "").replace("-", "")
        telephone = " ".join(
            [telephone[i : i + 2] for i in range(0, len(telephone), 2)]
        )

    # Préparation des données de la forêt à partir de post_data
    data_foret = {}
    data_foret["b_statut_public"] = post_data.get("b_statut_public")
    data_foret["b_document"] = post_data.get("b_document")
    # Données propriétaire stockées directement dans t_forets
    data_foret["nom_proprietaire"] = post_data.get("nom_proprietaire")
    data_foret["tel_proprietaire"] = telephone
    data_foret["email_proprietaire"] = post_data.get("email")
    data_foret["adresse_proprietaire"] = post_data.get("adresse")
    data_foret["commune_proprietaire"] = post_data.get("s_commune_proprietaire")
    data_foret["cp_proprietaire"] = post_data.get("s_code_postal")
    id_nomenclature_proprietaire_type = post_data.get(
        "id_nomenclature_proprietaire_type"
    )
    if not id_nomenclature_proprietaire_type:
        # Par défaut, type "Privé"
        nomenclature_prive = get_nomenclature(
            "cd_nomenclature", "PT_PRI", "OEASC_PROPRIETAIRE_TYPE"
        )
        if nomenclature_prive:
            id_nomenclature_proprietaire_type = nomenclature_prive["id_nomenclature"]
    data_foret["id_nomenclature_proprietaire_type"] = id_nomenclature_proprietaire_type
    data_foret["id_declarant"] = post_data.get("id_declarant")
    data_foret["nom_foret"] = post_data.get("nom_foret")
    data_foret["code_foret"] = post_data.get("code_foret")
    data_foret["label_foret"] = post_data.get("label_foret")
    data_foret["surface_calculee"] = post_data.get("surface_calculee")
    data_foret["surface_renseignee"] = post_data.get("surface_renseignee")

    # Regroupement des aires de la forêt
    post_data["areas_foret"] = (
        [] + post_data["areas_foret_communes"] + post_data["areas_foret_sections"]
    )
    if post_data["areas_foret_onf"]:
        post_data["areas_foret"].append(post_data["areas_foret_onf"])
    if post_data["areas_foret_dgd"]:
        post_data["areas_foret"].append(post_data["areas_foret_dgd"])

    data_foret["areas_foret"] = [
        {"id_area": id_area}
        for id_area in post_data.get("areas_foret", [])
        if id_area is not None
    ]

    # Création ou modification de la forêt
    foretSchema = TForetSchema()

    # Si modification d'une forêt existante
    if post_data.get("id_foret"):
        data_foret["id_foret"] = post_data.get("id_foret")
        foret_bdd = DB.session.get(TForet, post_data.get("id_foret"))

        foret = foretSchema.load(
            data_foret,
            instance=foret_bdd,
            partial=True,  # Mise à jour partielle
            session=DB.session,
        )
        DB.session.commit()  # modification de l'instance

    else:
        # Création d'une nouvelle forêt
        foret = foretSchema.load(data_foret, session=DB.session, partial=True)
        DB.session.add(foret)
        DB.session.commit()  # ajout de l'instance
        post_data["id_foret"] = foret.id_foret

    return foret


def check_token_renouvellement_declaration(id_declaration, token, session={}):
    """
    Vérifie la validité d'un token de renouvellement de déclaration.
    Utilisée pour sécuriser l'accès à certaines fonctionnalités liées aux déclarations,
    par exemple lors de la consultation ou de la modification d'une déclaration spécifique.
    """
    response = ApiResponse(log_file="declarations.log", session=session)

    # Récupère le token de déclaration depuis les paramètres de la requête
    if not token:
        response.add_error(
            user_message="Token manquant dans la requête", status_code=200
        )
        return response
    if not id_declaration:
        response.add_error(
            user_message="ID de déclaration manquant dans la requête", status_code=200
        )
        return response

    stmt = stmt_one_declaration_a_renouveler(id_declaration)
    result = DB.session.execute(stmt).fetchone()
    if not result:
        response.add_error(user_message="Déclaration non trouvée", status_code=200)
        return response

    # Normalize row access to a mapping/dict for safety across SQLAlchemy versions
    row = result._mapping if hasattr(result, "_mapping") else dict(result)
    token_renouvellement = row.get("token_renouvellement")
    date_fin_token = row.get("date_fin_token")

    if token_renouvellement is None:
        response.add_error(
            user_message="Cette déclaration n'a pas de token de renouvellement",
            status_code=200,
        )
        return response
    if date_fin_token is None:
        response.add_error(
            user_message="Cette déclaration n'a pas de date de fin de token",
            status_code=200,
        )
        return response

    now = datetime.now()
    # If date_fin_token is a date (not datetime), convert to datetime for a proper comparison
    if isinstance(date_fin_token, date) and not isinstance(date_fin_token, datetime):
        date_fin_token = datetime.combine(date_fin_token, datetime.max.time())

    if now > date_fin_token:
        response.add_error(
            system_error="Le lien a expiré",
            user_message="Le lien a expiré",
            status_code=200,
        )
        return response
    if token != token_renouvellement:
        response.add_error(
            system_error="Token invalide",
            user_message="Token invalide",
            status_code=200,
        )
        return response
    else:
        response.add_log(message="Token valide", type_log="INFO")
        return response


######################################################################################
######################################################################################


def get_filtres_droits_declarations(user):
    """
    Clauses SQLAlchemy qui restreignent les déclarations visibles selon les droits de l'utilisateur.
    Utilisée par la liste et la fiche de déclaration (requêtes jointes sur VUsers).

    - droit >= 5 (animateur, administrateur) : toutes les déclarations (pas de filtre)
    - droit >= 2 et organisme "réel" (pas un particulier) : les déclarations de son organisme
    - droit >= 1 : ses propres déclarations
    - sinon, ou sans utilisateur : aucune déclaration

    :param user: dictionnaire de l'utilisateur (droits, organisme, id_role), ou None
    :return: liste de clauses (vide = pas de restriction)
    """
    if not user:
        return [false()]

    niveau = user.get("max_level_profil", user.get("id_droit_max")) or 0

    if niveau >= 5:
        return []

    if niveau >= 2:
        # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
        liste_id_organismes_solo = get_id_organismes(
            ["Autre (préciser)", "Pas d'organisme", "Aucun"]
        )
        if user["id_organisme"] not in liste_id_organismes_solo:
            return [VUsers.organisme == user["organisme"]]

    if niveau >= 1:
        return [TDeclaration.id_declarant == user["id_role"]]

    return [false()]


# Pour la liste des déclarations (page système d'alertes => alertes signalées)
def get_liste_declarations(filters=None, user=None, id_declaration=None):
    """
    Retourne la liste des déclarations avec les informations nécessaires pour l'affichage de la liste.
    Exécute la requête et retourne les résultats.
    On peut passer des filtres supplémentaires (dict ou liste de clauses).
    """
    stmt = get_stmt_liste_declaration()

    # on réutilise la valeur passée en paramètre si c'est une liste/tuple, sinon on part d'une liste vide
    if isinstance(filters, (list, tuple)):
        local_filters = list(filters)
    else:
        local_filters = []

    # Restriction selon les droits de l'utilisateur
    local_filters.extend(get_filtres_droits_declarations(user))

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        local_filters.append(TDeclaration.id_declaration == id_declaration)

    if local_filters:
        stmt = stmt.where(and_(*local_filters))
    results = DB.session.execute(stmt).mappings().all()

    if not results:
        return []
    dict_result = [dict(row) for row in results]

    return dict_result


# pour la modification d'une déclaration.
def get_declaration(id_declaration):
    """
    Récupère en base de données une déclaration, sa forêt associée et son propriétaire.
    Retourne les données sous forme de tuple : (déclaration, forêt, propriétaire).

    Utilisation :
    - Cette fonction est utilisée lorsqu'on souhaite obtenir toutes les informations liées à une déclaration
      (par exemple pour l'affichage ou la modification d'une déclaration existante).

    :param id_declaration: Identifiant de la déclaration à récupérer.
    :return: Tuple (TDeclaration, TForet, None)
    """

    try:
        # On récupère la déclaration correspondant à l'identifiant fourni
        stmt_declaration = (
            select(TDeclaration)
            .where(TDeclaration.id_declaration == id_declaration)
            .limit(1)
        )
        declaration = DB.session.execute(stmt_declaration).scalars().first()

        # On récupère la forêt associée à la déclaration (contient les infos propriétaire)
        stmt_foret = (
            select(TForet).where(TForet.id_foret == declaration.id_foret).limit(1)
        )
        foret = DB.session.execute(stmt_foret).scalars().first()

    except Exception as e:
        # En cas d'erreur (ex: id non trouvé), on retourne des instances vides
        print(f"Erreur lors de la récupération de la déclaration : {e}")
        return (TDeclaration(), TForet(), None)

    return (declaration, foret, None)


#############################################################################


def get_id_areas(areas, type_list):
    """
    Retourne la liste des identifiants d'aires (id_area) correspondant aux types spécifiés.

    Utilisation :
    - Cette fonction est utilisée pour filtrer une liste d'aires selon leur type (par exemple, communes, sections, etc.)
      et récupérer uniquement les identifiants des aires correspondant aux types recherchés.

    :param areas: Liste de dictionnaires représentant les aires (chaque dictionnaire doit contenir au moins "id_area" et "type_code").
    :param type_list: Liste des codes de type à filtrer (ex: ["COMMUNE", "SECTION"]).
    :return: Liste des identifiants d'aires (id_area) correspondant aux types spécifiés.
    """

    return [x["id_area"] for x in filter(lambda x: x["type_code"] in type_list, areas)]


def get_id_area(areas, type_list):
    """
    Récupère l'identifiant de la première zone correspondant à une liste de types donnée.

    Args:
        areas (list): Liste des zones à examiner. Chaque zone doit contenir des informations permettant d'identifier son type.
        type_list (list): Liste des codes de type à filtrer (ex: ["COMMUNE", "SECTION"]).

    """

    id_areas = get_id_areas(areas, type_list)
    return id_areas[0] if id_areas else None


# uniquement utilisée dans le create_or_update_declaration pour le moment
def patch_areas_declarations(id_declaration):
    """
    Met à jour les informations géographiques (aires) associées à une déclaration.

    Cette fonction est utilisée principalement lors de la création ou modification d'une déclaration, afin de recalculer et synchroniser les liens entre la déclaration
    et les différentes aires géographiques (secteurs, communes, sections, etc.) en base.

    Elle effectue plusieurs opérations SQL :
    - Met à jour la géométrie (geom), la géométrie en WGS84 (geom_4326) et le centroïde de la déclaration
      à partir de l'union des géométries des aires de type ONF_UG ou CADASTRE liées à la déclaration.
    - Supprime les liens existants entre la déclaration et les aires de type SECTEUR, COMMUNE, SECTION,
      ONF_FRT, DGD pour éviter les doublons ou incohérences.
    - Recalcule et insère les nouveaux liens entre la déclaration et ces aires, en utilisant une fonction
      d'intersection géométrique avec une tolérance (ref_geo.intersect_geom_type_tol).

    :param id_declaration: Identifiant de la déclaration à traiter
    """

    # -- Mise à jour des champs geom, geom_4326 et centroid de la déclaration
    txt = text("""
    UPDATE oeasc_declarations.t_declarations e SET geom=d.geom, geom_4326=d.geom_4326, centroid=d.centroid
        FROM (SELECT id_declaration, geom, geom_4326, ARRAY[ST_Y(centroid), ST_X(centroid)] AS centroid
        FROM (SELECT id_declaration, geom, geom_4326, ST_CENTROID(geom_4326) AS centroid
        FROM (SELECT id_declaration, geom, ST_TRANSFORM(geom, 4326) AS geom_4326
        FROM (SELECT id_declaration, ST_MULTI(ST_UNION(l.geom)) AS geom
        FROM oeasc_declarations.cor_areas_declarations c
        JOIN ref_geo.l_areas l ON c.id_area = l.id_area AND l.id_type IN (ref_geo.get_id_type('OEASC_ONF_UG'), ref_geo.get_id_type('OEASC_CADASTRE'))
        WHERE :id_declaration_param = id_declaration
        GROUP BY id_declaration)a)b)c)d
        WHERE :id_declaration_param = e.id_declaration
        RETURNING e.id_declaration, e.centroid;

            -- Suppression des liens existants entre la déclaration et les aires de type SECTEUR, COMMUNE, SECTION, ONF_FRT, DGD
            DELETE FROM oeasc_declarations.cor_areas_declarations c
            USING ref_geo.l_areas l
            WHERE l.id_area=c.id_area AND l.id_type in (
            ref_geo.get_id_type('OEASC_SECTEUR'),
            ref_geo.get_id_type('OEASC_COMMUNE'),
            ref_geo.get_id_type('OEASC_SECTION'),
            ref_geo.get_id_type('OEASC_ONF_FRT'),
            ref_geo.get_id_type('OEASC_DGD')
            )
            AND c.id_declaration = :id_declaration_param
        ;

            -- Insertion des nouveaux liens entre la déclaration et les aires recalculées
            INSERT INTO oeasc_declarations.cor_areas_declarations

            WITH
            selected_types AS (SELECT UNNEST(ARRAY [
                    'OEASC_SECTEUR',
                    'OEASC_COMMUNE',
                    'OEASC_SECTION',
                    'OEASC_ONF_FRT',
                    'OEASC_DGD'
                ]) AS id_type)

                SELECT
                    :id_declaration_param,
                    ref_geo.intersect_geom_type_tol(d.geom, selected_types.id_type, 0.05) as id_area
                    FROM selected_types
                    JOIN oeasc_declarations.t_declarations d ON d.id_declaration = :id_declaration_param
                RETURNING *;

        """).bindparams(id_declaration_param=id_declaration)

    # Exécution de la requête SQL pour mettre à jour les aires de la déclaration
    DB.session.execute(txt)
    DB.session.commit()


def get_foret_from_code(code_foret):
    """
    Récupère une forêt et son propriétaire à partir du code forêt.

    Utilisation :
    - Cette fonction est utilisée lorsqu'on souhaite obtenir les informations d'une forêt
      (ainsi que son propriétaire) à partir de son code unique (code_foret).
    - Typiquement utilisée lors de la sélection d'une forêt existante dans un formulaire
      ou pour afficher les détails d'une forêt à partir de son code.

    :param code_foret: Code unique de la forêt à rechercher (chaîne de caractères).
    :return: Tuple (TForet, None) — les données propriétaire sont dans TForet.
    """

    # On s'assure que le code forêt est en majuscules pour la recherche
    code_foret = code_foret.upper()

    # On récupère la forêt correspondant au code fourni (contient les infos propriétaire)
    stmt_foret = select(TForet).where(TForet.code_foret == code_foret).limit(1)
    foret = DB.session.execute(stmt_foret).scalars().first()

    if foret is None:
        return (None, None)

    return (foret, None)


def get_foret_type(id_foret):
    """
    Retourne le type de forêt à partir de l'identifiant de la forêt.
    Utilise id_nomenclature_proprietaire_type stocké directement dans t_forets.
    """
    foret = (
        DB.session.execute(select(TForet).where(TForet.id_foret == id_foret).limit(1))
        .scalars()
        .first()
    )

    if not foret:
        return

    if not foret.id_nomenclature_proprietaire_type:
        return "Indéterminé"

    proprietaire_type = get_nomenclature_from_id(
        foret.id_nomenclature_proprietaire_type
    )["label_fr"]

    d_prop_foret_type = {
        "État": "Domaniale",
        "Centre hospitalier": "Autre forêt publique",
        "EP PNC": "Autre forêt publique",
        "Commune": "Communale",
        "Groupement forestier": "Groupement forestier",
        "Section / hameau": "Sectionale",
        "Privé": "Privée",
    }

    return d_prop_foret_type.get(proprietaire_type, "Indeterminé")


def hide_proprietaire(proprietaire):
    """
    Modifie l'affichage des informations sensibles concernant un propriétaire.

    Cette fonction est utilisée pour masquer les données personnelles d'un propriétaire
    lorsque l'utilisateur qui consulte les informations n'est ni le déclarant, ni un administrateur.
    Elle remplace les valeurs des champs sensibles par des valeurs génériques ou anonymisées.

    Utilisation :
    - Appelée lors de l'affichage des informations d'un propriétaire dans l'interface utilisateur,
      afin de garantir la confidentialité des données personnelles pour les utilisateurs non autorisés.

    Args:
        proprietaire (dict): Dictionnaire contenant les informations du propriétaire à anonymiser.

    Effet :
        Les champs suivants sont remplacés par des valeurs anonymes :
        - nom_proprietaire : "***"
        - adresse : "***"
        - s_code_postal : "***"
        - s_commune_proprietaire : "***"
        - telephone : "09 99 99 99 99"
        - email : "prive@prive.prive"
    """

    # Masquage des champs texte sensibles
    for key in [
        "nom_proprietaire",
        "adresse",
        "s_code_postal",
        "s_commune_proprietaire",
    ]:
        proprietaire[key] = "***"

    # Remplacement du numéro de téléphone par une valeur générique
    proprietaire["telephone"] = "09 99 99 99 99"
    # Remplacement de l'email par une adresse fictive
    proprietaire["email"] = "prive@prive.prive"


####################################################################################
# non utilisé actuellement
def resume_gravite(declaration_dict):
    """
    Non utilisé actuellement

    Détermine la gravité maximale (la "pire") parmi tous les dégâts d'une déclaration.

    Cette fonction est utilisée pour résumer la gravité d'une déclaration forestière,
    en parcourant tous les dégâts et toutes les essences associées à chaque dégât.
    Elle est typiquement appelée lors de la résolution complète d'une déclaration
    (ex: dans resolve_declaration) pour afficher ou exporter la gravité principale.

    :param declaration_dict: Dictionnaire représentant une déclaration, contenant la clé "degats"
    :return: Modifie le dictionnaire en ajoutant la clé "gravite" (dictionnaire nomenclature ou None)
    """

    gravite = None  # Variable pour stocker la gravité la plus élevée trouvée

    # Si la déclaration ne contient pas de dégâts, on ne fait rien
    if not declaration_dict.get("degats"):
        return

    # Parcours de tous les dégâts de la déclaration
    for degat in declaration_dict.get("degats"):
        # Parcours de toutes les essences associées à ce dégât
        for degat_essence in degat["degat_essences"]:
            # Si la gravité n'est pas renseignée pour cette essence, on passe
            if not degat_essence.get("id_nomenclature_degat_gravite"):
                continue

            # Si le code nomenclature de gravité est absent, on passe
            if not degat_essence["id_nomenclature_degat_gravite"].get(
                "cd_nomenclature"
            ):
                continue

            gravite_ = degat_essence["id_nomenclature_degat_gravite"]

            # Si aucune gravité n'a encore été trouvée, on initialise
            if not gravite:
                gravite = gravite_

            # Logique pour déterminer la gravité maximale :
            # Si on trouve une gravité "DG_IMPT" (importante), on la sélectionne en priorité
            # Sinon, si la gravité courante est "DG_FLB" (faible) et la nouvelle "DG_MOY" (moyenne), on la remplace
            if gravite_["cd_nomenclature"] == "DG_IMPT" or (
                gravite["cd_nomenclature"] == "DG_FLB"
                and gravite_["cd_nomenclature"] == "DG_MOY"
            ):
                gravite = gravite_

    # On ajoute la gravité maximale trouvée au dictionnaire de déclaration
    declaration_dict["gravite"] = gravite
