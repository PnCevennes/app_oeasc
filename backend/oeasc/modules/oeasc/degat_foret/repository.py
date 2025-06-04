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
    CorAreasDeclarationSchema,
    CorNomenclatureDeclarationEssenceSecondaireSchema,
    CorNomenclatureDeclarationEssenceComplementaireSchema,
    CorNomenclatureDeclarationMaturiteSchema,
    CorNomenclatureDeclarationOrigineSchema,
    CorNomenclatureDeclarationProtectionTypeSchema,
    CorNomenclatureDeclarationPaturageTypeSchema,
    CorNomenclatureDeclarationPaturageSaisonSchema,
    CorNomenclatureDeclarationEspeceSchema,
    TDegatEssenceSchema,
    TDegatSchema,
    TDeclarationSchema,
    CorAreasForetSchema,
    CorDgdCadastreSchema,
    TProprietaireSchema,
    TForetSchema,
    )


import json

config = current_app.config
DB = config["DB"]


def create_or_modify(model, key, dict_in, schema_cls=None):
    """
    Fonction générique de création ou modification utilisant Marshmallow.
    :param model: Le modèle SQLAlchemy à mettre à jour ou insérer.
    :param key: La clé primaire du modèle.
    :param dict_in: Les données à insérer ou mettre à jour.
    :param schema_cls: La classe du schéma Marshmallow à utiliser.
    :return: L'instance mise à jour ou insérée.
    """
    elem = None

    if key:
        val = dict_in.get(key, None)
        if val:
            stmt_elem = (
                select(model).where(getattr(model, key) == val)
                .limit(1)
            )
            elem = DB.session.execute(stmt_elem).scalars().first()

    if schema_cls is None:
        # On tente de deviner le schéma si non fourni
        schema_name = model.__name__ + "Schema"
        schema_cls = globals().get(schema_name)
        if schema_cls is None:
            raise ValueError(f"Schéma Marshmallow non trouvé pour {model.__name__}")

    schema = schema_cls()

    if elem is not None:
        # Mise à jour de l'existant
        elem = schema.load(dict_in, instance=elem, session=DB.session, partial=True)
    else:
        # Création d'une nouvelle instance
        elem = schema.load(dict_in, session=DB.session, partial=True)
        DB.session.add(elem)

    DB.session.commit()
    return elem



def update_or_insert(model, id_key, id_value, schema, data, session=None):
    """
    Met à jour ou insère une instance d'un modèle SQLAlchemy via marshmallow.
    :param model: Le modèle SQLAlchemy à mettre à jour ou insérer.
    :param id_key: La clé primaire du modèle.
    :param id_value: La valeur de la clé primaire.
    :param schema: Le schéma Marshmallow à utiliser pour la validation.
    :param data: Les données à valider et à insérer ou mettre à jour.
    :param session: La session SQLAlchemy à utiliser (facultatif).
    :return: L'instance mise à jour ou insérée.
    """
    instance = None

    if not session:
        session = DB.session

    # id_value n'est pas None, on vérifie si l'instance existe
    if id_value: 
        instance = session.get(model, id_value)

    if instance: # une instance avec l'id = id_value existe
        # Met à jour l'existant
        instance = schema.load(data, instance=instance, session=session, partial=True)
    else:
        # l'instance n'existe pas, on le crée
        # on retire l'id_proprietaire de data pour éviter les conflits
        data.pop(id_key, None)
        # chargement de l'instance dans le shema marshmallow
        instance = schema.load(data, session=session)
        session.add(instance)

    # Enregistrement en base
    session.commit()

    return instance


def get_declaration(id_declaration):
    """
    """

    try:
        stmt_declaration = (
            select(TDeclaration)
            .where(TDeclaration.id_declaration == id_declaration)
            .limit(1)
        )
        declaration = DB.session.execute(stmt_declaration).scalars().first()

        stmt_foret = (
            select(TForet)
            .where(TForet.id_foret == declaration.id_foret)
            .limit(1)
        )
        foret = DB.session.execute(stmt_foret).scalars().first()

        stmt_proprietaire = (
            select(TProprietaire)
            .where(TProprietaire.id_proprietaire == foret.id_proprietaire)
            .limit(1)
        )
        proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()


    except Exception:
        return (TDeclaration(), TForet(), TProprietaire())

    return (declaration, foret, proprietaire)


def create_or_update_declaration(post_data):
    """
    create_or_update_declaration
    """


    # post_data_origine = json.dumps(post_data, indent=4)
    # print("post_data_origine", post_data_origine)
    arranged_post_data = {}
    # 
    
    # post_data contient des données non conformes au schema, on traite tout pour que le json puisse être chargé dans marshmallow
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
    
    # Les relationships
    # Si des nomenclatures existent, on ajoute l'id de la déclaration avec la nomenclature 
    for key in post_data:
        if "nomenclatures_" in key:
            arranged_post_data[key] = [
                {
                    # "id_declaration": post_data.get("id_declaration"),
                    "id_nomenclature": id_nomenclature,
                }
                for id_nomenclature in post_data[key]
            ]


    # regroupement des areas de localisation.
    post_data["areas_localisation"] = (
        []
        + post_data["areas_localisation_cadastre"]
        + post_data["areas_localisation_onf_prf"]
        + post_data["areas_localisation_onf_ug"]
    )

    arranged_post_data["areas_localisation"] = [
        {"id_area": id_area, 
        # "id_declaration": post_data.get("id_declaration")
        }
        for id_area in post_data["areas_localisation"]
    ]


    # Si la parcelle n'a pas de document de gestion durable, c'est certainement un petit propriétaire
    # Meme si le cas est rare, on créé la possibilité de créer une nouvelle foret et un nouveau propriétaire
    if not post_data["b_document"]:
        id_declarant = post_data["id_declarant"]

        nomenclature = post_data[
            "id_nomenclature_proprietaire_declarant"
        ] and get_nomenclature_from_id(
            post_data["id_nomenclature_proprietaire_declarant"]
        )

        if nomenclature and nomenclature["cd_nomenclature"] != "P_D_O_NP":
            post_data["id_declarant"] = None
        # proprietaire
        proprietaireSchema = TProprietaireSchema()
        data_proprio = {}
        # proprietaire = create_or_modify(TProprietaire, "id_proprietaire", post_data)
        # data_proprio["id_proprietaire"] = post_data.get("nom_proprietaire")
        data_proprio["id_declarant"] = id_declarant

        data_proprio["nom_proprietaire"] = post_data.get("nom_proprietaire")
        data_proprio["telephone"] = post_data.get("telephone")
        data_proprio["email"] = post_data.get("email")
        data_proprio["adresse"] = post_data.get("adresse")
        data_proprio["s_code_postal"] = post_data.get("s_code_postal")
        data_proprio["s_commune_proprietaire"] = post_data.get("s_commune_proprietaire")
        data_proprio["id_nomenclature_proprietaire_type"] = post_data.get("id_nomenclature_proprietaire_type")

        # Si c'est la modification d'une déclaration, on la charge depuis la bdd pour comparer les champs et éventuellement supprimer
            # les champs qui ont été déselectionnés
        if post_data.get("id_proprietaire"): 
            data_proprio["id_declaration"] = post_data.get("id_declaration")
            proprietaire_bdd = DB.session.get(TProprietaire, post_data.get("id_declaration"))
        
            proprietaire = proprietaireSchema.load(
                data_proprio,
                instance=proprietaire_bdd,
                partial=True, # Important pour ne mettre à jour que les champs fournis
                session=DB.session
            )
            # declaration.degats = arranged_post_data.get("degats", [])
        else: 
            # Si c'est une création de déclaration. Juste on la load
            proprietaire = proprietaireSchema.load(
                data_proprio, session=DB.session, partial=True
            )
            DB.session.add(declaration)
        DB.session.commit()

        # post_data["id_proprietaire"] = proprietaire.id_proprietaire


        # creation d'une nouvelle foret si la zone est sans document de gestion
        data_foret = {}

        data_foret["id_proprietaire"] = proprietaire.id_proprietaire
        data_foret["b_statut_public"] = post_data.get("b_statut_public")
        data_foret["b_document"] = post_data.get("b_document")
        data_foret["nom_foret"] = post_data.get("nom_foret")
        data_foret["code_foret"] = post_data.get("code_foret")
        data_foret["label_foret"] = post_data.get("label_foret")
        data_foret["surface_calculee"] = post_data.get("surface_calculee")
        data_foret["surface_renseignee"] = post_data.get("surface_renseignee")
        

        # Regroupement des areas de foret
        post_data["areas_foret"] = (
            [] + post_data["areas_foret_communes"] + post_data["areas_foret_sections"]
        )
        if post_data["areas_foret_onf"]:
            post_data["areas_foret"].append(post_data["areas_foret_onf"])
        if post_data["areas_foret_dgd"]:
            post_data["areas_foret"].append(post_data["areas_foret_dgd"])
        
        data_foret["areas_foret"] = [
            {"id_area": id_area, 
            "id_declaration": post_data.get("id_declaration")
            }
            for id_area in post_data["areas_foret"]
        ]

        data_foret["id_foret"] = post_data.get("id_foret")
        foretSchema = TForetSchema()
        new_foret = foretSchema.load(
            data_foret, session=DB.session, partial=True
        )
        # foret
        # foret = create_or_modify(TForet, "id_foret", post_data)
        arranged_post_data["id_foret"] = new_foret.id_foret 

    else: 
        # Si la parcelle à un document de gestion durable, c'est le cas le plus courant, les forets sont déja en base et n'ont pas besoin d'être modifié
        
        # trouve le code_area qui correspond à la parcelle dans ref_geo
        id_area_foret = post_data["areas_foret_onf"] or post_data["areas_foret_dgd"]
        code_foret = get_area_from_id(id_area_foret)["area_code"]

        stmt_foret = (select(TForet)
        .where(TForet.code_foret == code_foret)
        .limit(1)              
        )
        foret = DB.session.execute(stmt_foret).scalars().first()

        arranged_post_data["id_foret"] = foret.id_foret


    declarationSchema = TDeclarationSchema()

    # Si c'est la modification d'une déclaration, on la charge depuis la bdd pour comparer les champs et éventuellement supprimer
    # les champs qui ont été déselectionnés
    if post_data.get("id_declaration"): 
        arranged_post_data["id_declaration"] = post_data.get("id_declaration")
        declaration_bdd = DB.session.get(TDeclaration, post_data.get("id_declaration"))
    
        declaration = declarationSchema.load(
            arranged_post_data,
            instance=declaration_bdd,
            partial=True, # Important pour ne mettre à jour que les champs fournis
            session=DB.session
        )
        # declaration.degats = arranged_post_data.get("degats", [])
    else: 
        # Si c'est une création de déclaration. Juste on la load
        declaration = declarationSchema.load(
            arranged_post_data, session=DB.session, partial=True
        )
        DB.session.add(declaration)

    DB.session.commit()

    print("id_declaration", declaration.id_declaration)    
    
    patch_areas_declarations(declaration.id_declaration)


    return arranged_post_data


def create_or_update_declaration_ancien(post_data):
    """
    create_or_update_declaration
    """

    # Si des nomenclatures existent, on les remplace par leur id

    for key in post_data:
        if "nomenclatures_" in key:
            post_data[key] = [
                {
                    "id_declaration": post_data.get("id_declaration"),
                    "id_nomenclature": id_nomenclature,
                }
                for id_nomenclature in post_data[key]
            ]

    # 
    post_data["areas_foret"] = (
        [] + post_data["areas_foret_communes"] + post_data["areas_foret_sections"]
    )
    if post_data["areas_foret_onf"]:
        post_data["areas_foret"].append(post_data["areas_foret_onf"])
    if post_data["areas_foret_dgd"]:
        post_data["areas_foret"].append(post_data["areas_foret_dgd"])


    # regroupement des areas de localisation.
    post_data["areas_localisation"] = (
        []
        + post_data["areas_localisation_cadastre"]
        + post_data["areas_localisation_onf_prf"]
        + post_data["areas_localisation_onf_ug"]
    )

    for key in ["areas_localisation", "areas_foret"]:
        post_data[key] = [
            {"id_area": id_area, "id_declaration": post_data.get("id_declaration")}
            for id_area in post_data[key]
        ]
    # Si la parcelle n'a pas de document de gestion durable
    if not post_data["b_document"]:
        id_declarant = post_data["id_declarant"]

        nomenclature = post_data[
            "id_nomenclature_proprietaire_declarant"
        ] and get_nomenclature_from_id(
            post_data["id_nomenclature_proprietaire_declarant"]
        )

        if nomenclature and nomenclature["cd_nomenclature"] != "P_D_O_NP":
            post_data["id_declarant"] = None
        # proprietaire
        proprietaire = create_or_modify(TProprietaire, "id_proprietaire", post_data)

        post_data["id_proprietaire"] = proprietaire.id_proprietaire

        post_data["id_declarant"] = id_declarant

        # foret
        foret = create_or_modify(TForet, "id_foret", post_data)
        post_data["id_foret"] = foret.id_foret 

    else: 
        # Si la parcelle à un document de gestion durable
        # get id_foret form id_areas
        id_area_foret = post_data["areas_foret_onf"] or post_data["areas_foret_dgd"]

        code_foret = get_area_from_id(id_area_foret)["area_code"]

        stmt_foret = (select(TForet)
        .where(TForet.code_foret == code_foret)
        .limit(1)              
        )
        foret = DB.session.execute(stmt_foret).scalars().first()


        post_data["id_foret"] = foret.id_foret

    # declaration

    foret_dict = TForetSchema().dump(foret) if foret else {}
    post_data["foret"] = foret_dict


    declaration = create_or_modify(TDeclaration, "id_declaration", post_data)

    patch_areas_declarations(declaration.id_declaration)

    declaration_dict = TDeclarationSchema().dump(declaration)

    # returned_declaration = declaration.as_dict(fields=[
    #     "areas_localisation",
    #     "nomenclatures_peuplement_essence_secondaire",
    #     "nomenclatures_peuplement_essence_complementaire",
    #     "nomenclatures_peuplement_maturite",
    #     "nomenclatures_peuplement_protection_type",
    #     "nomenclatures_peuplement_paturage_type",
    #     "nomenclatures_peuplement_paturage_saison",
    #     "nomenclatures_peuplement_espece",
    #     "nomenclatures_peuplement_origine2",
    #     "degats",
    #     "degats.degat_essences"

    # ])

    return declaration_dict

def get_id_areas(areas, type_list):
    """
    get_id_areas
    """

    return [x["id_area"] for x in filter(lambda x: x["type_code"] in type_list, areas)]


def get_id_area(areas, type_list):
    """
    get_id_area
    """

    id_areas = get_id_areas(areas, type_list)
    return id_areas[0] if id_areas else None


def get_foret_from_code(code_foret):
    """
    get_foret_from_code
    """

    code_foret = code_foret.upper()

    stmt_foret = (
        select(TForet)
        .where(TForet.code_foret == code_foret)
        .limit(1)
    )
    foret = DB.session.execute(stmt_foret).scalars().first()

    stmt_proprietaire = (
        select(TProprietaire)
        .where(TProprietaire.id_proprietaire == foret.id_proprietaire)
        .limit(1)
    )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return (foret, proprietaire)


def get_proprietaire_from_id_declarant(id_declarant):

    stmt_proprietaire = (
        select(TProprietaire)
        .where(TProprietaire.id_declarant == id_declarant)
        .limit(1)
    )
    proprietaire = DB.session.execute(stmt_proprietaire).scalars().first()

    return proprietaire or TProprietaire()


def get_declarations():
    """ne semble pas être utilisé"""
    stmt_declaration = (
        select(TDeclaration, TForet, VUsers)
        .join(TForet, TForet.id_foret == TDeclaration.id_foret)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)
    )
    declarations = DB.session.execute(stmt_declaration).all()
    declarations_schema = TDeclarationSchema(many=True)

    out = []

    # fields_declaration_foret_users = [
    #     "t_declarations.areas_localisation",
    #     "t_declarations.nomenclatures_peuplement_essence_secondaire",
    #     "t_declarations.nomenclatures_peuplement_essence_complementaire",
    #     "t_declarations.nomenclatures_peuplement_maturite",
    #     "t_declarations.nomenclatures_peuplement_protection_type",
    #     "t_declarations.nomenclatures_peuplement_paturage_type",
    #     "t_declarations.nomenclatures_peuplement_paturage_saison",
    #     "t_declarations.nomenclatures_peuplement_espece",
    #     "t_declarations.nomenclatures_peuplement_origine2",
    #     "t_declarations.degats",
    #     "t_forets.areas_foret",
    #     ]

    for declaration in declarations:
        d = declaration[0]
        d = declarations_schema.dump(d, many=False)
        f = declaration[1]
        f = declarations_schema.dump(f, many=False)
        u = declaration[2]
        u = declarations_schema.dump(u, many=False)

        # d = declaration[0].as_dict(fields=fields_declaration_foret_users)
        # f = declaration[1].as_dict(fields=fields_declaration_foret_users)
        # u = declaration[2].as_dict(fields=fields_declaration_foret_users)
        d.update(f)
        d.update(u)
        out.append(d)

    return out


def hide_proprietaire(proprietaire):
    for key in [
        "nom_proprietaire",
        "adresse",
        "s_code_postal",
        "s_commune_proprietaire",
    ]:
        proprietaire[key] = "***"

    proprietaire["telephone"] = "09 99 99 99 99"
    proprietaire["email"] = "prive@prive.prive"
