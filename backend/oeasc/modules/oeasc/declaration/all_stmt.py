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
    TDegatEssence,
)

from oeasc.modules.oeasc.user.models import VUsers

# Import des modèles forets (à adapter selon votre projet)
from oeasc.modules.oeasc.declaration.models import TForet, TProprietaire

from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes


from flask import current_app
config = current_app.config

# Fonctions PostgreSQL custom (appelées via func)
def get_nomenclature_label(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_label(arg), "")


def get_nomenclature_mnemonique(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemonique(arg), "")


def get_nomenclature_code(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_code(arg), "")


def get_nomenclature_labels(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_labels(arg), "")


def get_nomenclature_mnemoniques(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemoniques(arg), "")


def get_nomenclature_codes(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_codes(arg), "")

def get_area_names(id_declaration, area_type):
    return func.coalesce(func.oeasc_declarations.get_area_names(id_declaration, area_type), "")

def get_id_areas(id_declaration, area_type):
    return func.coalesce(func.oeasc_declarations.get_area_ids(id_declaration, area_type), "")
# get_id_areas = func.oeasc_declarations.get_id_areas



###############################################################################$
################             NOUVEAUX STMT SIMPLIFIES           ################
###############################################################################$


def get_stmt_for_resultats_degats():
    """ Récupère les dégats pour l'affichage des résultats (page: résultats de suivis/système d'alerte)"""

    stmt_all_degats = (
    select(
        TDeclaration.b_peuplement_paturage_presence,
        TDeclaration.b_peuplement_protection_existence,
        TDeclaration.centroid,
        get_area_names(TDeclaration.id_declaration, "OEASC_COMMUNE").label("communes"),
        VUsers.nom_complet.label("declarant"),
        func.to_char(TDeclaration.meta_create_date, "DD/MM/YYYY").label("declaration_date"),
        get_nomenclature_label(
            TDegatEssence.id_nomenclature_degat_anteriorite
        ).label("degat_anteriorite_label"),
        get_nomenclature_label(
            TDegatEssence.id_nomenclature_degat_essence
        ).label("degat_essence_label"),
        get_nomenclature_label(
            TDegatEssence.id_nomenclature_degat_etendue
        ).label("degat_etendue_label"),
        get_nomenclature_label(
            TDegatEssence.id_nomenclature_degat_gravite
        ).label("degat_gravite_label"),
        get_nomenclature_label(TDegat.id_nomenclature_degat_type).label(
                "degat_type_label"
        ),
        TDeclaration.id_declaration,
        VUsers.organisme.label("organisme"),
        get_nomenclature_label(TDeclaration.id_nomenclature_peuplement_acces).label(
                "peuplement_acces_label"
        ),
        get_nomenclature_label(
                TDeclaration.id_nomenclature_peuplement_essence_principale
        ).label("peuplement_ess_1_label"),
        get_nomenclature_label(TDeclaration.id_nomenclature_peuplement_type).label(
                "peuplement_type_label"
        ),  
        get_area_names(TDeclaration.id_declaration, "OEASC_SECTEUR").label("secteur"),

        case(
            (
                and_(TForet.b_statut_public == True, TForet.b_document == True),
                "Public (avec DGD)",
            ),
            (
                and_(TForet.b_statut_public == True, TForet.b_document == False),
                "Public (sans DGD)",
            ),
            (
                and_(TForet.b_statut_public == False, TForet.b_document == True),
                "Privé (avec DGD)",
            ),
            (
                and_(TForet.b_statut_public == False, TForet.b_document == False),
                "Privé (sans DGD)",
            ),
            else_="",
        ).label("type_foret"),
        case(
            (TDeclaration.b_valid == True, "Validé"),
            (TDeclaration.b_valid == False, "Non validé"),
            else_="En attente",
        ).label("valide"),

        # TDegat.id_degat,
        # TDegatEssence.id_degat_essence,
        
    )
    .outerjoin(TDegatEssence, TDegat.id_degat == TDegatEssence.id_degat)
    .join(TDeclaration, TDegat.id_declaration == TDeclaration.id_declaration)
    .join(VUsers, TDeclaration.id_declarant == VUsers.id_role)
    .join(TForet, TDeclaration.id_foret == TForet.id_foret)
    .order_by(TDegat.id_declaration)
    )  

    return stmt_all_degats


def get_stmt_for_declarations_export(type_file="csv", type_out="degat"):
    """ Récupère les informations sur les déclarations, les dégats et les forêts pour l'export des données (csv ou shape)
    type_file: "csv" ou "shape"
    type_out: "degat" ou "declaration"
    Si type_out == "degat", alors on récupère une ligne par dégât, avec les infos de la déclaration et du dégât.
    Si type_out == "declaration", alors on récupère une ligne par déclaration, avec les infos de la déclaration et une liste des types de dégats associés à la déclaration (sans les détails des dégats).
    Si type_file == "shape", alors on récupère la géométrie de la déclaration (champ geom de la table t_declaration).

    """

    stmt= (
        select(
            TDeclaration.id_declaration.label("id"),
            case(
                (TDeclaration.b_valid == True, "Validé"),
                (TDeclaration.b_valid == False, "Non validé"),
                else_="En attente",
            ).label("Valide"),
            func.to_char(TDeclaration.meta_create_date, "DD/MM/YYYY").label("Date"),
            VUsers.nom_complet.label("Déclarant"),
            VUsers.organisme.label("Organisme"),

            # TDeclaration.b_peuplement_paturage_presence,
            # TDeclaration.b_peuplement_protection_existence,
            case((TForet.b_statut_public == True, "Public"), else_="Privé").label(
                    "Statut forêt"
                ),
            case((TForet.b_document == True, "Oui"), else_="Non").label("Documentée"),
            TForet.label_foret.label("Nom forêt"),
            get_area_names(TDeclaration.id_declaration, "OEASC_SECTEUR").label("Secteur"),
            get_nomenclature_mnemonique(TDeclaration.id_nomenclature_peuplement_type).label(
                    "Peu. type"
            ),
            TDeclaration.precision_localisation.label("Précision localisation"),
            TDeclaration.commentaire.label("Commentaire"),
            get_nomenclature_mnemonique(TDeclaration.id_nomenclature_peuplement_origine).label(
                    "Origine peuplement"
            ),  

            ( # liste des origines des plants touchés
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationOrigine)
                .where(CorNomenclatureDeclarationOrigine.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationOrigine.id_nomenclature)
                .group_by(CorNomenclatureDeclarationOrigine.id_declaration)
                .correlate(TDeclaration)
            ).label("Origine plants touchés"),

            ( # liste des maturités
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationMaturite)
                .where(CorNomenclatureDeclarationMaturite.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationMaturite.id_nomenclature)
                .group_by(CorNomenclatureDeclarationMaturite.id_declaration)
                .correlate(TDeclaration)
            ).label("Peu. mat."),

            get_nomenclature_mnemonique(TDeclaration.id_nomenclature_peuplement_essence_principale).label(
                    "Ess. 1"
            ), 
            ( # liste des essences secondaires
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationEssenceSecondaire)
                .where(CorNomenclatureDeclarationEssenceSecondaire.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationEssenceSecondaire.id_nomenclature)
                .group_by(CorNomenclatureDeclarationEssenceSecondaire.id_declaration)
                .correlate(TDeclaration)
            ).label("Ess. 2"),
            ( # liste des essences complémentaires
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationEssenceComplementaire)
                .where(CorNomenclatureDeclarationEssenceComplementaire.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationEssenceComplementaire.id_nomenclature)
                .group_by(CorNomenclatureDeclarationEssenceComplementaire.id_declaration)
                .correlate(TDeclaration)
            ).label("Ess. 3"),


            get_nomenclature_mnemonique(TDeclaration.id_nomenclature_peuplement_paturage_statut).label(
                    "Pât. stat."
            ), 
            get_nomenclature_mnemonique(TDeclaration.id_nomenclature_peuplement_paturage_frequence).label(
                    "Pât. freq."
            ), 

            ( # liste des types de pâturage
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationPaturageType)
                .where(CorNomenclatureDeclarationPaturageType.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationPaturageType.id_nomenclature)
                .group_by(CorNomenclatureDeclarationPaturageType.id_declaration)
                .correlate(TDeclaration)
            ).label("Pât. type"),

            ( # liste des types de protection
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationProtectionType)
                .where(CorNomenclatureDeclarationProtectionType.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationProtectionType.id_nomenclature)
                .group_by(CorNomenclatureDeclarationProtectionType.id_declaration)
                .correlate(TDeclaration)
            ).label("Pro. type"),

            ( # liste des saisons de pâturage
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(CorNomenclatureDeclarationPaturageSaison)
                .where(CorNomenclatureDeclarationPaturageSaison.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == CorNomenclatureDeclarationPaturageSaison.id_nomenclature)
                .group_by(CorNomenclatureDeclarationPaturageSaison.id_declaration)
                .correlate(TDeclaration)
            ).label("Pât. sais."),

        )
    )

    if type_out == "degat":
        stmt = stmt.add_columns(   
            get_nomenclature_mnemonique(TDegat.id_nomenclature_degat_type).label(
                    "Dég. type"
            ), 

            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_essence).label(
                    "Dég. ess."
            ), 

            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_gravite).label(
                    "Dég. grâ."
            ), 
            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_etendue).label(
                    "Dég. éten."
            ), 
            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_anteriorite).label(
                    "Dég. ant."
            ), 
        )
    elif type_out == "declaration":
        # Ajout d'une colonne degat Type avec la liste de tous les types de dégats en chaine de caractères 
        stmt = stmt.add_columns(
            (
                select(
                    func.string_agg(cast(TNomenclatures.mnemonique, String), ", ")
                )
                .select_from(TDegat)
                .where(TDegat.id_declaration == TDeclaration.id_declaration)
                .where(TNomenclatures.id_nomenclature == TDegat.id_nomenclature_degat_type)
                .group_by(TDegat.id_declaration)
                .correlate(TDeclaration)
            ).label("Deg. type"),
        )


    if type_file == "shape":
        stmt = stmt.add_columns(
            TDeclaration.geom.label("geom")
        )
    elif type_file == "csv":
        stmt = stmt.add_columns(
            case(
                (
                    and_(TForet.b_statut_public == True, TForet.b_document == True),
                    get_area_names(TDeclaration.id_declaration, "OEASC_ONF_UG"),
                ),
                else_=get_area_names(TDeclaration.id_declaration, "OEASC_CADASTRE"),
            ).label("Parcelle(s)"),
            # case(
            #     (
            #         and_(TForet.b_statut_public == True, TForet.b_document == True),
            #         get_area_names(TDeclaration.id_declaration, "OEASC_ONF_FRT"),
            #     ),
            #     (
            #         and_(TForet.b_statut_public == False, TForet.b_document == True),
            #         get_area_names(TDeclaration.id_declaration, "OEASC_DGD"),
            #     ),
            #     else_=get_area_names(TDeclaration.id_declaration, "OEASC_SECTION"),
            # ).label("Nom section(s)"),
        )

    if type_out == "declaration":
        stmt = (stmt
            .select_from(TDeclaration)
            .join(VUsers, TDeclaration.id_declarant == VUsers.id_role)
            .join(TForet, TDeclaration.id_foret == TForet.id_foret)
            .order_by(TDeclaration.meta_create_date.desc())
        )
    elif type_out == "degat":
        stmt = (stmt
            .outerjoin(TDegatEssence, TDegat.id_degat == TDegatEssence.id_degat)
            .join(TDeclaration, TDegat.id_declaration == TDeclaration.id_declaration)
            .join(VUsers, TDeclaration.id_declarant == VUsers.id_role)
            .join(TForet, TDeclaration.id_foret == TForet.id_foret)
            .order_by(TDeclaration.meta_create_date.desc())
        )

    return stmt



##################################################################################
################# ANCIENS STMT: retransciptions des vues sql #####################
##################################################################################

# creation d'une requête pour la liste des déclarations.
def get_stmt_liste_declaration():
    """
    Crée une requête SQLAlchemy pour récupérer la liste des déclarations avec les informations nécessaires
    pour l'affichage de la liste.

    """

    # -------------------------
    # CTE : foret
    # Nécessaire : id_foret, label_foret, b_statut_public, b_document
    # -------------------------
    foret_cte = select(
        TForet.id_foret,
        TForet.label_foret,
        TForet.b_document,
        TForet.b_statut_public,
    ).cte("foret")

    # -------------------------
    # CTE : peuplement
    # Nécessaire : id_declaration, peuplement_type_mnemo, peuplement_ess_1_mnemo
    # -------------------------
    d1 = aliased(TDeclaration, name="d1")

    peuplement_cte = (
        select(
            d1.id_declaration,
            get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_type).label(
                "peuplement_type_mnemo"
            ),
            get_nomenclature_mnemonique(
                d1.id_nomenclature_peuplement_essence_principale
            ).label("peuplement_ess_1_mnemo"),
        )
        .select_from(d1)
        .cte("peuplement")
    )

    # -------------------------
    # CTE : peuplement_nomenclatures
    # Nécessaire : id_declaration, peuplement_origine2_mnemo
    # -------------------------
    d2 = aliased(TDeclaration, name="d2")
    c_origine = aliased(CorNomenclatureDeclarationOrigine, name="c_origine")

    peuplement_nomenclatures_cte = (
        select(
            d2.id_declaration,
            get_nomenclature_mnemoniques(
                func.array_agg(c_origine.id_nomenclature.distinct())
            ).label("peuplement_origine2_mnemo"),
        )
        .select_from(d2)
        .outerjoin(c_origine, d2.id_declaration == c_origine.id_declaration)
        .group_by(d2.id_declaration)
        .cte("peuplement_nomenclatures")
    )

    # -------------------------
    # CTE : degat_type
    # Nécessaire : id_declaration, degat_type_mnemos
    # -------------------------
    deg_1 = aliased(TDegat, name="deg_1")

    degat_type_cte = (
        select(
            deg_1.id_declaration,
            get_nomenclature_mnemoniques(
                func.array_agg(deg_1.id_nomenclature_degat_type.distinct())
            ).label("degat_type_mnemos"),
        )
        .select_from(deg_1)
        .group_by(deg_1.id_declaration)
        .cte("degat_type")
    )

    # -------------------------
    # Requête principale
    # -------------------------
    # d = TDeclaration
    f = foret_cte
    p = peuplement_cte
    pn = peuplement_nomenclatures_cte
    deg = degat_type_cte
    # vu = VUsers

    query = (
        select(
            TDeclaration.id_declaration,
            # func.to_char(TDeclaration.meta_create_date, "DD/MM/YYYY").label("declaration_date"),
            func.to_char(TDeclaration.meta_create_date, "YYYY/MM/DD").label(
                "declaration_date"
            ),
            VUsers.id_role.label("id_declarant"),
            VUsers.nom_complet.label("declarant"),
            VUsers.organisme,
            VUsers.id_droit_max,
            VUsers.org_mnemo,
            f.c.label_foret,
            get_area_names(TDeclaration.id_declaration, "OEASC_SECTEUR").label(
                "secteur"
            ),
            case(
                (
                    and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_area_names(TDeclaration.id_declaration, "OEASC_ONF_UG"),
                ),
                else_=get_area_names(TDeclaration.id_declaration, "OEASC_CADASTRE"),
            ).label("parcelles"),
            p.c.peuplement_type_mnemo,
            pn.c.peuplement_origine2_mnemo,
            p.c.peuplement_ess_1_mnemo,
            deg.c.degat_type_mnemos,
            func.to_char(TDeclaration.date_fin, "YYYY/MM/DD").label("date_fin"),
            # TDeclaration.date_fin,
            TDeclaration.status,
            TDeclaration.token_renouvellement,
            TDeclaration.b_valid,
        )
        .select_from(TDeclaration)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)
        .join(f, f.c.id_foret == TDeclaration.id_foret)
        .join(p, p.c.id_declaration == TDeclaration.id_declaration)
        .join(pn, pn.c.id_declaration == TDeclaration.id_declaration)
        .join(deg, deg.c.id_declaration == TDeclaration.id_declaration)
    )

    return query

def get_v_declarations_query():
    """
    
    """


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
            case((TForet.b_statut_public == True, "Public"), else_="Privé").label(
                "statut_public"
            ),
            case((TForet.b_document == True, "Oui"), else_="Non").label("document"),
            case(
                (
                    and_(TForet.b_statut_public == True, TForet.b_document == True),
                    "Public (avec DGD)",
                ),
                (
                    and_(TForet.b_statut_public == True, TForet.b_document == False),
                    "Public (sans DGD)",
                ),
                (
                    and_(TForet.b_statut_public == False, TForet.b_document == True),
                    "Privé (avec DGD)",
                ),
                (
                    and_(TForet.b_statut_public == False, TForet.b_document == False),
                    "Privé (sans DGD)",
                ),
                else_="",
            ).label("type_foret"),
            get_nomenclature_label(
                TProprietaire.id_nomenclature_proprietaire_type
            ).label("foret_type_label"),
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
            get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_type).label(
                "peuplement_type_mnemo"
            ),
            get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_origine).label(
                "peuplement_origine_mnemo"
            ),
            get_nomenclature_mnemonique(
                d1.id_nomenclature_peuplement_essence_principale
            ).label("peuplement_ess_1_mnemo"),
            get_nomenclature_mnemonique(
                d1.id_nomenclature_peuplement_paturage_statut
            ).label("peuplement_paturage_statut_mnemo"),
            get_nomenclature_mnemonique(
                d1.id_nomenclature_peuplement_paturage_frequence
            ).label("peuplement_paturage_frequence_mnemo"),
            get_nomenclature_mnemonique(d1.id_nomenclature_peuplement_acces).label(
                "peuplement_acces_mnemo"
            ),
            get_nomenclature_label(d1.id_nomenclature_peuplement_type).label(
                "peuplement_type_label"
            ),
            get_nomenclature_label(d1.id_nomenclature_peuplement_origine).label(
                "peuplement_origine_label"
            ),
            get_nomenclature_label(
                d1.id_nomenclature_peuplement_essence_principale
            ).label("peuplement_ess_1_label"),
            get_nomenclature_label(d1.id_nomenclature_peuplement_paturage_statut).label(
                "peuplement_paturage_statut_label"
            ),
            get_nomenclature_label(
                d1.id_nomenclature_peuplement_paturage_frequence
            ).label("peuplement_paturage_frequence_label"),
            get_nomenclature_label(d1.id_nomenclature_peuplement_acces).label(
                "peuplement_acces_label"
            ),
            get_nomenclature_code(d1.id_nomenclature_peuplement_type).label(
                "peuplement_type_code"
            ),
            get_nomenclature_code(d1.id_nomenclature_peuplement_origine).label(
                "peuplement_origine_code"
            ),
            get_nomenclature_code(
                d1.id_nomenclature_peuplement_essence_principale
            ).label("peuplement_ess_1_code"),
            get_nomenclature_code(d1.id_nomenclature_peuplement_paturage_statut).label(
                "peuplement_paturage_statut_code"
            ),
            get_nomenclature_code(
                d1.id_nomenclature_peuplement_paturage_frequence
            ).label("peuplement_paturage_frequence_code"),
            get_nomenclature_code(d1.id_nomenclature_peuplement_acces).label(
                "peuplement_acces_code"
            ),
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
    c_paturage_type = aliased(
        CorNomenclatureDeclarationPaturageType, name="c_paturage_type"
    )
    c_paturage_saison = aliased(
        CorNomenclatureDeclarationPaturageSaison, name="c_paturage_saison"
    )
    c_protection_type = aliased(
        CorNomenclatureDeclarationProtectionType, name="c_protection_type"
    )
    c_espece = aliased(CorNomenclatureDeclarationEspece, name="c_espece")
    c_origine = aliased(CorNomenclatureDeclarationOrigine, name="c_origine")

    peuplement_nomenclatures_cte = (
        select(
            d2.id_declaration,
            # mnemo
            get_nomenclature_mnemoniques(
                func.array_agg(c_maturite.id_nomenclature.distinct())
            ).label("peuplement_maturite_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_origine.id_nomenclature.distinct())
            ).label("peuplement_origine2_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_ess_2.id_nomenclature.distinct())
            ).label("peuplement_ess_2_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_ess_3.id_nomenclature.distinct())
            ).label("peuplement_ess_3_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_paturage_type.id_nomenclature.distinct())
            ).label("peuplement_paturage_type_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_paturage_saison.id_nomenclature.distinct())
            ).label("peuplement_paturage_saison_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_protection_type.id_nomenclature.distinct())
            ).label("peuplement_protection_type_mnemo"),
            get_nomenclature_mnemoniques(
                func.array_agg(c_espece.id_nomenclature.distinct())
            ).label("espece_mnemo"),
            # label
            get_nomenclature_labels(
                func.array_agg(c_maturite.id_nomenclature.distinct())
            ).label("peuplement_maturite_label"),
            get_nomenclature_labels(
                func.array_agg(c_origine.id_nomenclature.distinct())
            ).label("peuplement_origine2_label"),
            get_nomenclature_labels(
                func.array_agg(c_ess_2.id_nomenclature.distinct())
            ).label("peuplement_ess_2_label"),
            get_nomenclature_labels(
                func.array_agg(c_ess_3.id_nomenclature.distinct())
            ).label("peuplement_ess_3_label"),
            get_nomenclature_labels(
                func.array_agg(c_paturage_type.id_nomenclature.distinct())
            ).label("peuplement_paturage_type_label"),
            get_nomenclature_labels(
                func.array_agg(c_paturage_saison.id_nomenclature.distinct())
            ).label("peuplement_paturage_saison_label"),
            get_nomenclature_labels(
                func.array_agg(c_protection_type.id_nomenclature.distinct())
            ).label("peuplement_protection_type_label"),
            get_nomenclature_labels(
                func.array_agg(c_espece.id_nomenclature.distinct())
            ).label("espece_label"),
            # code
            get_nomenclature_codes(
                func.array_agg(c_maturite.id_nomenclature.distinct())
            ).label("peuplement_maturite_code"),
            get_nomenclature_codes(
                func.array_agg(c_origine.id_nomenclature.distinct())
            ).label("peuplement_origine2_code"),
            get_nomenclature_codes(
                func.array_agg(c_ess_2.id_nomenclature.distinct())
            ).label("peuplement_ess_2_code"),
            get_nomenclature_codes(
                func.array_agg(c_ess_3.id_nomenclature.distinct())
            ).label("peuplement_ess_3_code"),
            get_nomenclature_codes(
                func.array_agg(c_paturage_type.id_nomenclature.distinct())
            ).label("peuplement_paturage_type_code"),
            get_nomenclature_codes(
                func.array_agg(c_paturage_saison.id_nomenclature.distinct())
            ).label("peuplement_paturage_saison_code"),
            get_nomenclature_codes(
                func.array_agg(c_protection_type.id_nomenclature.distinct())
            ).label("peuplement_protection_type_code"),
            get_nomenclature_codes(
                func.array_agg(c_espece.id_nomenclature.distinct())
            ).label("espece_code"),
        )
        .select_from(d2)
        .outerjoin(c_ess_2, d2.id_declaration == c_ess_2.id_declaration)
        .outerjoin(c_ess_3, d2.id_declaration == c_ess_3.id_declaration)
        .outerjoin(c_maturite, d2.id_declaration == c_maturite.id_declaration)
        .outerjoin(c_paturage_type, d2.id_declaration == c_paturage_type.id_declaration)
        .outerjoin(
            c_paturage_saison, d2.id_declaration == c_paturage_saison.id_declaration
        )
        .outerjoin(
            c_protection_type, d2.id_declaration == c_protection_type.id_declaration
        )
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
            get_nomenclature_mnemoniques(
                func.array_agg(deg_1.id_nomenclature_degat_type.distinct())
            ).label("degat_type_mnemos"),
            get_nomenclature_labels(
                func.array_agg(deg_1.id_nomenclature_degat_type.distinct())
            ).label("degat_type_labels"),
            get_nomenclature_codes(
                func.array_agg(deg_1.id_nomenclature_degat_type.distinct())
            ).label("degat_type_codes"),
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
                (
                    and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_ONF_UG"),
                ),
                else_=get_area_names(d.id_declaration, "OEASC_CADASTRE"),
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
                (
                    d.autre_protection != None,
                    func.replace(
                        cast(pn.c.peuplement_protection_type_label, Text),
                        "Autre (préciser)",
                        d.autre_protection,
                    ),
                ),
                else_=cast(pn.c.peuplement_protection_type_label, Text),
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
                (
                    and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_ONF_FRT"),
                ),
                (
                    and_(f.c.b_statut_public == False, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_DGD"),
                ),
                else_=get_id_areas(d.id_declaration, "OEASC_SECTION"),
            ).label("areas_foret"),
            # Areas foret (noms)
            case(
                (
                    and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_ONF_FRT"),
                ),
                (
                    and_(f.c.b_statut_public == False, f.c.b_document == True),
                    get_area_names(d.id_declaration, "OEASC_DGD"),
                ),
                else_=get_area_names(d.id_declaration, "OEASC_SECTION"),
            ).label("areas_foret_names"),
            # Validation
            case(
                (d.b_valid == True, "Validé"),
                (d.b_valid == False, "Non validé"),
                else_="En attente",
            ).label("valide"),
            d.b_valid,
            areas_localisation_raw_subq.label("areas_localisation_raw"),
            # Areas localisation
            case(
                (
                    and_(f.c.b_statut_public == True, f.c.b_document == True),
                    get_id_areas(d.id_declaration, "OEASC_ONF_UG"),
                ),
                else_=get_id_areas(d.id_declaration, "OEASC_CADASTRE"),
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


def get_v_degats_query():
    """
    Crée une requête SQLAlchemy pour récupérer les informations sur les dégâts associés à une déclaration, avec les libellés et codes des nomenclatures.


    """

    stmt = (
        select(
            TDegat.id_declaration.label("id_declaration_degat"),
            get_nomenclature_mnemonique(TDegat.id_nomenclature_degat_type).label(
                "degat_type_mnemo"
            ),
            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_essence).label(
                "degat_essence_mnemo"
            ),
            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_gravite).label(
                "degat_gravite_mnemo"
            ),
            get_nomenclature_mnemonique(TDegatEssence.id_nomenclature_degat_etendue).label(
                "degat_etendue_mnemo"
            ),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_mnemo"),
            get_nomenclature_label(TDegat.id_nomenclature_degat_type).label(
                "degat_type_label"
            ),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_essence
            ).label("degat_essence_label"),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_gravite
            ).label("degat_gravite_label"),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_etendue
            ).label("degat_etendue_label"),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_label"),
            get_nomenclature_code(TDegat.id_nomenclature_degat_type).label(
                "degat_type_code"
            ),
            get_nomenclature_code(
                TDegatEssence.id_nomenclature_degat_essence
            ).label("degat_essence_code"),
            get_nomenclature_code(
                TDegatEssence.id_nomenclature_degat_gravite
            ).label("degat_gravite_code"),
            get_nomenclature_code(
                TDegatEssence.id_nomenclature_degat_etendue
            ).label("degat_etendue_code"),
            get_nomenclature_code(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_code"),
        )
        .select_from(TDegat)
        .join(
            TDegatEssence,
            TDegatEssence.id_degat == TDegat.id_degat,
            isouter=True,
        )
        .order_by(TDegat.id_declaration)
    )

    return stmt


def get_v_export_vl_declaration_query():
    """

    """

    vd_query = get_v_declarations_query()
    v = vd_query.subquery("v")

    d = aliased(TDeclaration, name="d")

    stmt = select(
        v.c.id_declaration,
        v.c.declaration_date,
        v.c.meta_create_date,
        v.c.commentaire,
        v.c.b_peuplement_protection_existence,
        v.c.b_peuplement_paturage_presence,
        v.c.b_autorisation,
        v.c.id_declarant,
        v.c.declarant,
        v.c.organisme,
        v.c.organisme_group,
        v.c.id_droit_max,
        v.c.org_mnemo,
        v.c.id_foret,
        v.c.label_foret,
        v.c.statut_public,
        v.c.document,
        v.c.b_statut_public,
        v.c.b_document,
        v.c.type_foret,
        v.c.foret_type_label,
        v.c.communes,
        v.c.secteur,
        v.c.parcelles,
        v.c.peuplement_surface,
        v.c.peuplement_type_mnemo,
        v.c.peuplement_origine_mnemo,
        v.c.peuplement_origine2_mnemo,
        v.c.peuplement_maturite_mnemo,
        v.c.peuplement_ess_1_mnemo,
        v.c.peuplement_ess_2_mnemo,
        v.c.peuplement_ess_3_mnemo,
        v.c.peuplement_paturage_statut_mnemo,
        v.c.peuplement_paturage_frequence_mnemo,
        v.c.peuplement_paturage_type_mnemo,
        v.c.peuplement_paturage_saison_mnemo,
        v.c.peuplement_protection_type_mnemo,
        v.c.espece_mnemo,
        v.c.peuplement_acces_mnemo,
        v.c.degat_type_mnemos,
        v.c.peuplement_type_label,
        v.c.peuplement_origine_label,
        v.c.peuplement_origine2_label,
        v.c.peuplement_maturite_label,
        v.c.peuplement_ess_1_label,
        v.c.peuplement_ess_2_label,
        v.c.peuplement_ess_3_label,
        v.c.peuplement_paturage_statut_label,
        v.c.peuplement_paturage_frequence_label,
        v.c.peuplement_paturage_type_label,
        v.c.peuplement_paturage_saison_label,
        v.c.peuplement_protection_type_label,
        v.c.espece_label,
        v.c.peuplement_acces_label,
        v.c.degat_type_labels,
        v.c.peuplement_type_code,
        v.c.peuplement_origine_code,
        v.c.peuplement_origine2_code,
        v.c.peuplement_maturite_code,
        v.c.peuplement_ess_1_code,
        v.c.peuplement_ess_2_code,
        v.c.peuplement_ess_3_code,
        v.c.peuplement_paturage_statut_code,
        v.c.peuplement_paturage_frequence_code,
        v.c.peuplement_paturage_type_code,
        v.c.peuplement_paturage_saison_code,
        v.c.peuplement_protection_type_code,
        v.c.espece_code,
        v.c.peuplement_acces_code,
        v.c.degat_type_codes,
        v.c.precision_localisation,
        v.c.centroid,
        v.c.areas_foret,
        v.c.areas_foret_names,
        v.c.valide,
        v.c.b_valid,
        v.c.areas_localisation_raw,
        v.c.areas_localisation,
        d.geom,
        d.geom_4326,
    ).select_from(v.join(d, d.id_declaration == v.c.id_declaration))

    return stmt


def get_v_declaration_degat_query():
    """

    """

    vd_query = get_v_declarations_query()
    v = vd_query.subquery("vd")

    vdeg_query = get_v_degats_query()
    vdeg = vdeg_query.subquery("vdeg")

    stmt = select(
        v.c.id_declaration,
        v.c.declaration_date,
        v.c.meta_create_date,
        v.c.commentaire,
        v.c.b_peuplement_protection_existence,
        v.c.b_peuplement_paturage_presence,
        v.c.b_autorisation,
        v.c.id_declarant,
        v.c.declarant,
        v.c.organisme,
        v.c.organisme_group,
        v.c.id_droit_max,
        v.c.org_mnemo,
        v.c.id_foret,
        v.c.label_foret,
        v.c.statut_public,
        v.c.document,
        v.c.b_statut_public,
        v.c.b_document,
        v.c.type_foret,
        v.c.foret_type_label,
        v.c.communes,
        v.c.secteur,
        v.c.parcelles,
        v.c.peuplement_surface,
        v.c.peuplement_type_mnemo,
        v.c.peuplement_origine_mnemo,
        v.c.peuplement_origine2_mnemo,
        v.c.peuplement_maturite_mnemo,
        v.c.peuplement_ess_1_mnemo,
        v.c.peuplement_ess_2_mnemo,
        v.c.peuplement_ess_3_mnemo,
        v.c.peuplement_paturage_statut_mnemo,
        v.c.peuplement_paturage_frequence_mnemo,
        v.c.peuplement_paturage_type_mnemo,
        v.c.peuplement_paturage_saison_mnemo,
        v.c.peuplement_protection_type_mnemo,
        v.c.espece_mnemo,
        v.c.peuplement_acces_mnemo,
        v.c.degat_type_mnemos,
        v.c.peuplement_type_label,
        v.c.peuplement_origine_label,
        v.c.peuplement_origine2_label,
        v.c.peuplement_maturite_label,
        v.c.peuplement_ess_1_label,
        v.c.peuplement_ess_2_label,
        v.c.peuplement_ess_3_label,
        v.c.peuplement_paturage_statut_label,
        v.c.peuplement_paturage_frequence_label,
        v.c.peuplement_paturage_type_label,
        v.c.peuplement_paturage_saison_label,
        v.c.peuplement_protection_type_label,
        v.c.espece_label,
        v.c.peuplement_acces_label,
        v.c.degat_type_labels,
        v.c.peuplement_type_code,
        v.c.peuplement_origine_code,
        v.c.peuplement_origine2_code,
        v.c.peuplement_maturite_code,
        v.c.peuplement_ess_1_code,
        v.c.peuplement_ess_2_code,
        v.c.peuplement_ess_3_code,
        v.c.peuplement_paturage_statut_code,
        v.c.peuplement_paturage_frequence_code,
        v.c.peuplement_paturage_type_code,
        v.c.peuplement_paturage_saison_code,
        v.c.peuplement_protection_type_code,
        v.c.espece_code,
        v.c.peuplement_acces_code,
        v.c.degat_type_codes,
        v.c.precision_localisation,
        v.c.centroid,
        v.c.areas_foret,
        v.c.areas_foret_names,
        v.c.valide,
        v.c.b_valid,
        v.c.areas_localisation_raw,
        v.c.areas_localisation,
        vdeg.c.id_declaration_degat,
        vdeg.c.degat_type_mnemo,
        vdeg.c.degat_essence_mnemo,
        vdeg.c.degat_gravite_mnemo,
        vdeg.c.degat_etendue_mnemo,
        vdeg.c.degat_anteriorite_mnemo,
        vdeg.c.degat_type_label,
        vdeg.c.degat_essence_label,
        vdeg.c.degat_gravite_label,
        vdeg.c.degat_etendue_label,
        vdeg.c.degat_anteriorite_label,
        vdeg.c.degat_type_code,
        vdeg.c.degat_essence_code,
        vdeg.c.degat_gravite_code,
        vdeg.c.degat_etendue_code,
        vdeg.c.degat_anteriorite_code,
    ).select_from(v.join(vdeg, vdeg.c.id_declaration_degat == v.c.id_declaration))

    return stmt


def get_v_export_declaration_csv_query():
    """
   
    """

    # Récupère la requête v_declarations et l'utilise comme sous-requête
    vd_query = get_v_declarations_query()
    vd = vd_query.subquery("vd")

    stmt = select(
        vd.c.id_declaration.label("id"),
        vd.c.valide.label("Valide"),
        vd.c.declaration_date.label("Date"),
        vd.c.declarant.label("Déclarant"),
        vd.c.organisme.label("Organisme"),
        vd.c.label_foret.label("Nom forêt"),
        vd.c.statut_public.label("Statut forêt"),
        vd.c.document.label("Documentée"),
        vd.c.secteur.label("Secteur"),
        vd.c.parcelles.label("Parcelle(s)"),
        vd.c.peuplement_type_mnemo.label("Peu. type"),
        vd.c.peuplement_origine_mnemo.label("Origine peuplement"),
        vd.c.peuplement_origine2_mnemo.label("Origine plants touchés"),
        vd.c.peuplement_maturite_mnemo.label("Peu. mat."),
        vd.c.peuplement_ess_1_mnemo.label("Ess. 1"),
        vd.c.peuplement_ess_2_mnemo.label("Ess. 2"),
        vd.c.peuplement_ess_3_mnemo.label("Ess. 3"),
        vd.c.precision_localisation.label("Précision localisation"),
        vd.c.commentaire.label("Commentaires"),
        func.split_part(cast(vd.c.peuplement_ess_2_mnemo, Text), ", ", 1).label(
            "ESS II.1"
        ),
        func.split_part(cast(vd.c.peuplement_ess_2_mnemo, Text), ", ", 2).label(
            "ESS II.2"
        ),
        func.split_part(cast(vd.c.peuplement_ess_2_mnemo, Text), ", ", 3).label(
            "ESS II.3"
        ),
        func.split_part(cast(vd.c.peuplement_ess_3_mnemo, Text), ", ", 1).label(
            "ESS III.1"
        ),
        func.split_part(cast(vd.c.peuplement_ess_3_mnemo, Text), ", ", 2).label(
            "ESS III.2"
        ),
        func.split_part(cast(vd.c.peuplement_ess_3_mnemo, Text), ", ", 3).label(
            "ESS III.3"
        ),
        vd.c.peuplement_paturage_statut_mnemo.label("Pât. stat."),
        vd.c.peuplement_paturage_frequence_mnemo.label("Pât. freq."),
        vd.c.peuplement_paturage_type_mnemo.label("Pât. type"),
        vd.c.peuplement_paturage_saison_mnemo.label("Pât. sais."),
        vd.c.peuplement_protection_type_mnemo.label("Pro. type"),
        vd.c.degat_type_mnemos.label("Dég. types"),
    ).select_from(vd)

    return stmt


def get_v_export_declaration_degats_csv_query():
    """
    """

    ved_query = get_v_export_declaration_csv_query()
    ved = ved_query.subquery("ved")

    vdeg_query = get_v_degats_query()
    vdeg = vdeg_query.subquery("vdeg")

    stmt = select(
        ved.c.id.label("id"),
        ved.c.Valide.label("Valide"),
        ved.c.Date.label("Date"),
        ved.c.Déclarant.label("Déclarant"),
        ved.c.Organisme.label("Organisme"),
        ved.c['Nom forêt'].label("Nom forêt"),
        ved.c['Statut forêt'].label("Statut forêt"),
        ved.c['Documentée'].label("Documentée"),
        ved.c.Secteur.label("Secteur"),
        ved.c['Peu. type'].label("Peu. type"),
        ved.c['Précision localisation'].label("Précision localisation"),
        ved.c.Commentaires.label("Commentaires"),
        ved.c['Origine peuplement'].label("Origine peuplement"),
        ved.c['Origine plants touchés'].label("Origine plants touchés"),
        ved.c['Peu. mat.'].label("Peu. mat."),
        ved.c['Ess. 1'].label("Ess. 1"),
        ved.c['Ess. 2'].label("Ess. 2"),
        ved.c['Pât. stat.'].label("Pât. stat."),
        ved.c['Pât. freq.'].label("Pât. freq."),
        ved.c['Pât. type'].label("Pât. type"),
        ved.c['Pât. sais.'].label("Pât. sais."),
        ved.c['Pro. type'].label("Pro. type"),
        vdeg.c.degat_type_mnemo.label("Dég. type"),
        vdeg.c.degat_essence_mnemo.label("Dég. ess."),
        vdeg.c.degat_gravite_mnemo.label("Dég. grâ."),
        vdeg.c.degat_etendue_mnemo.label("Dég. éten."),
        vdeg.c.degat_anteriorite_mnemo.label("Dég. ant."),
    ).select_from(ved.join(vdeg, vdeg.c.id_declaration_degat == ved.c.id))

    return stmt


def get_v_export_declaration_shape_query():
    """
    """

    ved_query = get_v_export_declaration_csv_query()
    ved = ved_query.subquery("ved")

    vl_query = get_v_export_vl_declaration_query()
    vl = vl_query.subquery("vl")

    stmt = select(
        ved.c.id.label("id"),
        ved.c.Valide.label("Valide"),
        ved.c.Date.label("Date"),
        ved.c.Déclarant.label("Déclarant"),
        ved.c.Organisme.label("Organisme"),
        ved.c['Nom forêt'].label("Nom forêt"),
        ved.c['Statut forêt'].label("Statut forêt"),
        ved.c['Documentée'].label("Documentée"),
        ved.c.Secteur.label("Secteur"),
        ved.c['Peu. type'].label("Peu. type"),
        ved.c['Origine peuplement'].label("Origine peuplement"),
        ved.c['Origine plants touchés'].label("Origine plants touchés"),
        ved.c['Peu. mat.'].label("Peu. mat."),
        ved.c['Ess. 1'].label("Ess. 1"),
        ved.c['Ess. 2'].label("Ess. 2"),
        ved.c['Pât. stat.'].label("Pât. stat."),
        ved.c['Pât. freq.'].label("Pât. freq."),
        ved.c['Pât. type'].label("Pât. type"),
        ved.c['Pât. sais.'].label("Pât. sais."),
        ved.c['Pro. type'].label("Pro. type"),
        vl.c.geom.label("geom"),
    ).select_from(ved.join(vl, vl.c.id_declaration == ved.c.id))

    return stmt


def get_v_export_declaration_degats_shape_query():
    """
    """

    ved_query = get_v_export_declaration_degats_csv_query()
    ved = ved_query.subquery("ved")

    vl_query = get_v_export_vl_declaration_query()
    vl = vl_query.subquery("vl")

    stmt = select(
        ved.c.id.label("id"),
        ved.c.Valide.label("Valide"),
        ved.c.Date.label("Date"),
        ved.c.Déclarant.label("Déclarant"),
        ved.c.Organisme.label("Organisme"),
        ved.c['Nom forêt'].label("Nom forêt"),
        ved.c['Statut forêt'].label("Statut forêt"),
        ved.c['Documentée'].label("Documentée"),
        ved.c.Secteur.label("Secteur"),
        ved.c['Peu. type'].label("Peu. type"),
        ved.c['Origine peuplement'].label("Origine peuplement"),
        ved.c['Origine plants touchés'].label("Origine plants touchés"),
        ved.c['Peu. mat.'].label("Peu. mat."),
        ved.c['Ess. 1'].label("Ess. 1"),
        ved.c['Ess. 2'].label("Ess. 2"),
        ved.c['Pât. stat.'].label("Pât. stat."),
        ved.c['Pât. freq.'].label("Pât. freq."),
        ved.c['Pât. type'].label("Pât. type"),
        ved.c['Pât. sais.'].label("Pât. sais."),
        ved.c['Pro. type'].label("Pro. type"),
        ved.c['Dég. type'].label("Dég. type"),
        ved.c['Dég. ess.'].label("Dég. ess."),
        ved.c['Dég. grâ.'].label("Dég. grâ."),
        ved.c['Dég. éten.'].label("Dég. éten."),
        ved.c['Dég. ant.'].label("Dég. ant."),
        vl.c.geom.label("geom"),
    ).select_from(ved.join(vl, vl.c.id_declaration == ved.c.id))

    return stmt


def get_v_declaration_degats_restrict_query():
    """
    """

    vd_query = get_v_declarations_query()
    vd = vd_query.subquery("vd")

    vdeg_query = get_v_degats_query()
    vdeg = vdeg_query.subquery("vdeg")

    stmt = select(
        vd.c.declaration_date,
        vdeg.c.degat_gravite_label,
        vdeg.c.degat_etendue_label,
        vdeg.c.degat_anteriorite_label,
        vdeg.c.degat_essence_label,
        vdeg.c.degat_type_label,
        vd.c.peuplement_type_label,
        vd.c.secteur,
        vd.c.centroid,
        vd.c.organisme,
        vd.c.type_foret,
        vd.c.communes,
        vd.c.declarant,
        vd.c.b_peuplement_paturage_presence,
        vd.c.b_peuplement_protection_existence,
        vd.c.peuplement_acces_label,
        vd.c.peuplement_ess_1_label,
        vd.c.valide,
        vd.c.id_declaration,
    ).select_from(vd.join(vdeg, vdeg.c.id_declaration_degat == vd.c.id_declaration))

    return stmt

