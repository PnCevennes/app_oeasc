"""
api pour la table ref_geo
"""

# from geojson import FeatureCollection
from sqlalchemy import text, select
from flask import Blueprint, request, current_app
from utils_flask_sqla.response import json_resp

from .models import (
    # TAreas,
    # VAreas,
    VMAreasSimples,
    LAreas,
    BibAreasType,
    CorHierarchieArea,
    CorAreaIntersect,
)
from .schema import (
    VMAreasSimplesSchema,
    BibAreasTypeSchema,
    CorHierarchieAreaSchema,
)

from .repository import (
    get_id_type,
    areas_from_type_code,
    areas_from_type_code_container,
    areas_post,
    set_table_and_schema,
    build_area_hierarchy,
)

bp = Blueprint("ref_geo", __name__)

config = current_app.config

DB = config["DB"]


@bp.route("type_codes_oeasc")
@json_resp
def get_type_code_oeasc():
    """
    renvoie les element de bibareastype relatifs à l'OEASC
    """
    # Prépare une requête SQLAlchemy pour sélectionner les types d'aires
    # dont le champ ref_name est soit "OEASC" soit "ONF".
    # Ces valeurs correspondent aux référentiels utilisés dans le projet OEASC
    # et par l'Office National des Forêts (ONF).
    stmt_data = (
        select(BibAreasType)
        .where(BibAreasType.ref_name.in_(("OEASC", "ONF")))
        .order_by(BibAreasType.type_code)  # Trie les résultats par code de type
    )

    # Exécute la requête sur la base de données et récupère tous les résultats.
    data = DB.session.execute(stmt_data).scalars().all()

    # Sérialise les objets BibAreasType en dictionnaires JSON
    # grâce au schéma BibAreasTypeSchema.
    areasType_dict = BibAreasTypeSchema(many=True).dump(data)

    # Retourne la liste des types d'aires au format JSON.
    # Cette fonction est utilisée pour afficher dans l'interface
    # les différents types d'aires disponibles pour OEASC et ONF,
    # par exemple lors du paramétrage ou du filtrage des données géographiques.
    return areasType_dict


@bp.route("get_id_type/<string:type_code>")
@json_resp
def get_id_type_api(type_code):
    """
    Récupère l'identifiant du type d'aire à partir de son code.

    Cette fonction est utilisée pour obtenir l'id_type correspondant à un type_code donné,
    par exemple "OEASC_CADASTRE". Cela permet de faire le lien entre le code utilisé dans
    l'interface ou les requêtes et l'identifiant interne en base de données.

    Utilisation typique :
    - Lorsqu'on souhaite filtrer ou récupérer des aires selon leur type,
      il est nécessaire d'obtenir l'id_type à partir du type_code.
    - Peut être utilisé dans des requêtes où l'id_type est requis pour des jointures
      ou des recherches dans d'autres tables.

    Exemple d'URL : /get_id_type/OEASC_CADASTRE
    """
    return get_id_type(type_code)


@bp.route("area/<string:data_type>/<int:id_area>")
@json_resp
def get_area(data_type, id_area):
    """
    Récupère une aire spécifique en fonction de son identifiant.

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Exemple d'URL : /area/l/277431

    Cette fonction est utilisée :
    - Lorsqu'on souhaite afficher ou récupérer les informations détaillées d'une aire précise,
      par exemple pour afficher la fiche d'une aire dans l'interface utilisateur.
    - Pour obtenir la géométrie d'une aire afin de l'afficher sur une carte (si data_type == "l").
    - Dans des traitements où l'on a besoin de toutes les propriétés d'une aire à partir de son identifiant.
    """
    # On récupère la table et le schéma correspondant au type de données demandé
    # b_simple=True signifie qu'on utilise la version "simple" (sans géométrie complexe)

    table, schema = set_table_and_schema(b_simple=True, data_type=data_type)

    # On prépare la requête SQLAlchemy pour sélectionner l'aire dont l'id correspond à id_area
    stmt_area = (
        select(table)
        .where(table.id_area == id_area)
        .limit(1)  # On limite à un seul résultat (l'id_area étant unique)
    )
    # On exécute la requête et on récupère le premier résultat (ou None si non trouvé)
    data = DB.session.execute(stmt_area).scalars().first()

    # Si le type de données est "l", on retourne le résultat au format GeoJSON
    if data_type == "l":
        result = schema(as_geojson=True).dump(data)
        return result
    else:
        # Sinon, on retourne les attributs sous forme de dictionnaire classique
        return schema().dump(data)


@bp.route("areas/<string:data_type>/<string:id_areas>", methods=["GET"])
@json_resp
def get_areas_liste(data_type, id_areas):
    """
    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)
    Cette fonction est utilisée pour récupérer des aires spécifiques en fonction de leurs identifiants.
    Exemple d'URL : /areas/l/277431-277432-277433

    Utilisation typique :
    - Pour afficher sur une carte ou dans une liste plusieurs aires sélectionnées par l'utilisateur.
    - Lorsqu'on souhaite récupérer les informations détaillées de plusieurs aires en une seule requête.
    - Pour des traitements batch où l'on a besoin des propriétés ou de la géométrie de plusieurs aires.
    """
    # On découpe la chaîne d'identifiants reçue dans l'URL en une liste Python.
    # Les identifiants sont séparés par des tirets, ex : "277431-277432-277433"
    liste_areas = id_areas.split("-")

    # On récupère la table SQLAlchemy et le schéma de sérialisation correspondant au type de données demandé.
    # b_simple=True signifie qu'on utilise la version "simple" (géométrie simplifiée ou attributs uniquement).
    table, schema = set_table_and_schema(b_simple=True, data_type=data_type)

    # On prépare la requête SQLAlchemy pour sélectionner toutes les aires dont l'id_area est dans la liste.
    stmt_area = select(table).where(table.id_area.in_(liste_areas))

    # On exécute la requête sur la base de données et on récupère tous les résultats.
    data = DB.session.execute(stmt_area).scalars().all()

    # Si le type de données est "l", on retourne les résultats au format GeoJSON (pour affichage cartographique).
    if data_type == "l":
        return schema(many=True, as_geojson=True).dump(data)
    else:
        # Sinon, on retourne les résultats sous forme de dictionnaires classiques (attributs uniquement).
        return schema(many=True).dump(data)


@bp.route("areas_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_post(data_type):
    """
    Cette fonction permet de récupérer les informations de plusieurs aires
    à partir d'une liste d'identifiants passée en POST (dans le corps de la requête).

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Lorsqu'on souhaite afficher ou traiter plusieurs aires sélectionnées par l'utilisateur,
      par exemple pour un affichage cartographique ou une analyse batch.
    - Quand la liste des aires à récupérer est trop longue pour être passée dans l'URL,
      on utilise une requête POST avec un JSON contenant les identifiants.
    - Pour des traitements côté client où l'on envoie dynamiquement une liste d'aires à l'API.

    Exemple de payload JSON :
    {
        "areas": [277431, 277432, 277433]
    }
    """
    # On récupère le contenu JSON envoyé dans la requête POST
    data_in = request.get_json()

    # On extrait la liste des identifiants d'aires à partir du JSON
    areas = data_in["areas"]

    # b_simple=False signifie qu'on veut la version complète (avec géométrie si data_type == "l")
    b_simple = False

    # On appelle la fonction générique qui va interroger la base et sérialiser les résultats
    return areas_post(b_simple, data_type, areas)


@bp.route("areas_from_type/<string:data_type>", methods=["GET"])
@json_resp
def get_areas(data_type):
    """
    Récupère les informations de plusieurs aires à partir d'une liste d'identifiants passée en GET.

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Lorsqu'on souhaite afficher ou traiter plusieurs aires sélectionnées par l'utilisateur,
      par exemple pour un affichage cartographique ou une analyse batch.
    - Quand la liste des aires à récupérer est passée en paramètres GET (dans l'URL),
      sous forme de liste d'identifiants.
    - Pour des traitements côté client où l'on envoie dynamiquement une liste d'aires à l'API.

    Exemple d'URL :
    /areas_from_type/l?id_area=277431&id_area=277432&id_area=277433
    """
    # On récupère la liste des identifiants d'aires passée en paramètres GET (dans l'URL)
    areas = request.args.getlist("id_area")

    # b_simple=False signifie qu'on veut la version complète (avec géométrie si data_type == "l")
    b_simple = False

    # On appelle la fonction générique qui va interroger la base et sérialiser les résultats
    return areas_post(b_simple, data_type, areas)


@bp.route("areas_simple/<string:data_type>", methods=["GET"])
@json_resp
def get_areas_simple(data_type):
    """
    Récupère les informations de plusieurs aires "simples" à partir d'une liste d'identifiants passée en GET.

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Lorsqu'on souhaite afficher ou traiter plusieurs aires sélectionnées par l'utilisateur,
      par exemple pour un affichage cartographique ou une analyse batch.
    - Quand la liste des aires à récupérer est passée en paramètres GET (dans l'URL),
      sous forme de liste d'identifiants.
    - Pour des traitements côté client où l'on envoie dynamiquement une liste d'aires à l'API.

    Exemple d'URL :
    /areas_simple/l?id_area=277431&id_area=277432&id_area=277433
    """
    # On récupère la liste des identifiants d'aires passée en paramètres GET (dans l'URL)
    areas = request.args.getlist("id_area")

    # b_simple=True signifie qu'on utilise la version "simple" (géométrie simplifiée ou attributs uniquement)
    b_simple = True

    # On appelle la fonction générique qui va interroger la base et sérialiser les résultats
    return areas_post(b_simple, data_type, areas)


@bp.route("areas_simples_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_simples_post(data_type):
    """
    Cette fonction permet de récupérer les informations de plusieurs aires "simples"
    à partir d'une liste d'identifiants passée en POST (dans le corps de la requête).

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Lorsqu'on souhaite afficher ou traiter plusieurs aires sélectionnées par l'utilisateur,
      par exemple pour un affichage cartographique ou une analyse batch.
    - Quand la liste des aires à récupérer est trop longue pour être passée dans l'URL,
      on utilise une requête POST avec un JSON contenant les identifiants.
    - Pour des traitements côté client où l'on envoie dynamiquement une liste d'aires à l'API.

    Exemple de payload JSON :
    {
        "areas": [277431, 277432, 277433]
    }
    """
    # On récupère le contenu JSON envoyé dans la requête POST
    data_in = request.get_json()

    # On extrait la liste des identifiants d'aires à partir du JSON
    areas = data_in["areas"]

    # b_simple=True signifie qu'on utilise la version "simple" (géométrie simplifiée ou attributs uniquement)
    b_simple = True

    # On appelle la fonction générique qui va interroger la base et sérialiser les résultats
    return areas_post(b_simple, data_type, areas)


@bp.route("areas_centroid_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_centroid_post(data_type):
    """
    Cette fonction permet de calculer le centroïde (centre géométrique) d'un ensemble d'aires
    dont les identifiants sont transmis via une requête POST au format JSON.

    Utilisation typique :
    - Pour afficher le centre d'un groupe d'aires sur une carte (par exemple, zoomer sur un ensemble d'entités).
    - Pour des traitements spatiaux où l'on souhaite connaître le point central d'une sélection d'aires.
    - Peut être utilisée côté client pour obtenir rapidement la position centrale d'une sélection multiple.
    """
    # On récupère le dictionnaire JSON envoyé dans la requête POST.
    # Ce dictionnaire doit contenir des clés (groupes ou catégories) et des valeurs (listes d'id_area).
    d_areas = request.get_json()

    # Dictionnaire de sortie qui contiendra pour chaque clé le centroïde calculé.
    d_out = {}

    # On parcourt chaque groupe d'aires transmis dans le JSON.
    for key, value in d_areas.items():
        v = value

        # On convertit la liste d'identifiants en tuple pour l'utiliser dans la requête SQL.
        t = tuple(v)

        # Si la liste ne contient qu'un seul identifiant, on adapte le format pour la requête SQL.
        if len(v) == 1:
            t = str(t).replace(",", "")

        # On prépare la requête SQL pour calculer le centroïde :
        # - ST_UNION(geom_4326) fusionne toutes les géométries des aires sélectionnées.
        # - ST_CENTROID calcule le centre de la géométrie fusionnée.
        # - ST_X et ST_Y récupèrent les coordonnées du centroïde.
        sql_text = text("SELECT ST_X(c),ST_Y(c) \
            FROM (SELECT ST_CENTROID(ST_UNION(geom_4326)) as c \
            FROM ref_geo.l_areas \
            WHERE id_area in :areas )a").bindparams(areas=t)
        result = DB.session.execute(sql_text).first()

        # On inverse l'ordre des coordonnées pour obtenir [latitude, longitude].
        v = [result[1], result[0]]
        d_out[key] = v

    # On retourne le dictionnaire contenant pour chaque groupe le centroïde calculé.
    return d_out


@bp.route(
    "areas_from_type_code/<string:data_type>/<string:type_code>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_from_type_code(data_type, type_code):
    """
    Retourne toutes les aires pour un type_code donné (par exemple OEASC_CADASTRE).

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Lorsqu'on souhaite afficher ou récupérer toutes les aires d'un certain type,
      par exemple toutes les parcelles cadastrales, toutes les forêts, etc.
    - Pour filtrer les données géographiques selon leur type dans l'interface utilisateur,
      lors du paramétrage ou du filtrage cartographique.
    - Utile pour des analyses spatiales ou statistiques sur un ensemble homogène d'aires.
    - Peut être utilisé côté client pour afficher sur une carte toutes les entités d'un type donné.
    - La distinction entre "t" et "l" permet d'obtenir soit les attributs seuls, soit les géométries pour affichage cartographique.
    """

    # On appelle la fonction générique qui interroge la base de données
    # pour récupérer toutes les aires correspondant au type_code donné.
    # b_simple=False signifie qu'on veut la version complète (avec géométrie si data_type == "l").
    return areas_from_type_code(False, data_type, type_code)


@bp.route(
    "areas_simples_from_type_code/<string:data_type>/<string:type_code>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_simples_from_type_code(data_type, type_code):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie
    """

    data = areas_from_type_code(True, data_type, type_code)

    return data


@bp.route(
    "areas_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<string:ids_area_container>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_from_type_code_container(data_type, type_code, ids_area_container):
    """
    Retourne toutes les aires pour un type_code donné (par exemple OEASC_CADASTRE)
    et étant contenue dans la géométrie identifiée par son id_area : id_area_container
    la recherche de ses éléments se fait par rapport aux area_code:
        - soit en comparant les area_code des contenus et du contenant (cas général)
        - soit en se servant d'une table de corrélation pré-calculée
            pour le cas des forêts avec DGD
    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la géométrie
    """

    b_simple = False
    return areas_from_type_code_container(
        b_simple, data_type, type_code, ids_area_container
    )


@bp.route(
    "areas_simples_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<ids_area_container>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_simples_from_type_code_container(
    data_type, type_code, ids_area_container
):
    """
    Retourne toutes les aires "simples" pour un type_code donné (par exemple OEASC_CADASTRE)
    et étant contenues dans la géométrie identifiée par son id_area : id_area_container.

    La recherche des éléments contenus se fait :
        - soit en comparant les area_code des contenus et du contenant (cas général)
        - soit en utilisant une table de corrélation pré-calculée (cas particulier, ex : forêts avec DGD)

    data_type :
        t -> renvoie seulement les attributs (sans géométrie)
        l -> renvoie aussi la géométrie (format GeoJSON)

    Utilisation typique :
    - Pour afficher sur une carte toutes les entités d'un type donné qui sont contenues dans une aire "contenant"
      (ex : toutes les parcelles cadastrales dans une commune, tous les peuplements dans une forêt, etc.).
    - Utile pour des analyses spatiales où l'on souhaite filtrer les entités par inclusion géographique.
    - Permet de réaliser des recherches spatiales complexes côté client ou serveur, en limitant les résultats
      à une zone géographique précise.
    - La version "simple" est utilisée pour optimiser les performances (géométrie simplifiée ou attributs uniquement).

    """
    # On indique que l'on souhaite la version "simple" des aires (b_simple=True)
    b_simple = True

    # On appelle la fonction générique qui interroge la base de données pour récupérer les aires
    # correspondant au type_code et contenues dans l'aire spécifiée par ids_area_container.
    # Cette fonction gère la logique de comparaison des area_code ou l'utilisation de la table de corrélation.
    return areas_from_type_code_container(
        b_simple, data_type, type_code, ids_area_container
    )


@bp.route("areas_child_of/<int:id_type>/<int:id_area>", methods=["GET"])
@json_resp
def get_areas_child_of(id_type, id_area):
    """
    Récupère les aires enfants d'une aire spécifique en fonction de son identifiant.

    Utilisation typique :
    - Pour afficher sur une carte ou dans une liste tous les enfants d'une aire donnée (ex : toutes les parcelles d'une commune, tous les peuplements d'une forêt, etc.).
    - Lorsqu'on souhaite explorer la hiérarchie spatiale ou administrative des aires (parent/enfant).
    - Utile pour des analyses spatiales ou des traitements où l'on doit connaître les entités incluses dans une autre.

    id_type : identifiant du type d'aire (ex : type de commune, de parcelle, etc.)
    id_area : identifiant de l'aire parent (ex : id d'une commune ou d'une forêt)
    Exemple d'URL : /areas_child_of/1/277431
    """

    # On prépare une requête SQLAlchemy pour récupérer toutes les relations de hiérarchie
    # où l'aire parent correspond à id_area et le type du parent à id_type.
    # Cela permet d'obtenir tous les liens vers les aires enfants de ce parent.
    stmt = (
        select(CorHierarchieArea)
        .where(CorHierarchieArea.id_area_parent == id_area)
        .where(CorHierarchieArea.id_type_parent == id_type)
    )
    all_child_areas = DB.session.execute(stmt).scalars().all()

    # On extrait la liste des identifiants des aires enfants à partir des résultats précédents.
    # Cela permet de récupérer ensuite les informations détaillées de chaque aire enfant.
    child_ids = [child.id_area_enfant for child in all_child_areas]

    # On prépare une requête pour récupérer les données des aires enfants
    # à partir de la vue simplifiée vm_lareas_simples.
    stmt_areas = select(VMAreasSimples).where(VMAreasSimples.id_area.in_(child_ids))
    data = DB.session.execute(stmt_areas).scalars().all()

    # On utilise le schéma VMAreasSimplesSchema pour sérialiser les données au format GeoJSON,
    # ce qui est utile pour l'affichage cartographique ou le transfert de données spatiales.
    all_areas = VMAreasSimplesSchema(many=True, as_geojson=True, include_geom=True).dump(data)

    # On retourne la liste des aires enfants au format JSON (GeoJSON si demandé).
    return all_areas


@bp.route("areas_infos_from_parcelles", methods=["GET"])
@json_resp
def get_areas_infos_from_parcelles():
    """
    Retourne les forêts, secteurs et communes associés à une liste de parcelles
    via la table cor_area_intersect.

    Paramètre GET : id_parcelle (répétable)
    Exemple : /areas_infos_from_parcelles?id_parcelle=123&id_parcelle=456

    Réponse : {"forets": [...], "secteurs": [...], "communes": [...]}
    Chaque élément contient les attributs VMAreasSimples (sans géométrie).
    """
    id_parcelles = request.args.getlist("id_parcelle", type=int)
    if not id_parcelles:
        return {"forets": [], "secteurs": [], "communes": []}

    intersects = (
        DB.session.execute(
            select(CorAreaIntersect).where(CorAreaIntersect.id_parcelle.in_(id_parcelles))
        )
        .scalars()
        .all()
    )

    ids_foret = set()
    ids_secteur = set()
    ids_commune = set()
    for row in intersects:
        for fid in (row.id_foret_onf, row.id_foret_dgd, row.id_foret_prive):
            if fid is not None:
                ids_foret.add(fid)
        if row.id_secteur is not None:
            ids_secteur.add(row.id_secteur)
        if row.id_commune is not None:
            ids_commune.add(row.id_commune)

    schema = VMAreasSimplesSchema

    def fetch_areas(ids):
        if not ids:
            return []
        data = DB.session.execute(
            select(VMAreasSimples).where(VMAreasSimples.id_area.in_(ids))
        ).scalars().all()
        return schema(many=True).dump(data)

    return {
        "forets": fetch_areas(ids_foret),
        "secteurs": fetch_areas(ids_secteur),
        "communes": fetch_areas(ids_commune),
    }


@bp.route("areas_hierarchy/<string:id_areas>", methods=["GET"])
@json_resp
def get_areas_hierarchy(id_areas):
    """
    Récupère la hiérarchie des aires à partir d'une liste d'identifiants.

    Utilisation typique :
    - Pour afficher la structure hiérarchique des aires sélectionnées (ex : communes, parcelles, peuplements, etc.).
    - Utile dans l'interface utilisateur pour visualiser les relations parent/enfant entre entités géographiques.
    - Permet d'obtenir à la fois les informations des aires et leur organisation hiérarchique (ex : arbre, graphe).
    - Peut servir pour des analyses spatiales ou administratives où la notion de hiérarchie est importante.

    id_areas : liste des identifiants d'aires à récupérer, séparés par des tirets.
    Exemple d'URL : /areas_hierarchy/277431-277432-277433
    """

    # On découpe la chaîne d'identifiants reçue dans l'URL en une liste Python.
    # Les identifiants sont séparés par des tirets, ex : "277431-277432-277433"
    liste_areas = id_areas.split("-")

    # On prépare la requête SQLAlchemy pour récupérer les informations des aires
    # à partir de la vue VAreas, qui contient les attributs détaillés des aires.
    stmt_area = select(VMAreasSimples).where(VMAreasSimples.id_area.in_(liste_areas))
    # On exécute la requête et on récupère tous les résultats.
    data = DB.session.execute(stmt_area).scalars().all()
    # On sérialise via VMAreasSimplesSchema (sans géométrie) pour éviter l_areas.description.
    data_result = VMAreasSimplesSchema(many=True).dump(data)

    # On prépare une requête SQLAlchemy pour récupérer les relations de hiérarchie
    # où l'aire enfant correspond à l'un des identifiants transmis.
    # Cela permet d'obtenir les liens parent/enfant pour les aires sélectionnées.
    stmt_hierarchy = select(CorHierarchieArea).where(
        # On sélectionne les relations où l'id_area_enfant est dans la liste des identifiants.
        (CorHierarchieArea.id_area_enfant.in_(liste_areas))
    )
    # On exécute la requête et on récupère tous les résultats.
    hierarchy_data = DB.session.execute(stmt_hierarchy).scalars().all()
    # On sérialise les objets CorHierarchieArea en dictionnaires JSON grâce au schéma CorHierarchieAreaSchema.
    hierarchy_result = CorHierarchieAreaSchema(many=True).dump(hierarchy_data)

    # On construit la hiérarchie à partir des données récupérées :
    # - data_result contient les informations des aires (attributs).
    # - hierarchy_result contient les liens parent/enfant.
    # La fonction build_area_hierarchy organise ces données en structure hiérarchique (arbre ou graphe).
    hierarchy = build_area_hierarchy(data_result, hierarchy_result)

    # On retourne la hiérarchie construite au format JSON.
    return hierarchy


@bp.route("declaration_hierarchy_from_intersect", methods=["GET"])
@json_resp
def get_declaration_hierarchy_from_intersect():
    """
    Construit la hiérarchie des areas d'une déclaration à partir de CorAreaIntersect.
    Plus fiable que areas_hierarchy qui s'appuie sur cor_hierarchie_area (souvent incomplet).

    Query params :
      - id_cadastre (répétable) : IDs des parcelles cadastrales
      - id_ug (répétable)       : IDs des unités de gestion ONF
      - b_document              : "true" / "false"
      - b_statut_public         : "true" / "false"
    """
    id_cadastres = [int(x) for x in request.args.getlist("id_cadastre") if x]
    id_ugs = [int(x) for x in request.args.getlist("id_ug") if x]
    b_document = request.args.get("b_document") == "true"
    b_statut_public = request.args.get("b_statut_public") == "true"

    leaf_ids = id_cadastres + id_ugs
    if not leaf_ids:
        return []

    intersect_rows = DB.session.execute(
        select(CorAreaIntersect).where(CorAreaIntersect.id_parcelle.in_(leaf_ids))
    ).scalars().all()

    all_ids = set(leaf_ids)
    relations_set = set()

    for row in intersect_rows:
        # UG ONF : toujours hiérarchie ONF (foret_onf → parcelle_onf → ug)
        if row.id_parcelle in id_ugs:
            if row.id_parcelle_onf:
                relations_set.add((row.id_parcelle, row.id_parcelle_onf))
                all_ids.add(row.id_parcelle_onf)
            if row.id_foret_onf and row.id_parcelle_onf:
                relations_set.add((row.id_parcelle_onf, row.id_foret_onf))
                all_ids.add(row.id_foret_onf)
        # Cadastres : hiérarchie selon le type de forêt
        elif row.id_parcelle in id_cadastres:
            if b_document and not b_statut_public:
                # Forêt DGD : foret_dgd → cadastre
                if row.id_foret_dgd:
                    relations_set.add((row.id_parcelle, row.id_foret_dgd))
                    all_ids.add(row.id_foret_dgd)
            else:
                # Hors forêt : commune → section → cadastre
                if row.id_section_cadastrale:
                    relations_set.add((row.id_parcelle, row.id_section_cadastrale))
                    all_ids.add(row.id_section_cadastrale)
                if row.id_commune and row.id_section_cadastrale:
                    relations_set.add((row.id_section_cadastrale, row.id_commune))
                    all_ids.add(row.id_commune)

    relations = [
        {"id_area_enfant": enfant, "id_area_parent": parent}
        for enfant, parent in relations_set
    ]

    areas = DB.session.execute(
        select(VMAreasSimples).where(VMAreasSimples.id_area.in_(list(all_ids)))
    ).scalars().all()
    data_result = VMAreasSimplesSchema(many=True).dump(areas)

    return build_area_hierarchy(data_result, relations)
