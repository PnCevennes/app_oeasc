"""
Fonctions de traitement de données pour les déclarations
"""

from sqlalchemy import (
    select, case, func, text, literal, cast, String, Boolean, Text,
    and_, or_, literal_column
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

from oeasc.modules.oeasc.nomenclature import (
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
    f_create_or_update_declaration pour préparer les données à afficher ou à transmettre.

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


# def resolve_declaration(declaration_dict):
#     """
#     transforme les id nomenclature, area en données
#     """
#     get_dict_nomenclature_areas(declaration_dict)
#     get_foret_type(declaration_dict.get("foret"))
#     resume_gravite(declaration_dict)

#     return declaration_dict


# def dfpu_as_dict_from_id_declaration(id_declaration, b_resolve=True):
#     """
#     retourne une declaration (avec infos foret proprio etc)
#     sous forme de dictionnaire
#     """
#     declaration, foret, proprietaire, declarant = get_dfpu(id_declaration)
#     declaration_dict = dfpu_as_dict(
#         declaration, foret, proprietaire, declarant, b_resolve
#     )
#     return declaration_dict


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


# def get_dfpu(id_declaration):
#     """
#     renvoie (declaration, foret, proprietaire, declarant)
#     """

#     declaration = foret = proprietaire = declarant = None

#     stmt_declaration = (
#         select(TDeclaration)
#         .where(TDeclaration.id_declaration == id_declaration)
#         .limit(1)
#     )
#     declaration = DB.session.execute(stmt_declaration).scalars().first()

#     if declaration:
#         id_declarant = declaration.id_declarant

#         if id_declarant:
#             declarant = get_user(id_declarant)
#         id_foret = declaration.id_foret

#         if id_foret:
#             foret, proprietaire = get_foret(id_foret)

#     return (declaration, foret, proprietaire, declarant)


def create_or_modify(model, key, val, dict_in, schema=None, session=None):
    """
    Fonction générique de création ou modification d'une instance d'un modèle SQLAlchemy
    à partir d'un dictionnaire de données, en utilisant Marshmallow pour la validation et la sérialisation.

    Cette fonction est utilisée dans plusieurs cas :
    - Lors de la création ou la modification d'une déclaration, d'une forêt ou d'un propriétaire
      (voir f_create_or_update_declaration)
    - Pour factoriser la logique d'upsert (update ou insert) sur n'importe quel modèle SQLAlchemy
      avec un schéma Marshmallow associé.

    :param model: Le modèle SQLAlchemy à traiter (ex: TDeclaration, TForet, TProprietaire)
    :param key: La clé primaire du modèle (ex: "id_declaration")
    :param val: La valeur de la clé primaire (ex: 123)
    :param dict_in: Le dictionnaire de données à insérer ou mettre à jour
    :param schema: Le schéma Marshmallow à utiliser (optionnel, déduit automatiquement si absent)
    :param session: La session SQLAlchemy à utiliser (optionnelle, DB.session par défaut)
    :return: L'instance créée ou modifiée
    """
    elem = None
    if session is None:
        # Si aucune session n'est fournie, on utilise la session par défaut
        session = DB.session

    if key:
        # Si une clé primaire est fournie, on tente de récupérer l'instance existante
        elem = session.get(model, val)

    if schema is None:
        # Si aucun schéma n'est fourni, on le déduit automatiquement à partir du nom du modèle
        schema_name = model.__name__ + "Schema"
        schema = globals().get(schema_name)
        if schema is None:
            # Si le schéma n'existe pas, on lève une erreur explicite
            raise ValueError(
                f"Schema {schema_name} not found for model {model.__name__}"
            )

    if elem is not None:
        # Si l'instance existe déjà, on la met à jour avec les nouvelles données
        elem = schema.load(dict_in, instance=elem, session=session, partial=True)
    else:
        # Si l'instance n'existe pas, on la crée
        # On retire la clé primaire du dictionnaire pour éviter les conflits à la création
        dict_in.pop(key, None)
        elem = schema.load(dict_in, session=session)
        session.add(elem)

    # On valide les modifications en base
    session.commit()
    return elem


def patch_areas_declarations(id_declaration):
    """
    Met à jour les informations géographiques (aires) associées à une déclaration.

    Cette fonction est utilisée principalement lors de la création ou modification d'une déclaration
    (voir f_create_or_update_declaration), afin de recalculer et synchroniser les liens entre la déclaration
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


def update_or_insert(model, id_key, id_value, schema, data, session=None):
    """
    Met à jour ou insère une instance d'un modèle SQLAlchemy via marshmallow.

    Cette fonction est utilisée dans :
    - f_create_or_update_declaration : pour insérer ou mettre à jour une forêt ou un propriétaire
    - Toute logique nécessitant un upsert générique sur un modèle SQLAlchemy avec validation Marshmallow

    :param model: Le modèle SQLAlchemy à mettre à jour ou insérer (ex: TForet, TProprietaire).
    :param id_key: La clé primaire du modèle (ex: "id_foret", "id_proprietaire").
    :param id_value: La valeur de la clé primaire (ex: 123).
    :param schema: Le schéma Marshmallow à utiliser pour la validation et la sérialisation.
    :param data: Les données à valider et à insérer ou mettre à jour (dictionnaire).
    :param session: La session SQLAlchemy à utiliser (facultatif, DB.session par défaut).
    :return: L'instance mise à jour ou insérée.
    """
    instance = None

    # Si aucune session n'est fournie, on utilise la session par défaut
    if not session:
        session = DB.session

    # Si une valeur de clé primaire est fournie, on tente de récupérer l'instance existante
    if id_value:
        instance = session.get(model, id_value)

    if instance:
        # Si l'instance existe déjà, on la met à jour avec les nouvelles données
        # Le paramètre partial=True permet de ne mettre à jour que les champs fournis
        instance = schema.load(data, instance=instance, session=session, partial=True)
    else:
        # Si l'instance n'existe pas, on la crée
        # On retire la clé primaire du dictionnaire pour éviter les conflits à la création
        data.pop(id_key, None)
        # Chargement et validation des données dans le schéma Marshmallow
        instance = schema.load(data, session=session)
        # Ajout de la nouvelle instance à la session
        session.add(instance)

    # Validation des modifications en base (commit)
    session.commit()

    return instance


def f_create_or_update_declaration(declaration_dict):
    """
    Création ou modification d'une déclaration.

    Cette fonction est utilisée lors de la création ou la modification d'une déclaration forestière.
    Elle gère également la création ou la mise à jour des objets liés (forêt, propriétaire) selon le cas.
    Elle est encore utilisée dans l'envoi de mail, mais il serait préférable de la refactorer pour passer
    par une fonction dédiée à la gestion des dégâts de forêt.

    :param declaration_dict: Dictionnaire contenant les données de la déclaration à créer ou modifier.
    :return: Dictionnaire représentant la déclaration complète après traitement.
    """

    declaration = proprietaire = foret = None

    id_declaration = declaration_dict.get("id_declaration", None)

    # On écrit la forêt ou le propriétaire dans la base uniquement si la forêt n'est pas documentée
    if not declaration_dict["foret"]["b_document"]:
        # Récupération des identifiants de forêt et de propriétaire
        id_foret = declaration_dict["foret"].get("id_foret", None)
        id_proprietaire = declaration_dict["foret"]["proprietaire"].get(
            "id_proprietaire", None
        )

        # Création ou mise à jour du propriétaire
        proprietaire = update_or_insert(
            TProprietaire,
            "id_proprietaire",
            id_proprietaire,
            TProprietaireSchema,
            declaration_dict["foret"]["proprietaire"],
            session=DB.session,
        )

        # Création ou mise à jour de la forêt
        foret = update_or_insert(
            TForet,
            "id_foret",
            id_foret,
            TForetSchema,
            declaration_dict["foret"],
            session=DB.session,
        )

        # Mise à jour des identifiants dans le dictionnaire de déclaration
        declaration_dict["foret"]["id_proprietaire"] = proprietaire.id_proprietaire
        declaration_dict["id_foret"] = foret.id_foret

    else:
        # Si la forêt est documentée, on met à jour uniquement les objets existants
        id_proprietaire = declaration_dict["foret"]["proprietaire"].get(
            "id_proprietaire", None
        )

        proprietaire = update_or_insert(
            TProprietaire,
            "id_proprietaire",
            id_proprietaire,
            TProprietaireSchema,
            declaration_dict["foret"]["proprietaire"],
            session=DB.session,
        )

        id_foret = declaration_dict["foret"].get("id_foret", None)
        foret = update_or_insert(
            TForet,
            "id_foret",
            id_foret,
            TForetSchema,
            declaration_dict["foret"],
            session=DB.session,
        )

    # Si une date de création personnalisée est fournie, on crée la déclaration puis on la modifie
    if declaration_dict.get("meta_create_date", None):
        declaration = create_or_modify(
            TDeclaration, "id_declaration", id_declaration, declaration_dict
        )
        id_declaration = declaration.id_declaration

    # Création ou modification de la déclaration principale
    declaration = create_or_modify(
        TDeclaration, "id_declaration", id_declaration, declaration_dict
    )

    # Mise à jour des liens géographiques (aires) associés à la déclaration
    DB.session.commit()
    patch_areas_declarations(declaration.id_declaration)

    # Transformation de la déclaration en dictionnaire enrichi pour le frontend ou l'export
    d = dfpu_as_dict(declaration, foret, proprietaire, None)

    return d


def get_declarations(
    user=None, type_export=None, type_out=None, id_declaration=None, restrict=False
):
    """
    Retourne une liste de déclarations sous forme de tableau de dictionnaires.

    Cette fonction permet de récupérer les déclarations forestières selon différents paramètres :
    - type_export : format d'export souhaité ("csv", "shape", ou None pour le format par défaut)
    - type_out : "degat" pour une ligne par dégât, None pour une ligne par déclaration
    - user : dictionnaire contenant les informations sur l'utilisateur (droits, organisme, etc.)
    - id_declaration : pour filtrer sur une déclaration précise
    - restrict : pour restreindre la vue (utilisé principalement pour les vues de dégâts)

    Elle est utilisée dans :
    - Les endpoints d'API pour l'affichage ou l'export des déclarations
    - Les exports CSV ou shapefile
    - Les interfaces d'administration ou d'animation pour filtrer selon les droits utilisateur
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


def resume_gravite(declaration_dict):
    """
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



# Fonctions PostgreSQL custom (appelées via func)
get_nomenclature_label = func.ref_nomenclatures.get_nomenclature_label
get_nomenclature_mnemonique = func.ref_nomenclatures.get_nomenclature_mnemonique
get_nomenclature_code = func.ref_nomenclatures.get_nomenclature_code
get_nomenclature_labels = func.ref_nomenclatures.get_nomenclature_labels
get_nomenclature_mnemoniques = func.ref_nomenclatures.get_nomenclature_mnemoniques
get_nomenclature_codes = func.ref_nomenclatures.get_nomenclature_codes
get_area_names = func.oeasc_declarations.get_area_names
get_id_areas = func.oeasc_declarations.get_id_areas


def get_v_declarations_query():
    # """
    # Reconstruit la vue v_declarations en SQLAlchemy.
    # Retourne une query SQLAlchemy.
    # """

    # # -------------------------
    # # CTE : foret
    # # -------------------------
    # with app.app_context():
        foret_cte = (
            select(
                TForet.id_foret,
                TForet.label_foret,
                TForet.b_document,
                TForet.b_statut_public,
                case(
                    (TForet.b_statut_public == True, "Public"),
                    else_="Privé"
                ).label("statut_public"),
                case(
                    (TForet.b_document == True, "Oui"),
                    else_="Non"
                ).label("document"),
                case(
                    (and_(TForet.b_statut_public == True, TForet.b_document == True), "Public (avec DGD)"),
                    (and_(TForet.b_statut_public == True, TForet.b_document == False), "Public (sans DGD)"),
                    (and_(TForet.b_statut_public == False, TForet.b_document == True), "Privé (avec DGD)"),
                    (and_(TForet.b_statut_public == False, TForet.b_document == False), "Privé (sans DGD)"),
                    else_=""
                ).label("type_foret"),
                get_nomenclature_label(TProprietaire.id_nomenclature_proprietaire_type).label("foret_type_label"),
            )
            .join(TProprietaire, TProprietaire.id_proprietaire == TForet.id_proprietaire)
            .cte("foret")
        )

        # -------------------------
        # CTE : peuplement
        # -------------------------
        d1 = aliased(TDeclaration, name="d1")

        peuplement_cte = (
            select(
                d1.id_declaration,
                d1.peuplement_surface,
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_type).label("peuplement_type_mnemo"),
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_origine).label("peuplement_origine_mnemo"),
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_essence_principale).label("peuplement_ess_1_mnemo"),
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_paturage_statut).label("peuplement_paturage_statut_mnemo"),
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_paturage_frequence).label("peuplement_paturage_frequence_mnemo"),
                get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_acces).label("peuplement_acces_mnemo"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_type).label("peuplement_type_label"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_origine).label("peuplement_origine_label"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_essence_principale).label("peuplement_ess_1_label"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_paturage_statut).label("peuplement_paturage_statut_label"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_paturage_frequence).label("peuplement_paturage_frequence_label"),
                get_nomenclature_label(d1.id_nomenclature_peuplement_acces).label("peuplement_acces_label"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_type).label("peuplement_type_code"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_origine).label("peuplement_origine_code"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_essence_principale).label("peuplement_ess_1_code"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_paturage_statut).label("peuplement_paturage_statut_code"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_paturage_frequence).label("peuplement_paturage_frequence_code"),
                get_nomenclature_code(d1.id_nomenclature_peuplement_acces).label("peuplement_acces_code"),
            )
            .select_from(d1)
            .cte("peuplement")
        )

        # -------------------------
        # CTE : peuplement_nomenclatures
        # -------------------------
        d2 = aliased(TDeclaration, name="d2")
        c_ess_2 = aliased(CorNomenclatureDeclarationEssenceSecondaire, name="c_ess_2")
        c_ess_3 = aliased(CorNomenclatureDeclarationEssenceComplementaire, name="c_ess_3")
        c_maturite = aliased(CorNomenclatureDeclarationMaturite, name="c_maturite")
        c_paturage_type = aliased(CorNomenclatureDeclarationPaturageType, name="c_paturage_type")
        c_paturage_saison = aliased(CorNomenclatureDeclarationPaturageSaison, name="c_paturage_saison")
        c_protection_type = aliased(CorNomenclatureDeclarationProtectionType, name="c_protection_type")
        c_espece = aliased(CorNomenclatureDeclarationEspece, name="c_espece")
        c_origine = aliased(CorNomenclatureDeclarationOrigine, name="c_origine")

        peuplement_nomenclatures_cte = (
            select(
                d2.id_declaration,
                # mnemo
                get_nomenclature_mnemoniques(func.array_agg(c_maturite.id_nomenclature.distinct())).label("peuplement_maturite_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_origine.id_nomenclature.distinct())).label("peuplement_origine2_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_ess_2.id_nomenclature.distinct())).label("peuplement_ess_2_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_ess_3.id_nomenclature.distinct())).label("peuplement_ess_3_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_paturage_type.id_nomenclature.distinct())).label("peuplement_paturage_type_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_paturage_saison.id_nomenclature.distinct())).label("peuplement_paturage_saison_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_protection_type.id_nomenclature.distinct())).label("peuplement_protection_type_mnemo"),
                get_nomenclature_mnemoniques(func.array_agg(c_espece.id_nomenclature.distinct())).label("espece_mnemo"),
                # label
                get_nomenclature_labels(func.array_agg(c_maturite.id_nomenclature.distinct())).label("peuplement_maturite_label"),
                get_nomenclature_labels(func.array_agg(c_origine.id_nomenclature.distinct())).label("peuplement_origine2_label"),
                get_nomenclature_labels(func.array_agg(c_ess_2.id_nomenclature.distinct())).label("peuplement_ess_2_label"),
                get_nomenclature_labels(func.array_agg(c_ess_3.id_nomenclature.distinct())).label("peuplement_ess_3_label"),
                get_nomenclature_labels(func.array_agg(c_paturage_type.id_nomenclature.distinct())).label("peuplement_paturage_type_label"),
                get_nomenclature_labels(func.array_agg(c_paturage_saison.id_nomenclature.distinct())).label("peuplement_paturage_saison_label"),
                get_nomenclature_labels(func.array_agg(c_protection_type.id_nomenclature.distinct())).label("peuplement_protection_type_label"),
                get_nomenclature_labels(func.array_agg(c_espece.id_nomenclature.distinct())).label("espece_label"),
                # code
                get_nomenclature_codes(func.array_agg(c_maturite.id_nomenclature.distinct())).label("peuplement_maturite_code"),
                get_nomenclature_codes(func.array_agg(c_origine.id_nomenclature.distinct())).label("peuplement_origine2_code"),
                get_nomenclature_codes(func.array_agg(c_ess_2.id_nomenclature.distinct())).label("peuplement_ess_2_code"),
                get_nomenclature_codes(func.array_agg(c_ess_3.id_nomenclature.distinct())).label("peuplement_ess_3_code"),
                get_nomenclature_codes(func.array_agg(c_paturage_type.id_nomenclature.distinct())).label("peuplement_paturage_type_code"),
                get_nomenclature_codes(func.array_agg(c_paturage_saison.id_nomenclature.distinct())).label("peuplement_paturage_saison_code"),
                get_nomenclature_codes(func.array_agg(c_protection_type.id_nomenclature.distinct())).label("peuplement_protection_type_code"),
                get_nomenclature_codes(func.array_agg(c_espece.id_nomenclature.distinct())).label("espece_code"),
            )
            .select_from(d2)
            .outerjoin(c_ess_2, d2.id_declaration == c_ess_2.id_declaration)
            .outerjoin(c_ess_3, d2.id_declaration == c_ess_3.id_declaration)
            .outerjoin(c_maturite, d2.id_declaration == c_maturite.id_declaration)
            .outerjoin(c_paturage_type, d2.id_declaration == c_paturage_type.id_declaration)
            .outerjoin(c_paturage_saison, d2.id_declaration == c_paturage_saison.id_declaration)
            .outerjoin(c_protection_type, d2.id_declaration == c_protection_type.id_declaration)
            .outerjoin(c_espece, d2.id_declaration == c_espece.id_declaration)
            .outerjoin(c_origine, d2.id_declaration == c_origine.id_declaration)
            .group_by(d2.id_declaration)
            .cte("peuplement_nomenclatures")
        )

        # -------------------------
        # CTE : degat_type
        # (à adapter selon votre modèle TDegats)
        # -------------------------


        deg_1 = aliased(TDegat, name="deg_1")

        degat_type_cte = (
            select(
                deg_1.id_declaration,
                get_nomenclature_mnemoniques(func.array_agg(deg_1.id_nomenclature_degat_type.distinct())).label("degat_type_mnemos"),
                get_nomenclature_labels(func.array_agg(deg_1.id_nomenclature_degat_type.distinct())).label("degat_type_labels"),
                get_nomenclature_codes(func.array_agg(deg_1.id_nomenclature_degat_type.distinct())).label("degat_type_codes"),
            )
            .select_from(deg_1)
            .group_by(deg_1.id_declaration)
            .cte("degat_type")
        )

        # -------------------------
        # Sous-requête : areas_localisation_raw
        # -------------------------
        cad_sub = aliased(CorAreasDeclaration, name="cad")
        areas_localisation_raw_subq = (
            select(func.array_agg(cad_sub.id_area))
            .where(cad_sub.id_declaration == TDeclaration.id_declaration)
            .correlate(TDeclaration)
            .scalar_subquery()
        )

        # -------------------------
        # Requête principale
        # -------------------------
        d = TDeclaration
        f = foret_cte
        p = peuplement_cte
        pn = peuplement_nomenclatures_cte
        deg = degat_type_cte
        vu = VUsers

        query = (
            select(
                d.id_declaration,
                func.to_char(d.meta_create_date, "DD/MM/YYYY").label("declaration_date"),
                d.meta_create_date,
                d.commentaire,
                d.b_peuplement_protection_existence,
                d.b_peuplement_paturage_presence,
                d.b_autorisation,
                vu.id_role.label("id_declarant"),
                vu.nom_complet.label("declarant"),
                vu.organisme,
                # vu.organisme_group,
                vu.id_droit_max,
                vu.org_mnemo,
                f.c.id_foret,
                f.c.label_foret,
                f.c.statut_public,
                f.c.document,
                f.c.b_statut_public,
                f.c.b_document,
                f.c.type_foret,
                f.c.foret_type_label,
                # Zones géographiques
                get_area_names(d.id_declaration, "OEASC_COMMUNE").label("communes"),
                get_area_names(d.id_declaration, "OEASC_SECTEUR").label("secteur"),
                case(
                    (and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_ONF_UG")),
                    else_=get_area_names(d.id_declaration, "OEASC_CADASTRE")
                ).label("parcelles"),
                # Peuplement simple
                p.c.peuplement_surface,
                p.c.peuplement_type_mnemo,
                p.c.peuplement_origine_mnemo,
                pn.c.peuplement_origine2_mnemo,
                pn.c.peuplement_maturite_mnemo,
                p.c.peuplement_ess_1_mnemo,
                pn.c.peuplement_ess_2_mnemo,
                pn.c.peuplement_ess_3_mnemo,
                p.c.peuplement_paturage_statut_mnemo,
                p.c.peuplement_paturage_frequence_mnemo,
                pn.c.peuplement_paturage_type_mnemo,
                pn.c.peuplement_paturage_saison_mnemo,
                pn.c.peuplement_protection_type_mnemo,
                pn.c.espece_mnemo,
                p.c.peuplement_acces_mnemo,
                deg.c.degat_type_mnemos,
                # Labels
                p.c.peuplement_type_label,
                p.c.peuplement_origine_label,
                pn.c.peuplement_origine2_label,
                pn.c.peuplement_maturite_label,
                p.c.peuplement_ess_1_label,
                pn.c.peuplement_ess_2_label,
                pn.c.peuplement_ess_3_label,
                p.c.peuplement_paturage_statut_label,
                p.c.peuplement_paturage_frequence_label,
                pn.c.peuplement_paturage_type_label,
                pn.c.peuplement_paturage_saison_label,
                # Gestion du "autre_protection"
                case(
                    (d.autre_protection != None,
                    func.replace(
                        cast(pn.c.peuplement_protection_type_label, Text),
                        "Autre (préciser)",
                        d.autre_protection
                    )),
                    else_=cast(pn.c.peuplement_protection_type_label, Text)
                ).label("peuplement_protection_type_label"),
                pn.c.espece_label,
                p.c.peuplement_acces_label,
                deg.c.degat_type_labels,
                # Codes
                p.c.peuplement_type_code,
                p.c.peuplement_origine_code,
                pn.c.peuplement_origine2_code,
                pn.c.peuplement_maturite_code,
                p.c.peuplement_ess_1_code,
                pn.c.peuplement_ess_2_code,
                pn.c.peuplement_ess_3_code,
                p.c.peuplement_paturage_statut_code,
                p.c.peuplement_paturage_frequence_code,
                pn.c.peuplement_paturage_type_code,
                pn.c.peuplement_paturage_saison_code,
                pn.c.peuplement_protection_type_code,
                pn.c.espece_code,
                p.c.peuplement_acces_code,
                deg.c.degat_type_codes,
                d.precision_localisation,
                d.centroid,
                d.date_fin,
                d.status,
                d.token_renouvellement,
                # Areas foret (id)
                case(
                    (and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_ONF_FRT")),
                    (and_(f.c.b_statut_public == False, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_DGD")),
                    else_=get_id_areas(d.id_declaration, "OEASC_SECTION")
                ).label("areas_foret"),
                # Areas foret (noms)
                case(
                    (and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_ONF_FRT")),
                    (and_(f.c.b_statut_public == False, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_DGD")),
                    else_=get_area_names(d.id_declaration, "OEASC_SECTION")
                ).label("areas_foret_names"),
                # Validation
                case(
                    (d.b_valid == True, "Validé"),
                    (d.b_valid == False, "Non validé"),
                    else_="En attente"
                ).label("valide"),
                d.b_valid,
                areas_localisation_raw_subq.label("areas_localisation_raw"),
                # Areas localisation
                case(
                    (and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_ONF_UG")),
                    else_=get_id_areas(d.id_declaration, "OEASC_CADASTRE")
                ).label("areas_localisation"),
            )
            .select_from(d)
            .join(vu, vu.id_role == d.id_declarant)
            .join(f, f.c.id_foret == d.id_foret)
            .join(p, p.c.id_declaration == d.id_declaration)
            .join(pn, pn.c.id_declaration == d.id_declaration)
            .join(deg, deg.c.id_declaration == d.id_declaration)
        )

        return query
