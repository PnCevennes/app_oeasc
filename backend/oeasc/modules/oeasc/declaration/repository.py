"""
Fonctions de traitement de données pour les déclarations
"""

from sqlalchemy import (
    select,
    case,
    func,
    text,
    literal,
    cast,
    String,
    Boolean,
    Text,
    and_,
    or_,
    literal_column,
)
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import array_agg, ARRAY, INTEGER

from oeasc.modules.oeasc.declaration.models import (
    TDeclaration,
    CorAreasDeclaration,
    CorNomenclatureDeclarationEspece,
    CorNomenclatureDeclarationEssenceComplementaire,
    CorNomenclatureDeclarationEssenceSecondaire,
    CorNomenclatureDeclarationMaturite,
    CorNomenclatureDeclarationOrigine,
    CorNomenclatureDeclarationPaturageSaison,
    CorNomenclatureDeclarationPaturageType,
    CorNomenclatureDeclarationProtectionType,
    TForet,
    TProprietaire,
    TDegat,
)

from oeasc.modules.oeasc.user.models import VUsers

# Import des modèles forets (à adapter selon votre projet)
from oeasc.modules.oeasc.declaration.models import TForet, TProprietaire


from flask import current_app
from utils_flask_sqla_geo.generic import GenericQueryGeo
from utils_flask_sqla.generic import GenericQuery
from .schema import (
    TDeclarationSchema,
    TProprietaireSchema,
    TForetSchema,
)
from .all_stmt import (
    get_stmt_liste_declaration,
    get_v_declarations_query,
    get_v_degats_query,
    get_v_export_vl_declaration_query,
    get_v_declaration_degat_query,
    get_v_export_declaration_csv_query,
    get_v_export_declaration_degats_csv_query,
    get_v_export_declaration_shape_query,
    get_v_export_declaration_degats_shape_query,
    get_v_declaration_degats_restrict_query,
    get_stmt_for_resultats_degats,
)

from oeasc.modules.oeasc.nomenclature import (
    get_area_from_id,
    get_nomenclature_from_id,
    get_dict_nomenclature_areas,
)
from oeasc.modules.oeasc.user.repository import get_user, get_id_organismes

config = current_app.config
DB = config["DB"]

status_declaration = {
    "Active": 1,
    "A renouveler": 2,
    "Archivée": 3,
    "Dupliquée": 4,
}


# add_degats uniquement utilsé dans get_fiche_declaration
def add_degats(declarations):
    """
    Ajoute un objet 'degats' à chaque déclaration dans la liste fournie.

    Cette fonction est utilisée dans :
    - get_declarations : pour enrichir chaque déclaration avec ses dégâts associés
    - Toute logique nécessitant d'associer les dégâts (type, essence, gravité, etc.) aux déclarations

    Elle récupère les dégâts via la vue SQL 'v_degats', puis les regroupe par déclaration.
    Pour chaque déclaration, elle ajoute une clé 'degats' contenant la liste des dégâts structurés.

    :param declarations: Liste de dictionnaires représentant les déclarations
    """

    # Récupération des dégâts via la vue SQL 'v_degats'
    data_degats = GenericQuery(
        DB, "v_degats", "oeasc_declarations", limit=1e6
    ).return_query()["items"]

    # Dictionnaire pour regrouper les dégâts par déclaration
    degats_declarations = {}

    for deg in data_degats:
        # On récupère la liste des dégâts pour la déclaration courante
        dd = degats_declarations.get(deg["id_declaration_degat"])
        if not dd:
            dd = degats_declarations[deg["id_declaration_degat"]] = []

        d_cur = None
        # On cherche si le type de dégât existe déjà dans la liste
        for d in dd:
            if d["degat_type_mnemo"] == deg["degat_type_mnemo"]:
                d_cur = d
                break

        if not d_cur:
            # Si le type de dégât n'existe pas, on le crée
            d_cur = {
                "degat_type_mnemo": deg["degat_type_mnemo"],
                "degat_type_label": deg["degat_type_label"],
                "degat_type_code": deg["degat_type_code"],
            }
            d_cur["degat_essences"] = []
            dd.append(d_cur)

        # On ajoute les informations d'essence de dégât si elles existent
        if deg.get("degat_essence_mnemo"):
            d_cur["degat_essences"].append(
                {
                    "degat_essence_mnemo": deg["degat_essence_mnemo"],
                    "degat_anteriorite_mnemo": deg["degat_anteriorite_mnemo"],
                    "degat_gravite_mnemo": deg["degat_gravite_mnemo"],
                    "degat_etendue_mnemo": deg["degat_etendue_mnemo"],
                    "degat_essence_label": deg["degat_essence_label"],
                    "degat_anteriorite_label": deg["degat_anteriorite_label"],
                    "degat_gravite_label": deg["degat_gravite_label"],
                    "degat_etendue_label": deg["degat_etendue_label"],
                    "degat_essence_code": deg["degat_essence_code"],
                    "degat_anteriorite_code": deg["degat_anteriorite_code"],
                    "degat_gravite_code": deg["degat_gravite_code"],
                    "degat_etendue_code": deg["degat_etendue_code"],
                }
            )

    # On ajoute la liste des dégâts à chaque déclaration
    for d in declarations:
        d["degats"] = degats_declarations.get(d["id_declaration"], [])


def get_fiche_declaration(
    user=None, type_export=None, type_out=None, id_declaration=None, restrict=False
):
    """
    Récupère les données d'une déclaration selon les paramètres fournis.
    Cette fonction est utilisée pour obtenir les informations d'une déclaration spécifique ou d'un ensemble de déclarations
    en fonction des droits de l'utilisateur, du type d'export souhaité et d'autres critères.
    """

    # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
    liste_id_organismes_solo = get_id_organismes(
        ["Autre (préciser)", "Pas d'organisme", "Aucun"]
    )

    # Dictionnaire de correspondance entre les paramètres et les vues SQL à utiliser
    view_names = {
        "csv": "v_export_declarations_csv",
        "csv_deg": "v_export_declaration_degats_csv",
        "shape": "v_export_declarations_shape",
        "shape_deg": "v_export_declaration_degats_shape",
        "default": "v_declarations",
        "default_deg": "v_declaration_degats",
        "default_deg_restrict": "v_declaration_degats_restrict",
    }

    # Choix de la vue selon les paramètres d'export et de sortie
    if type_export in ["csv", "shape"]:
        view_key = type_export
    else:
        view_key = "default"

    if type_out == "degat":
        view_key += "_deg"

    if restrict:
        # Restriction supplémentaire, principalement pour les vues de dégâts
        view_key += "_restrict"

    view_name = view_names[view_key]

    # Définition des filtres selon les droits de l'utilisateur
    filters = {}
    if user:
        # Cas administrateur ou animateur (droit >= 5) : accès à toutes les déclarations
        if user["id_droit_max"] >= 5:
            pass  # Pas de filtre

        # Cas déclarant de la même structure (hors particuliers) (droit >= 2)
        elif (
            user["id_droit_max"] >= 2
            and user["id_organisme"] not in liste_id_organismes_solo
        ):
            filters = {"organisme": user["organisme"]}

        # Cas droit 1 : accès uniquement à ses propres alertes
        elif user["id_droit_max"] >= 1:
            filters = {"id_declarant": user["id_role"]}

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        filters["id_declaration"] = id_declaration

    # Définition du champ géométrique pour l'export shapefile
    geometry_field = None
    if type_export == "shape":
        geometry_field = "geom"

    # Création de la requête via GenericQueryGeo (utilise la vue SQL et les filtres)
    data = None
    gq = GenericQueryGeo(
        DB,
        view_name,
        "oeasc_declarations",
        geometry_field=geometry_field,
        filters=filters,
        limit=1e6,
    )

    # Cas d'export shapefile : on retourne directement le résultat de la requête
    if type_export == "shape":
        return gq.query()[0]

    # Exécution de la requête et récupération des données
    data = gq.return_query()

    # Si aucune donnée n'est trouvée, on retourne une liste vide
    if not (data and data.get("items")):
        return []

    declarations = data.get("items")

    # Remplacement des valeurs None par des chaînes vides pour éviter les erreurs côté frontend
    for d in declarations:
        for e in d:
            if d[e] is None:
                d[e] = ""

    # Si on utilise une vue d'export ou de dégâts, on retourne directement les déclarations
    if view_key != "default":
        return declarations

    # Cas par défaut : enrichissement des déclarations avec les objets "dégats"
    # (utilisé pour l'affichage détaillé ou l'export complet)
    add_degats(declarations)

    # Pré-traitement des nomenclatures géographiques (désactivé ici)
    # pre_get_dict_nomenclature_areas(declarations)
    # Résolution complète des déclarations (désactivé ici)
    # declarations = [resolve_declaration(d) for d in declarations]

    return declarations


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

    arranged_post_data = {}

    # On prépare un dictionnaire conforme au schéma Marshmallow pour la déclaration.
    # On extrait et adapte les champs nécessaires depuis post_data.
    arranged_post_data["id_declarant"] = post_data.get("id_declarant")
    arranged_post_data["id_foret"] = post_data.get("id_foret")
    arranged_post_data["id_nomenclature_peuplement_type"] = post_data.get(
        "id_nomenclature_peuplement_type"
    )
    arranged_post_data["id_nomenclature_peuplement_acces"] = post_data.get(
        "id_nomenclature_peuplement_acces"
    )
    arranged_post_data["id_nomenclature_peuplement_essence_principale"] = post_data.get(
        "id_nomenclature_peuplement_essence_principale"
    )
    arranged_post_data["meta_create_date"] = post_data.get("meta_create_date")
    arranged_post_data["meta_update_date"] = None  # sera mis à jour dans la bdd

    arranged_post_data["b_peuplement_protection_existence"] = post_data.get(
        "b_peuplement_protection_existence"
    )
    arranged_post_data["b_peuplement_paturage_presence"] = post_data.get(
        "b_peuplement_paturage_presence"
    )
    arranged_post_data["b_autorisation"] = post_data.get("b_autorisation")
    arranged_post_data["b_valid"] = post_data.get("b_valid")

    arranged_post_data["id_nomenclature_proprietaire_declarant"] = post_data.get(
        "id_nomenclature_proprietaire_declarant"
    )
    arranged_post_data["id_nomenclature_peuplement_origine"] = post_data.get(
        "id_nomenclature_peuplement_origine"
    )
    arranged_post_data["id_nomenclature_foret_type"] = post_data.get(
        "id_nomenclature_foret_type"
    )
    arranged_post_data["id_nomenclature_peuplement_paturage_frequence"] = post_data.get(
        "id_nomenclature_peuplement_paturage_frequence"
    )
    arranged_post_data["id_nomenclature_peuplement_paturage_statut"] = post_data.get(
        "id_nomenclature_peuplement_paturage_statut"
    )
    arranged_post_data["peuplement_surface"] = post_data.get("peuplement_surface")
    arranged_post_data["autre_protection"] = post_data.get("autre_protection")
    arranged_post_data["precision_localisation"] = post_data.get(
        "precision_localisation"
    )
    arranged_post_data["commentaire"] = post_data.get("commentaire")
    arranged_post_data["degats"] = post_data.get("degats")

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

    # On adapte le format des aires pour Marshmallow (sans id_declaration)
    arranged_post_data["areas_localisation"] = [
        {"id_area": id_area} for id_area in post_data["areas_localisation"]
    ]

    # Cas 1 : La parcelle n'a pas de document de gestion durable (petit propriétaire)
    # On crée éventuellement un nouveau propriétaire et une nouvelle forêt
    if not post_data["b_document"]:
        id_declarant = post_data["id_declarant"]

        # On récupère la nomenclature du propriétaire déclarant
        nomenclature = post_data[
            "id_nomenclature_proprietaire_declarant"
        ] and get_nomenclature_from_id(
            post_data["id_nomenclature_proprietaire_declarant"]
        )

        # Si la nomenclature n'est pas "P_D_O_NP", on retire le déclarant
        if nomenclature and nomenclature["cd_nomenclature"] != "P_D_O_NP":
            post_data["id_declarant"] = None

        # Préparation des données du propriétaire
        proprietaireSchema = TProprietaireSchema()
        data_proprio = {}
        data_proprio["id_declarant"] = id_declarant
        data_proprio["nom_proprietaire"] = post_data.get("nom_proprietaire")
        data_proprio["telephone"] = post_data.get("telephone")
        data_proprio["email"] = post_data.get("email")
        data_proprio["adresse"] = post_data.get("adresse")
        data_proprio["s_code_postal"] = post_data.get("s_code_postal")
        data_proprio["s_commune_proprietaire"] = post_data.get("s_commune_proprietaire")
        data_proprio["id_nomenclature_proprietaire_type"] = post_data.get(
            "id_nomenclature_proprietaire_type"
        )

        # Si modification d'un propriétaire existant
        if post_data.get("id_proprietaire"):
            data_proprio["id_declaration"] = post_data.get("id_declaration")
            proprietaire_bdd = DB.session.get(
                TProprietaire, post_data.get("id_declaration")
            )

            proprietaire = proprietaireSchema.load(
                data_proprio,
                instance=proprietaire_bdd,
                partial=True,  # Mise à jour partielle
                session=DB.session,
            )
            DB.session.commit()  # modification de l'instance

        else:
            # Création d'un nouveau propriétaire
            proprietaire = proprietaireSchema.load(
                data_proprio, session=DB.session, partial=True
            )
            DB.session.add(proprietaire)
            DB.session.commit()  # ajout de l'instance
            post_data["id_proprietaire"] = proprietaire.id_proprietaire

        # Préparation des données de la forêt
        data_foret = {}
        data_foret["id_proprietaire"] = proprietaire.id_proprietaire
        data_foret["b_statut_public"] = post_data.get("b_statut_public")
        data_foret["b_document"] = post_data.get("b_document")
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

        # Création de la forêt
        foretSchema = TForetSchema()
        new_foret = foretSchema.load(data_foret, session=DB.session, partial=True)
        DB.session.add(new_foret)
        DB.session.commit()
        arranged_post_data["id_foret"] = new_foret.id_foret

    else:
        # Cas 2 : La parcelle a un document de gestion durable (forêt existante)
        # On récupère la forêt existante à partir du code_area
        id_area_foret = post_data["areas_foret_onf"] or post_data["areas_foret_dgd"]
        code_foret = get_area_from_id(id_area_foret)["area_code"]

        stmt_foret = select(TForet).where(TForet.code_foret == code_foret).limit(1)
        foret = DB.session.execute(stmt_foret).scalars().first()
        arranged_post_data["id_foret"] = foret.id_foret

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
        declaration = declarationSchema.load(
            arranged_post_data, session=DB.session, partial=True
        )
        DB.session.add(declaration)

    DB.session.commit()

    # Mise à jour des aires liées à la déclaration (communes, secteurs, sections)
    patch_areas_declarations(declaration.id_declaration)

    # On retourne les données arrangées (utiles pour debug ou pour affichage)
    return arranged_post_data


######################################################################################
######################################################################################


# Pour la liste des déclarations (page système d'alertes => alertes signalées)
def get_liste_declarations(filters=None, user=None, id_declaration=None):
    """
    Retourne la liste des déclarations avec les informations nécessaires pour l'affichage de la liste.
    Exécute la requête et retourne les résultats.
    On peut passer des filtres supplémentaires (dict ou liste de clauses).
    """
    # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
    liste_id_organismes_solo = get_id_organismes(
        ["Autre (préciser)", "Pas d'organisme", "Aucun"]
    )

    query = get_stmt_liste_declaration()

    # Définition des filtres selon les droits de l'utilisateur
    # on réutilise la valeur passée en paramètre si c'est une liste/tuple, sinon on part d'une liste vide
    if isinstance(filters, (list, tuple)):
        local_filters = list(filters)
    else:
        local_filters = []

    if user:

        if (
            user["id_droit_max"] >= 5
        ):  # Cas admin ou animateur (droit >= 5) : accès à toutes les déclarations
            pass  # Pas de filtre
        elif (  # Cas déclarant de la même structure (hors particuliers) (droit >= 2)
            user["id_droit_max"] >= 2
            and user["id_organisme"] not in liste_id_organismes_solo
        ):
            local_filters.append(VUsers.organisme == user["organisme"])
        elif (
            user["id_droit_max"] >= 1
        ):  # Cas droit 1 : accès uniquement à ses propres alertes
            local_filters.append(TDeclaration.id_declarant == user["id_role"])

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        local_filters.append(TDeclaration.id_declaration == id_declaration)

    if local_filters:
        query = query.where(and_(*local_filters))
    results = DB.session.execute(query).mappings().all()

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
    :return: Tuple (TDeclaration, TForet, TProprietaire)
    """

    try:
        # On récupère la déclaration correspondant à l'identifiant fourni
        stmt_declaration = (
            select(TDeclaration)
            .where(TDeclaration.id_declaration == id_declaration)
            .limit(1)
        )
        declaration = DB.session.execute(stmt_declaration).scalars().first()

        # On récupère la forêt associée à la déclaration
        stmt_foret = (
            select(TForet).where(TForet.id_foret == declaration.id_foret).limit(1)
        )
        foret = DB.session.execute(stmt_foret).scalars().first()

        # On récupère le propriétaire associé à la forêt
        stmt_proprietaire = (
            select(TProprietaire)
            .where(TProprietaire.id_proprietaire == foret.id_proprietaire)
            .limit(1)
        )
        proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    except Exception as e:
        # En cas d'erreur (ex: id non trouvé), on retourne des instances vides
        print(f"Erreur lors de la récupération de la déclaration : {e}")
        return (TDeclaration(), TForet(), TProprietaire())

    return (declaration, foret, proprietaire)


# pour les export et les résultat de suivis => système d'alertes
# sera a supprimé lorsqu'on aura tout passé en sqlalchemy
def get_declarations_view_ancien(
    user=None, type_export=None, type_out=None, id_declaration=None, restrict=False
):
    """
    Retourne des donées de déclarations a partir des vues.

    Cette fonction permet de récupérer les déclarations forestières selon différents paramètres :
    - type_export : format d'export souhaité ("csv", "shape", ou None pour le format par défaut)
    - type_out : "degat" pour une ligne par dégât, None pour une ligne par déclaration
    - user : dictionnaire contenant les informations sur l'utilisateur (droits, organisme, etc.)
    - id_declaration : pour filtrer sur une déclaration précise
    - restrict : pour restreindre la vue (utilisé principalement pour les vues de dégâts)

    """

    # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
    liste_id_organismes_solo = get_id_organismes(
        ["Autre (préciser)", "Pas d'organisme", "Aucun"]
    )

    # Dictionnaire de correspondance entre les paramètres et les vues SQL à utiliser
    view_names = {
        "csv": "v_export_declarations_csv",
        "csv_deg": "v_export_declaration_degats_csv",
        "shape": "v_export_declarations_shape",
        "shape_deg": "v_export_declaration_degats_shape",
        "default": "v_declarations",
        "default_deg": "v_declaration_degats",
        "default_deg_restrict": "v_declaration_degats_restrict",
    }

    # Choix de la vue selon les paramètres d'export et de sortie
    if type_export in ["csv", "shape"]:
        view_key = type_export
    else:
        view_key = "default"

    if type_out == "degat":
        view_key += "_deg"

    if restrict:
        # Restriction supplémentaire, principalement pour les vues de dégâts
        view_key += "_restrict"

    view_name = view_names[view_key]

    # Définition des filtres selon les droits de l'utilisateur
    filters = {}
    if user:
        # Cas administrateur ou animateur (droit >= 5) : accès à toutes les déclarations
        if user["id_droit_max"] >= 5:
            pass  # Pas de filtre

        # Cas déclarant de la même structure (hors particuliers) (droit >= 2)
        elif (
            user["id_droit_max"] >= 2
            and user["id_organisme"] not in liste_id_organismes_solo
        ):
            filters = {"organisme": user["organisme"]}

        # Cas droit 1 : accès uniquement à ses propres alertes
        elif user["id_droit_max"] >= 1:
            filters = {"id_declarant": user["id_role"]}

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        filters["id_declaration"] = id_declaration

    # Définition du champ géométrique pour l'export shapefile
    geometry_field = None
    if type_export == "shape":
        geometry_field = "geom"

    # Création de la requête via GenericQueryGeo (utilise la vue SQL et les filtres)
    data = None
    gq = GenericQueryGeo(
        DB,
        view_name,
        "oeasc_declarations",
        geometry_field=geometry_field,
        filters=filters,
        limit=1e6,
    )

    # Cas d'export shapefile : on retourne directement le résultat de la requête
    if type_export == "shape":
        return gq.query()[0]

    # Exécution de la requête et récupération des données
    data = gq.return_query()

    # Si aucune donnée n'est trouvée, on retourne une liste vide
    if not (data and data.get("items")):
        return []

    declarations = data.get("items")

    # Remplacement des valeurs None par des chaînes vides pour éviter les erreurs côté frontend
    for d in declarations:
        for e in d:
            if d[e] is None:
                d[e] = ""

    # Si on utilise une vue d'export ou de dégâts, on retourne directement les déclarations
    if view_key != "default":
        return declarations

    # Cas par défaut : enrichissement des déclarations avec les objets "dégats"
    # (utilisé pour l'affichage détaillé ou l'export complet)
    add_degats(declarations)

    # Pré-traitement des nomenclatures géographiques (désactivé ici)
    # pre_get_dict_nomenclature_areas(declarations)
    # Résolution complète des déclarations (désactivé ici)
    # declarations = [resolve_declaration(d) for d in declarations]

    return declarations


# pour les export et les résultat de suivis => système d'alertes
# sera a supprimé lorsqu'on aura tout passé en sqlalchemy
def get_declarations_view(
    user=None, type_export=None, type_out=None, id_declaration=None, restrict=False
):
    """
    Retourne des donées de déclarations a partir des vues.

    Cette fonction permet de récupérer les déclarations forestières selon différents paramètres :
    - type_export : format d'export souhaité ("csv", "shape", ou None pour le format par défaut)
    - type_out : "degat" pour une ligne par dégât, None pour une ligne par déclaration
    - user : dictionnaire contenant les informations sur l'utilisateur (droits, organisme, etc.)
    - id_declaration : pour filtrer sur une déclaration précise
    - restrict : pour restreindre la vue (utilisé principalement pour les vues de dégâts)

    """

    # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
    liste_id_organismes_solo = get_id_organismes(
        ["Autre (préciser)", "Pas d'organisme", "Aucun"]
    )

    # Dictionnaire de correspondance entre les paramètres et les vues SQL à utiliser
    view_names = {
        "csv": "v_export_declarations_csv",
        "csv_deg": "v_export_declaration_degats_csv",
        "shape": "v_export_declarations_shape",
        "shape_deg": "v_export_declaration_degats_shape",
        "default": "v_declarations",
        "default_deg": "v_declaration_degats",
        "default_deg_restrict": "v_declaration_degats_restrict",
    }

    stmt_function_names = {
        "csv": get_v_export_declaration_csv_query,
        "csv_deg": get_v_export_declaration_degats_csv_query,
        "shape": get_v_export_declaration_shape_query,
        "shape_deg": get_v_export_declaration_degats_shape_query,
        "default": get_v_declarations_query,
        "default_deg": get_v_declaration_degat_query,
        "default_deg_restrict": get_v_declaration_degats_restrict_query,
    }

    # Choix de la vue selon les paramètres d'export et de sortie
    if type_export in ["csv", "shape"]:
        view_key = type_export
    else:
        view_key = "default"

    if type_out == "degat":
        view_key += "_deg"

    if restrict:
        # Restriction supplémentaire, principalement pour les vues de dégâts
        view_key += "_restrict"

    view_name = view_names[view_key]

    stmt_function = stmt_function_names[view_key]
    stmt = stmt_function()

    # Définition des filtres selon les droits de l'utilisateur
    filters = {}
    if user:
        # Cas administrateur ou animateur (droit >= 5) : accès à toutes les déclarations
        if user["id_droit_max"] >= 5:
            pass  # Pas de filtre

        # Cas déclarant de la même structure (hors particuliers) (droit >= 2)
        elif (
            user["id_droit_max"] >= 2
            and user["id_organisme"] not in liste_id_organismes_solo
        ):
            stmt = stmt.where(VUsers.organisme == user["organisme"])
            # filters = {"organisme": user["organisme"]}

        # Cas droit 1 : accès uniquement à ses propres alertes
        elif user["id_droit_max"] >= 1:
            stmt = stmt.where(TDeclaration.id_declarant == user["id_role"])
            # filters = {"id_declarant": user["id_role"]}

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        stmt = stmt.where(TDeclaration.id_declaration == id_declaration)
        # filters["id_declaration"] = id_declaration

    # Définition du champ géométrique pour l'export shapefile
    geometry_field = None
    if type_export == "shape":
        geometry_field = "geom"
        stmt = stmt.add_columns(
            func.ST_AsBinary(
                func.ST_Transform(func.ST_Centroid(TDeclaration.geom), 4326)
            ).label("geom")
        )

    # Création de la requête via GenericQueryGeo (utilise la vue SQL et les filtres)
    data = None
    # gq = GenericQueryGeo(
    #     DB,
    #     view_name,
    #     "oeasc_declarations",
    #     geometry_field=geometry_field,
    #     filters=filters,
    #     limit=1e6,
    # )

    gq = DB.session.execute(stmt).mappings().all()

    # Cas d'export shapefile : on retourne directement le résultat de la requête
    if type_export == "shape":
        return gq.query()[0]

    # Exécution de la requête et récupération des données
    data = gq.return_query()

    # Si aucune donnée n'est trouvée, on retourne une liste vide
    if not (data and data.get("items")):
        return []

    declarations = data.get("items")

    # Remplacement des valeurs None par des chaînes vides pour éviter les erreurs côté frontend
    for d in declarations:
        for e in d:
            if d[e] is None:
                d[e] = ""

    # Si on utilise une vue d'export ou de dégâts, on retourne directement les déclarations
    if view_key != "default":
        return declarations

    # Cas par défaut : enrichissement des déclarations avec les objets "dégats"
    # (utilisé pour l'affichage détaillé ou l'export complet)
    add_degats(declarations)

    # Pré-traitement des nomenclatures géographiques (désactivé ici)
    # pre_get_dict_nomenclature_areas(declarations)
    # Résolution complète des déclarations (désactivé ici)
    # declarations = [resolve_declaration(d) for d in declarations]

    return declarations


def add_filters_declarations(query, user=None, id_declaration=None):
    """
    Ajoute des filtres à une requête de déclaration en fonction des droits de l'utilisateur et d'un éventuel identifiant de déclaration.

    Utilisation :
    - Cette fonction est utilisée pour appliquer les restrictions d'accès aux déclarations selon les droits de l'utilisateur.
    - Elle peut être utilisée dans différentes fonctions de récupération de déclarations pour centraliser la logique de filtrage.

    :param query: Requête SQLAlchemy à laquelle ajouter les filtres
    :param user: Dictionnaire contenant les informations sur l'utilisateur (droits, organisme, etc.)
    :param id_declaration: Identifiant de déclaration pour filtrer sur une déclaration précise (optionnel)
    :return: Requête SQLAlchemy avec les filtres appliqués
    """

    # Liste des identifiants d'organismes considérés comme "solo" (particuliers, pas d'organisme, etc.)
    liste_id_organismes_solo = get_id_organismes(
        ["Autre (préciser)", "Pas d'organisme", "Aucun"]
    )

    if user:
        if (
            user["id_droit_max"] >= 5
        ):  # Cas admin ou animateur (droit >= 5) : accès à toutes les déclarations
            pass  # Pas de filtre
        elif (  # Cas déclarant de la même structure (hors particuliers) (droit >= 2)
            user["id_droit_max"] >= 2
            and user["id_organisme"] not in liste_id_organismes_solo
        ):
            query = query.where(VUsers.organisme == user["organisme"])
        elif (
            user["id_droit_max"] >= 1
        ):  # Cas droit 1 : accès uniquement à ses propres alertes
            query = query.where(TDeclaration.id_declarant == user["id_role"])

    # Cas où on souhaite une seule déclaration (filtre par identifiant)
    if id_declaration:
        query = query.where(TDeclaration.id_declaration == id_declaration)

    return query


def replace_none_by_empty_string(data):
    """
    Remplace les valeurs None par des chaînes vides dans une liste de dictionnaires.
    """

    for row in data:
        for e in row:
            if row[e] is None:
                row[e] = ""
    return data


# def get_degats_for_resultats_suivi(user=None, id_declaration=None):
#     """
#     Récupère les dégâts associés à une déclaration pour l'affichage dans les résultats de suivi.

#     Utilisation :
#     - Cette fonction est utilisée pour obtenir les informations détaillées des dégâts (type, essence, gravité, etc.)
#       associées à une déclaration spécifique, notamment dans le contexte des résultats de suivi ou d'affichage détaillé.

#     :param id_declaration: Identifiant de la déclaration pour laquelle récupérer les dégâts
#     :return: Liste des dégâts structurés associés à la déclaration
#     """

#     # Récupération des dégâts via la vue SQL 'v_degats' filtrée par id_declaration
#     stmt = get_v_declaration_degats_restrict_query()
#     stmt = add_filters_declarations(stmt, user=user, id_declaration=id_declaration)
#     data_degats = DB.session.execute(stmt).mappings().all()
#     # si aucune doée n'est trouvée, on retourne une liste vide
#     if not data_degats:
#         return []
#     # remplacement des valeurs None par des chaînes vides pour éviter les erreurs côté frontend
#     data_degats = replace_none_by_empty_string(data_degats)

#     data_degats = [dict(row) for row in data_degats]


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
        type_list (list): Liste des types de zones recherchés.

    Returns:
        int or None: L'identifiant de la première zone correspondant à l'un des types spécifiés dans type_list, ou None si aucune zone ne correspond.

    Utilisation:
        Cette fonction est utilisée lorsqu'on souhaite obtenir rapidement l'identifiant d'une zone spécifique parmi une liste, en filtrant selon certains types.
        Par exemple, dans le contexte d'une application de gestion forestière, elle permet de retrouver l'identifiant d'une zone forestière d'un type particulier (ex: zone protégée, zone exploitée, etc.).

    Remarques:
        - La fonction utilise get_id_areas pour obtenir la liste des identifiants correspondant aux types recherchés, puis retourne le premier trouvé.
        - Si aucune zone ne correspond, la fonction retourne None.

    get_id_area
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
    :return: Tuple (TForet, TProprietaire) correspondant à la forêt et son propriétaire.
    """

    # On s'assure que le code forêt est en majuscules pour la recherche
    code_foret = code_foret.upper()

    # On récupère la forêt correspondant au code fourni
    stmt_foret = select(TForet).where(TForet.code_foret == code_foret).limit(1)
    foret = DB.session.execute(stmt_foret).scalars().first()

    # On récupère le propriétaire associé à la forêt trouvée
    stmt_proprietaire = (
        select(TProprietaire)
        .where(TProprietaire.id_proprietaire == foret.id_proprietaire)
        .limit(1)
    )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    # On retourne la forêt et son propriétaire sous forme de tuple
    return (foret, proprietaire)


def get_foret_type(id_foret):
    """
    Retourne le type de forêt à partir de l'identifiant de la forêt.
    Utilisé pour enrichir les informations d'une déclaration avec le type de forêt
    (ex: Domaniale, Communale, Privée, etc.) selon le type du propriétaire.
    """
    # On récupère la forêt et son propriétaire via la fonction get_foret
    foret, proprietaire = get_foret(id_foret)

    # Si la forêt n'existe pas, on ne retourne rien
    if not foret:
        return

    # Si le type de propriétaire n'est pas renseigné, on retourne "Indéterminé"
    if not proprietaire.id_nomenclature_proprietaire_type:
        return "Indéterminé"

    # On récupère le libellé du type de propriétaire via la nomenclature
    proprietaire_type = get_nomenclature_from_id(
        proprietaire.id_nomenclature_proprietaire_type
    )["label_fr"]

    # Dictionnaire de correspondance entre le type de propriétaire et le type de forêt
    d_prop_foret_type = {
        "État": "Domaniale",
        "Centre hospitalier": "Autre forêt publique",
        "EP PNC": "Autre forêt publique",
        "Commune": "Communale",
        "Groupement forestier": "Groupement forestier",
        "Section / hameau": "Sectionale",
        "Privé": "Privée",
    }

    # On retourne le type de forêt correspondant, ou "Indeterminé" si non trouvé
    foret_type = d_prop_foret_type.get(proprietaire_type, "Indeterminé")

    return foret_type


def dfpu_as_dict(declaration, foret, proprietaire, declarant, b_resolve=True):
    """
    Retourne une déclaration sous forme de dictionnaire, enrichie avec les informations
    de la forêt, du propriétaire et du déclarant.

    Cette fonction est utilisée pour transformer les objets SQLAlchemy (déclaration, forêt,
    propriétaire, déclarant) en un dictionnaire exploitable par le frontend ou pour l'export.
    Elle est notamment utilisée dans les fonctions dfpu_as_dict_from_id_declaration et
    create_or_update_declaration pour préparer les données à afficher ou à transmettre.

    :param declaration: Instance de TDeclaration (ou None)
    :param foret: Instance de TForet (ou None)
    :param proprietaire: Instance de TProprietaire (ou None)
    :param declarant: Dictionnaire utilisateur (ou None)
    :param b_resolve: Booléen, si True enrichit le dictionnaire avec les nomenclatures et le type de forêt
    :return: Dictionnaire représentant la déclaration complète
    """

    # Si la déclaration n'est pas fournie, on crée une instance vide
    if not declaration:
        declaration = TDeclaration()

    # Si la forêt n'est pas fournie, on crée une instance vide
    if not foret:
        foret = TForet()

    # Si le propriétaire n'est pas fourni, on crée une instance vide
    if not proprietaire:
        proprietaire = TProprietaire()

    # Si le déclarant n'est pas fourni, on récupère l'utilisateur courant
    if not declarant:
        declarant = get_user()

    # Sérialisation des objets en dictionnaires via Marshmallow
    declaration_schema = TDeclarationSchema()
    declaration_dict = declaration_schema.dump(declaration)

    foret_dict = TForetSchema().dump(foret)
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)

    # On ajoute les informations de forêt et de propriétaire à la déclaration
    declaration_dict["foret"] = foret_dict
    declaration_dict["declarant"] = declarant
    declaration_dict["foret"]["proprietaire"] = proprietaire_dict

    # Si demandé, on enrichit le dictionnaire avec les nomenclatures et le type de forêt
    if b_resolve:
        # Ajoute les informations de nomenclature et d'aires géographiques
        get_dict_nomenclature_areas(declaration_dict)
        # Ajoute le type de forêt selon le propriétaire
        get_foret_type(declaration_dict.get("id_foret"))

    return declaration_dict


def get_foret(id_foret):
    """
    Renvoie l'objet forêt et son propriétaire à partir de l'identifiant de la forêt.

    Cette fonction est utilisée dans :
    - get_foret_type : pour déterminer le type de forêt selon le propriétaire
    - dfpu_as_dict : pour enrichir les informations de la déclaration avec la forêt et le propriétaire

    :param id_foret: Identifiant de la forêt
    :return: Tuple (foret, proprietaire)
    """

    foret = proprietaire = None

    # On récupère la forêt correspondant à l'id fourni
    stmt_foret = select(TForet).where(TForet.id_foret == id_foret).limit(1)
    foret = DB.session.execute(stmt_foret).scalars().first()

    # Si la forêt existe, on récupère son propriétaire
    if foret:
        id_proprietaire = foret.id_proprietaire

        if id_proprietaire:
            stmt_proprietaire = (
                select(TProprietaire)
                .where(TProprietaire.id_proprietaire == id_proprietaire)
                .limit(1)
            )
            proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return foret, proprietaire


def get_proprietaire_from_id(id_proprietaire, type_proprietaire="proprietaire"):
    """

    Args:
        id_proprietaire (int): L'identifiant du propriétaire à rechercher.

    Returns:
        TProprietaire: L'objet propriétaire correspondant à l'identifiant, ou un objet vide si aucun n'est trouvé.

    Utilisation :
        Cette fonction est utilisée pour obtenir les informations d'un propriétaire à partir de son identifiant,
        par exemple lors de la consultation ou de la modification d'une forêt ou d'une déclaration.
    """
    if type_proprietaire == "declarant":
        stmt_proprietaire = (
            select(TProprietaire)
            .where(TProprietaire.id_declarant == id_proprietaire)
            .limit(1)
        )

    elif type_proprietaire == "proprietaire":
        stmt_proprietaire = (
            select(TProprietaire)
            .where(TProprietaire.id_proprietaire == id_proprietaire)
            .limit(1)
        )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return proprietaire or TProprietaire()


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
#############################$ NOUVEAUX ##########################################


def get_degats_for_resultats_suivi():
    stmt = get_stmt_for_resultats_degats()
    result = DB.session.execute(stmt).mappings().all()
    if not result:
        return []
    data = [dict(row) for row in result]

    return data


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
