"""
degat module api
"""

from flask import current_app
from ..declaration.models import TProprietaire, TForet, TDeclaration
from ..declaration.repository import patch_areas_declarations
from ..nomenclature import get_area_from_id, get_nomenclature_from_id
from ..user.models import VUsers
from sqlalchemy import select
from ..declaration.schema import (
    TDeclarationSchema,
    TProprietaireSchema,
    TForetSchema,
    )

config = current_app.config
DB = config["DB"]


def create_or_modify(model, key, dict_in, schema_cls=None):
    """
    Fonction générique de création ou modification d'une instance d'un modèle SQLAlchemy
    en utilisant Marshmallow pour la validation et le chargement des données.

    :param model: Le modèle SQLAlchemy à mettre à jour ou insérer (ex: TProprietaire, TForet, TDeclaration).
    :param key: La clé primaire du modèle (ex: "id_proprietaire", "id_foret", "id_declaration").
    :param dict_in: Les données à insérer ou mettre à jour (sous forme de dictionnaire).
    :param schema_cls: La classe du schéma Marshmallow à utiliser (optionnel, sinon déduit automatiquement).
    :return: L'instance mise à jour ou insérée.
    """

    elem = None  # Instance existante ou à créer

    # Si une clé primaire est fournie, on tente de récupérer l'instance existante en base
    if key:
        val = dict_in.get(key, None)
        if val:
            stmt_elem = (
                select(model).where(getattr(model, key) == val)
                .limit(1)
            )
            elem = DB.session.execute(stmt_elem).scalars().first()

    # Si le schéma Marshmallow n'est pas fourni, on le déduit du nom du modèle
    if schema_cls is None:
        schema_name = model.__name__ + "Schema"
        schema_cls = globals().get(schema_name)
        if schema_cls is None:
            raise ValueError(f"Schéma Marshmallow non trouvé pour {model.__name__}")

    schema = schema_cls()

    # Si l'instance existe, on la met à jour avec les nouvelles données
    if elem is not None:
        elem = schema.load(dict_in, instance=elem, session=DB.session, partial=True)
    else:
        # Sinon, on crée une nouvelle instance avec les données fournies
        elem = schema.load(dict_in, session=DB.session, partial=True)
        DB.session.add(elem)

    # On valide et on enregistre les modifications en base
    DB.session.commit()
    return elem


def update_or_insert(model, id_key, id_value, schema, data, session=None):
    """
    Met à jour ou insère une instance d'un modèle SQLAlchemy via marshmallow.

    :param model: Le modèle SQLAlchemy à mettre à jour ou insérer (ex: TProprietaire, TForet, TDeclaration).
    :param id_key: La clé primaire du modèle (ex: "id_proprietaire", "id_foret", "id_declaration").
    :param id_value: La valeur de la clé primaire à rechercher ou insérer.
    :param schema: Le schéma Marshmallow à utiliser pour la validation et le chargement des données.
    :param data: Les données à valider et à insérer ou mettre à jour (dictionnaire).
    :param session: La session SQLAlchemy à utiliser (optionnel, sinon DB.session).
    :return: L'instance mise à jour ou insérée.
    """

    instance = None  # Instance existante ou à créer

    # Si aucune session n'est fournie, on utilise celle de l'application
    if not session:
        session = DB.session

    # Si une valeur de clé primaire est fournie, on tente de récupérer l'instance existante en base
    if id_value: 
        instance = session.get(model, id_value)

    if instance:
        # Si l'instance existe, on la met à jour avec les nouvelles données
        instance = schema.load(data, instance=instance, session=session, partial=True)
    else:
        # Si l'instance n'existe pas, on la crée
        # On retire la clé primaire des données pour éviter les conflits lors de la création
        data.pop(id_key, None)
        # On charge l'instance via Marshmallow et on l'ajoute à la session
        instance = schema.load(data, session=session)
        session.add(instance)

    # On valide et on enregistre les modifications en base
    session.commit()

    return instance


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
            select(TForet)
            .where(TForet.id_foret == declaration.id_foret)
            .limit(1)
        )
        foret = DB.session.execute(stmt_foret).scalars().first()

        # On récupère le propriétaire associé à la forêt
        stmt_proprietaire = (
            select(TProprietaire)
            .where(TProprietaire.id_proprietaire == foret.id_proprietaire)
            .limit(1)
        )
        proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    except Exception:
        # En cas d'erreur (ex: id non trouvé), on retourne des instances vides
        return (TDeclaration(), TForet(), TProprietaire())

    return (declaration, foret, proprietaire)


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
    arranged_post_data["id_nomenclature_peuplement_type"] = post_data.get("id_nomenclature_peuplement_type")
    arranged_post_data["id_nomenclature_peuplement_acces"] = post_data.get("id_nomenclature_peuplement_acces")
    arranged_post_data["id_nomenclature_peuplement_essence_principale"] = post_data.get("id_nomenclature_peuplement_essence_principale")
    arranged_post_data["meta_create_date"] = post_data.get("meta_create_date")
    arranged_post_data["meta_update_date"] = None # sera mis à jour dans la bdd

    arranged_post_data["b_peuplement_protection_existence"] = post_data.get("b_peuplement_protection_existence")
    arranged_post_data["b_peuplement_paturage_presence"] = post_data.get("b_peuplement_paturage_presence")
    arranged_post_data["b_autorisation"] = post_data.get("b_autorisation")
    arranged_post_data["b_valid"] = post_data.get("b_valid")

    arranged_post_data["id_nomenclature_proprietaire_declarant"] = post_data.get("id_nomenclature_proprietaire_declarant")
    arranged_post_data["id_nomenclature_peuplement_origine"] = post_data.get("id_nomenclature_peuplement_origine")
    arranged_post_data["id_nomenclature_foret_type"] = post_data.get("id_nomenclature_foret_type")
    arranged_post_data["id_nomenclature_peuplement_paturage_frequence"] = post_data.get("id_nomenclature_peuplement_paturage_frequence")
    arranged_post_data["id_nomenclature_peuplement_paturage_statut"] = post_data.get("id_nomenclature_peuplement_paturage_statut")
    arranged_post_data["peuplement_surface"] = post_data.get("peuplement_surface")
    arranged_post_data["autre_protection"] = post_data.get("autre_protection")
    arranged_post_data["precision_localisation"] = post_data.get("precision_localisation")
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
        {"id_area": id_area}
        for id_area in post_data["areas_localisation"]
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
        data_proprio["id_nomenclature_proprietaire_type"] = post_data.get("id_nomenclature_proprietaire_type")

        # Si modification d'un propriétaire existant
        if post_data.get("id_proprietaire"): 
            data_proprio["id_declaration"] = post_data.get("id_declaration")
            proprietaire_bdd = DB.session.get(TProprietaire, post_data.get("id_declaration"))
        
            proprietaire = proprietaireSchema.load(
                data_proprio,
                instance=proprietaire_bdd,
                partial=True, # Mise à jour partielle
                session=DB.session
            )
            DB.session.commit() # modification de l'instance

        else: 
            # Création d'un nouveau propriétaire
            proprietaire = proprietaireSchema.load(
                data_proprio, session=DB.session, partial=True
            )
            DB.session.add(proprietaire)
            DB.session.commit() # ajout de l'instance
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
            for id_area in post_data.get("areas_foret", []) if id_area is not None
        ]

        # Création de la forêt
        foretSchema = TForetSchema()
        new_foret = foretSchema.load(
            data_foret, session=DB.session, partial=True
        )
        DB.session.add(new_foret)
        DB.session.commit()
        arranged_post_data["id_foret"] = new_foret.id_foret 

    else: 
        # Cas 2 : La parcelle a un document de gestion durable (forêt existante)
        # On récupère la forêt existante à partir du code_area
        id_area_foret = post_data["areas_foret_onf"] or post_data["areas_foret_dgd"]
        code_foret = get_area_from_id(id_area_foret)["area_code"]

        stmt_foret = (select(TForet)
        .where(TForet.code_foret == code_foret)
        .limit(1)              
        )
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
            partial=True, # Mise à jour partielle
            session=DB.session
        )
        # declaration.degats = arranged_post_data.get("degats", [])
    else: 
        # Création d'une nouvelle déclaration
        declaration = declarationSchema.load(
            arranged_post_data, session=DB.session, partial=True
        )
        DB.session.add(declaration)

    DB.session.commit()

    print("id_declaration", declaration.id_declaration)    
    
    # Mise à jour des aires liées à la déclaration (communes, secteurs, sections)
    patch_areas_declarations(declaration.id_declaration)

    # On retourne les données arrangées (utiles pour debug ou pour affichage)
    return arranged_post_data


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
    stmt_foret = (
        select(TForet)
        .where(TForet.code_foret == code_foret)
        .limit(1)
    )
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


def get_proprietaire_from_id_declarant(id_declarant):
    """
    Récupère l'objet TProprietaire associé à un identifiant de déclarant donné.

    Cette fonction effectue une requête sur la table TProprietaire afin de trouver le propriétaire
    correspondant à l'identifiant de déclarant passé en paramètre. Si aucun propriétaire n'est trouvé,
    elle retourne une nouvelle instance vide de TProprietaire.

    Args:
        id_declarant (int): L'identifiant du déclarant pour lequel on souhaite récupérer le propriétaire.

    Returns:
        TProprietaire: L'objet propriétaire correspondant à l'identifiant, ou un objet vide si aucun n'est trouvé.

    Utilisation :
        Cette fonction est généralement utilisée lors de la récupération des informations d'un propriétaire
        à partir d'un identifiant de déclarant, par exemple lors de la consultation ou de la modification
        d'une déclaration de dégâts en forêt.
    """

    stmt_proprietaire = (
        select(TProprietaire)
        .where(TProprietaire.id_declarant == id_declarant)
        .limit(1)
    )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return proprietaire or TProprietaire()



def get_proprietaire_from_id(id_proprietaire):
    """
    Récupère l'objet TProprietaire associé à un identifiant de propriétaire donné.

    Cette fonction effectue une requête sur la table TProprietaire afin de trouver le propriétaire
    correspondant à l'identifiant passé en paramètre. Si aucun propriétaire n'est trouvé,
    elle retourne une nouvelle instance vide de TProprietaire.

    Args:
        id_proprietaire (int): L'identifiant du propriétaire à rechercher.

    Returns:
        TProprietaire: L'objet propriétaire correspondant à l'identifiant, ou un objet vide si aucun n'est trouvé.

    Utilisation :
        Cette fonction est utilisée pour obtenir les informations d'un propriétaire à partir de son identifiant,
        par exemple lors de la consultation ou de la modification d'une forêt ou d'une déclaration.
    """

    stmt_proprietaire = (
        select(TProprietaire)
        .where(TProprietaire.id_proprietaire == id_proprietaire)
        .limit(1)
    )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return proprietaire or TProprietaire()


def get_declarations():
    """
    Récupère la liste des déclarations de dégâts en forêt, en joignant les informations
    de la forêt associée et de l'utilisateur déclarant.

    Utilisation :
    - Cette fonction est utilisée pour obtenir l'ensemble des déclarations enregistrées,
      avec les détails de la forêt et du déclarant (utilisateur), par exemple pour l'affichage
      dans une interface d'administration ou de suivi des déclarations.

    Fonctionnement :
    - Effectue une requête SQLAlchemy pour sélectionner les déclarations (TDeclaration),
      les forêts associées (TForet) et les utilisateurs déclarants (VUsers).
    - Les jointures sont faites sur l'identifiant de la forêt et sur le rôle de l'utilisateur
      (attention : la jointure sur VUsers semble utiliser id_role, ce qui pourrait être une erreur
      si le lien logique est plutôt id_user ou similaire).
    - Les résultats sont sérialisés via le schéma Marshmallow TDeclarationSchema.
    - Pour chaque déclaration, les informations de la forêt et de l'utilisateur sont fusionnées
      dans le dictionnaire de sortie.
    - Retourne une liste de dictionnaires contenant toutes les informations agrégées.

    Remarques :
    - Cette fonction est typiquement utilisée pour afficher un tableau récapitulatif des déclarations,
      avec les détails de la forêt et du déclarant.
    - La sérialisation des objets forêt et utilisateur utilise le même schéma que la déclaration,
      ce qui peut ne pas être optimal si les champs diffèrent.
    """

    # Préparation de la requête SQLAlchemy avec jointures sur la forêt et l'utilisateur
    stmt_declaration = (
        select(TDeclaration, TForet, VUsers)
        .join(TForet, TForet.id_foret == TDeclaration.id_foret)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)  # À vérifier selon le modèle
    )
    # Exécution de la requête et récupération des résultats
    declarations = DB.session.execute(stmt_declaration).all()
    # Initialisation du schéma Marshmallow pour la sérialisation
    declarations_schema = TDeclarationSchema(many=True)

    out = []

    # Parcours des résultats pour sérialiser et fusionner les données
    for declaration in declarations:
        d = declaration[0]  # Instance TDeclaration
        d = declarations_schema.dump(d, many=False)
        f = declaration[1]  # Instance TForet
        f = declarations_schema.dump(f, many=False)
        u = declaration[2]  # Instance VUsers
        u = declarations_schema.dump(u, many=False)

        # Fusion des informations de la forêt et de l'utilisateur dans le dictionnaire de déclaration
        d.update(f)
        d.update(u)
        out.append(d)

    # Retourne la liste des déclarations enrichies
    return out


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

