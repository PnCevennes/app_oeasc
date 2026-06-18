"""
Fonctions de traitement de données pour les déclarations
"""

from sqlalchemy import (
    select,
    case,
    func,
    cast,
    String,
    and_,
    or_,
    update,
    union_all,
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
    TDegat,
    TDegatEssence,
)
from oeasc.ref_geo_oeasc.models import BibAreasType, LAreas, CorAreaIntersect, VMAreasSimples
from pypnnomenclature.models import TNomenclatures
from oeasc.modules.oeasc.declaration.models import TForet
from oeasc.modules.oeasc.user.models import VUsers

from flask import current_app


# Fonctions PostgreSQL custom (appelées via func)
def get_nomenclature_label(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_label(arg), "")


def get_nomenclature_mnemonique(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemonique(arg), "")


def get_nomenclature_code(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_code(arg), "")


def get_nomenclature_labels(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_labels(arg), "")


def get_liste_nomenclature_labels(id_declaration, table):
    """
    Crée une requête SQLAlchemy pour récupérer les libellés d'une nomenclature associée à une déclaration, en fonction de la table et de la colonne d'id de nomenclature spécifiées.
    """
    c_nomenclature = aliased(TNomenclatures, name="c_nomenclature")

    stmt = (
        select(func.string_agg(cast(c_nomenclature.label_fr, String), ", "))
        .select_from(table)
        .where(table.id_declaration == id_declaration)
        .where(c_nomenclature.id_nomenclature == table.id_nomenclature)
        .group_by(table.id_declaration)
        .correlate(TDeclaration)
    )

    return stmt


def get_nomenclature_mnemoniques(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_mnemoniques(arg), "")


def get_nomenclature_codes(arg):
    return func.coalesce(func.ref_nomenclatures.get_nomenclature_codes(arg), "")


def get_area_names(id_declaration, area_type):
    return func.coalesce(
        func.oeasc_declarations.get_area_names(id_declaration, area_type), ""
    )


def get_id_areas(id_declaration, area_type):
    return func.coalesce(
        func.oeasc_declarations.get_area_ids(id_declaration, area_type), ""
    )


# get_id_areas = func.oeasc_declarations.get_id_areas

###############################################################################$
################             NOUVEAUX STMT SIMPLIFIES           ################
###############################################################################$


def filter_declarations_a_renouveler(stmt):
    """Ajoute un filtre à une requête de déclarations pour ne récupérer que celles à renouveler, c'est à dire celles dont la date de fin est dépassée et qui ne sont pas archivées."""

    # Import local pour éviter un import circulaire avec repository
    import json
    import os

    # read declaration status using current_app.config at runtime
    with open(
        os.path.join(
            current_app.config["ROOT_DIR"], "config", "variables", "declaration.json"
        ),
        "r",
    ) as _f:
        statut_declaration = json.load(_f)["STATUT_DECLARATION"]

    stmt = stmt.where(
        TDeclaration.date_fin <= func.now(),  # date de fin dépassée
        or_(
            TDeclaration.statut == statut_declaration["Active"],
            TDeclaration.statut >= statut_declaration["Relance"],
        ),  # statut "Active" ou "Relance"
        TDeclaration.b_valid == True,
        # VUsers.accept_email == True
    )

    return stmt


def get_stmt_degats(id_declaration):
    """
    Crée une requête SQLAlchemy pour récupérer les informations sur les dégâts associés à une déclaration, avec les libellés et codes des nomenclatures.
    """

    stmt = (
        select(
            TDegat.id_declaration.label("id_declaration_degat"),
            TDegat.id_degat,
            TDegatEssence.id_degat_essence,
            get_nomenclature_mnemonique(TDegat.id_nomenclature_degat_type).label(
                "degat_type_mnemo"
            ),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_essence
            ).label("degat_essence_mnemo"),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_gravite
            ).label("degat_gravite_mnemo"),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_etendue
            ).label("degat_etendue_mnemo"),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_mnemo"),
            get_nomenclature_label(TDegat.id_nomenclature_degat_type).label(
                "degat_type_label"
            ),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_essence).label(
                "degat_essence_label"
            ),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_gravite).label(
                "degat_gravite_label"
            ),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_etendue).label(
                "degat_etendue_label"
            ),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_label"),
            get_nomenclature_code(TDegat.id_nomenclature_degat_type).label(
                "degat_type_code"
            ),
            get_nomenclature_code(TDegatEssence.id_nomenclature_degat_essence).label(
                "degat_essence_code"
            ),
            get_nomenclature_code(TDegatEssence.id_nomenclature_degat_gravite).label(
                "degat_gravite_code"
            ),
            get_nomenclature_code(TDegatEssence.id_nomenclature_degat_etendue).label(
                "degat_etendue_code"
            ),
            get_nomenclature_code(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_code"),
        )
        .select_from(TDegat)
        .where(TDegat.id_declaration == id_declaration)
        .join(
            TDegatEssence,
            TDegatEssence.id_degat == TDegat.id_degat,
            isouter=True,
        )
        .order_by(TDegat.id_declaration)
    )

    return stmt


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
    # CTE : nom_foret (via cor_area_intersect → vm_areas_simples)
    # -------------------------
    nom_foret_cte = (
        select(
            CorAreasDeclaration.id_declaration,
            func.string_agg(VMAreasSimples.area_name.distinct(), ", ").label("label_foret"),
        )
        .select_from(CorAreasDeclaration)
        .join(CorAreaIntersect, CorAreaIntersect.id_parcelle == CorAreasDeclaration.id_area)
        .join(
            VMAreasSimples,
            or_(
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_onf,
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_dgd,
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_prive,
            ),
        )
        .group_by(CorAreasDeclaration.id_declaration)
        .cte("nom_foret")
    )

    # -------------------------
    # CTE : secteur (via cor_area_intersect → vm_areas_simples)
    # -------------------------
    secteur_cte = (
        select(
            CorAreasDeclaration.id_declaration,
            func.string_agg(VMAreasSimples.area_name.distinct(), ", ").label("secteur"),
        )
        .select_from(CorAreasDeclaration)
        .join(CorAreaIntersect, CorAreaIntersect.id_parcelle == CorAreasDeclaration.id_area)
        .join(VMAreasSimples, VMAreasSimples.id_area == CorAreaIntersect.id_secteur)
        .group_by(CorAreasDeclaration.id_declaration)
        .cte("secteur")
    )

    # -------------------------
    # Requête principale
    # -------------------------
    # d = TDeclaration
    f = foret_cte
    p = peuplement_cte
    pn = peuplement_nomenclatures_cte
    deg = degat_type_cte
    nf = nom_foret_cte
    sec = secteur_cte
    # vu = VUsers

    stmt = (
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
            nf.c.label_foret,
            sec.c.secteur,
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
            TDeclaration.statut,
            TDeclaration.b_valid,
        )
        .select_from(TDeclaration)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)
        .join(f, f.c.id_foret == TDeclaration.id_foret)
        .join(p, p.c.id_declaration == TDeclaration.id_declaration)
        .join(pn, pn.c.id_declaration == TDeclaration.id_declaration)
        .join(deg, deg.c.id_declaration == TDeclaration.id_declaration)
        .outerjoin(nf, nf.c.id_declaration == TDeclaration.id_declaration)
        .outerjoin(sec, sec.c.id_declaration == TDeclaration.id_declaration)
    )

    return stmt


def get_stmt_fiche_declaration(id_declaration):
    """Récupère les informations d'une déclaration à partir de son id, pour l'affichage de la page de détail d'une déclaration"""

    nom_foret_subq = (
        select(func.string_agg(VMAreasSimples.area_name.distinct(), ", "))
        .select_from(CorAreasDeclaration)
        .join(CorAreaIntersect, CorAreaIntersect.id_parcelle == CorAreasDeclaration.id_area)
        .join(
            VMAreasSimples,
            or_(
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_onf,
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_dgd,
                VMAreasSimples.id_area == CorAreaIntersect.id_foret_prive,
            ),
        )
        .where(CorAreasDeclaration.id_declaration == id_declaration)
        .correlate(TDeclaration)
        .scalar_subquery()
    )

    secteur_subq = (
        select(func.string_agg(VMAreasSimples.area_name.distinct(), ", "))
        .select_from(CorAreasDeclaration)
        .join(CorAreaIntersect, CorAreaIntersect.id_parcelle == CorAreasDeclaration.id_area)
        .join(VMAreasSimples, VMAreasSimples.id_area == CorAreaIntersect.id_secteur)
        .where(CorAreasDeclaration.id_declaration == id_declaration)
        .correlate(TDeclaration)
        .scalar_subquery()
    )

    communes_subq = (
        select(func.string_agg(VMAreasSimples.area_name.distinct(), ", "))
        .select_from(CorAreasDeclaration)
        .join(CorAreaIntersect, CorAreaIntersect.id_parcelle == CorAreasDeclaration.id_area)
        .join(VMAreasSimples, VMAreasSimples.id_area == CorAreaIntersect.id_commune)
        .where(CorAreasDeclaration.id_declaration == id_declaration)
        .correlate(TDeclaration)
        .scalar_subquery()
    )

    stmt = (
        select(
            ########################## INFORMATIONS ######################################
            TDeclaration.id_declaration,
            TDeclaration.b_valid.label("b_valid"),
            TDeclaration.centroid.label("centroid"),
            case(
                (TDeclaration.b_valid == True, "Validé"),
                (TDeclaration.b_valid == False, "Non validé"),
                else_="En attente",
            ).label("valide"),
            case(
                (TDeclaration.b_autorisation == True, "Autorisé"),
                (TDeclaration.b_autorisation == False, "Non autorisé"),
                else_="Inconnu",
            ).label("autorisation"),
            func.to_char(TDeclaration.meta_create_date, "DD/MM/YYYY").label(
                "declaration_date"
            ),
            func.to_char(TDeclaration.date_fin, "DD/MM/YYYY").label("date_fin"),
            TDeclaration.statut.label("statut"),
            # ############################ DECLARANT ######################################
            VUsers.id_role.label("id_declarant"),
            VUsers.nom_complet.label("declarant"),
            VUsers.email.label("email"),
            VUsers.organisme.label("organisme"),
            ############################ FORET ######################################
            nom_foret_subq.label("nom_foret"),
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
            TForet.surface_renseignee.label("surface_renseignee"),
            # case((TForet.b_statut_public == True, "Public"), else_="Privé").label(
            #     "statut_foret"
            # ),
            # case((TForet.b_document == True, "Oui (document de gestion durable)"), else_="Non").label("documentee"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationEspece
            ).label("especes_labels"),
            # ######################## PEUPLEMENT LOCALISATION  ###################################
            secteur_subq.label("secteur"),
            communes_subq.label("communes"),
            case(
                (
                    and_(TForet.b_statut_public == True, TForet.b_document == True),
                    get_area_names(TDeclaration.id_declaration, "OEASC_ONF_UG"),
                ),
                else_=get_area_names(TDeclaration.id_declaration, "OEASC_CADASTRE"),
            ).label("parcelles"),
            get_nomenclature_label(TDeclaration.id_nomenclature_peuplement_acces).label(
                "accessibilite"
            ),
            TDeclaration.precision_localisation.label("precision_localisation"),
            # ####################### PEUPLEMENT ESSENCES ###################################
            get_nomenclature_label(
                TDeclaration.id_nomenclature_peuplement_essence_principale
            ).label("peuplement_ess_1"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationEssenceSecondaire
            ).label("peuplement_ess_2"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationEssenceComplementaire
            ).label("peuplement_ess_3"),
            # ####################### PEUPLEMENT DESCRIPTION ###################################
            get_nomenclature_mnemonique(
                TDeclaration.id_nomenclature_peuplement_type
            ).label("peuplement_type"),
            get_nomenclature_mnemonique(
                TDeclaration.id_nomenclature_peuplement_origine
            ).label("origine_peuplement"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationOrigine
            ).label("origine_plants_touches"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationMaturite
            ).label("peuplement_maturite"),
            # ############################   PEUPLEMENT PATURAGE/PROTECTION  ########################
            get_nomenclature_label(
                TDeclaration.id_nomenclature_peuplement_paturage_statut
            ).label("paturage_statut"),
            get_nomenclature_label(
                TDeclaration.id_nomenclature_peuplement_paturage_frequence
            ).label("paturage_frequence"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationPaturageType
            ).label("peuplement_paturage_type"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationPaturageSaison
            ).label("peuplement_paturage_saison"),
            get_liste_nomenclature_labels(
                id_declaration, CorNomenclatureDeclarationProtectionType
            ).label("peuplement_protection_type"),
            TDeclaration.commentaire.label("commentaire"),
            TDeclaration.token_renouvellement,
            TDeclaration.date_fin_token,
            TForet.b_document.label("document_foret"),
            TForet.b_statut_public.label("statut_public_foret"),
        )
        .where(TDeclaration.id_declaration == id_declaration)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)
        .join(TForet, TForet.id_foret == TDeclaration.id_foret)
    )

    return stmt


def get_stmt_for_resultats_degats():
    """Récupère les dégats pour l'affichage des résultats (page: résultats de suivis/système d'alerte)"""

    stmt_all_degats = (
        select(
            TDeclaration.b_peuplement_paturage_presence,
            TDeclaration.b_peuplement_protection_existence,
            TDeclaration.centroid,
            get_area_names(TDeclaration.id_declaration, "OEASC_COMMUNE").label(
                "communes"
            ),
            VUsers.nom_complet.label("declarant"),
            func.to_char(TDeclaration.meta_create_date, "DD/MM/YYYY").label(
                "declaration_date"
            ),
            get_nomenclature_label(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("degat_anteriorite_label"),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_essence).label(
                "degat_essence_label"
            ),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_etendue).label(
                "degat_etendue_label"
            ),
            get_nomenclature_label(TDegatEssence.id_nomenclature_degat_gravite).label(
                "degat_gravite_label"
            ),
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
            get_area_names(TDeclaration.id_declaration, "OEASC_SECTEUR").label(
                "secteur"
            ),
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
    """Récupère les informations sur les déclarations, les dégats et les forêts pour l'export des données (csv ou shape)
    type_file: "csv" ou "shape"
    type_out: "degat" ou "declaration"
    Si type_out == "degat", alors on récupère une ligne par dégât, avec les infos de la déclaration et du dégât.
    Si type_out == "declaration", alors on récupère une ligne par déclaration, avec les infos de la déclaration et une liste des types de dégats associés à la déclaration (sans les détails des dégats).
    Si type_file == "shape", alors on récupère la géométrie de la déclaration (champ geom de la table t_declaration).

    """

    stmt = select(
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
        get_nomenclature_mnemonique(
            TDeclaration.id_nomenclature_peuplement_origine
        ).label("Origine peuplement"),
        (  # liste des origines des plants touchés
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationOrigine)
            .where(
                CorNomenclatureDeclarationOrigine.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationOrigine.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationOrigine.id_declaration)
            .correlate(TDeclaration)
        ).label("Origine plants touchés"),
        (  # liste des maturités
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationMaturite)
            .where(
                CorNomenclatureDeclarationMaturite.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationMaturite.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationMaturite.id_declaration)
            .correlate(TDeclaration)
        ).label("Peu. mat."),
        get_nomenclature_mnemonique(
            TDeclaration.id_nomenclature_peuplement_essence_principale
        ).label("Ess. 1"),
        (  # liste des essences secondaires
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationEssenceSecondaire)
            .where(
                CorNomenclatureDeclarationEssenceSecondaire.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationEssenceSecondaire.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationEssenceSecondaire.id_declaration)
            .correlate(TDeclaration)
        ).label("Ess. 2"),
        (  # liste des essences complémentaires
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationEssenceComplementaire)
            .where(
                CorNomenclatureDeclarationEssenceComplementaire.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationEssenceComplementaire.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationEssenceComplementaire.id_declaration)
            .correlate(TDeclaration)
        ).label("Ess. 3"),
        get_nomenclature_mnemonique(
            TDeclaration.id_nomenclature_peuplement_paturage_statut
        ).label("Pât. stat."),
        get_nomenclature_mnemonique(
            TDeclaration.id_nomenclature_peuplement_paturage_frequence
        ).label("Pât. freq."),
        (  # liste des types de pâturage
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationPaturageType)
            .where(
                CorNomenclatureDeclarationPaturageType.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationPaturageType.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationPaturageType.id_declaration)
            .correlate(TDeclaration)
        ).label("Pât. type"),
        (  # liste des types de protection
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationProtectionType)
            .where(
                CorNomenclatureDeclarationProtectionType.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationProtectionType.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationProtectionType.id_declaration)
            .correlate(TDeclaration)
        ).label("Pro. type"),
        (  # liste des saisons de pâturage
            select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
            .select_from(CorNomenclatureDeclarationPaturageSaison)
            .where(
                CorNomenclatureDeclarationPaturageSaison.id_declaration
                == TDeclaration.id_declaration
            )
            .where(
                TNomenclatures.id_nomenclature
                == CorNomenclatureDeclarationPaturageSaison.id_nomenclature
            )
            .group_by(CorNomenclatureDeclarationPaturageSaison.id_declaration)
            .correlate(TDeclaration)
        ).label("Pât. sais."),
    )

    if type_out == "degat":
        stmt = stmt.add_columns(
            get_nomenclature_mnemonique(TDegat.id_nomenclature_degat_type).label(
                "Dég. type"
            ),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_essence
            ).label("Dég. ess."),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_gravite
            ).label("Dég. grâ."),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_etendue
            ).label("Dég. éten."),
            get_nomenclature_mnemonique(
                TDegatEssence.id_nomenclature_degat_anteriorite
            ).label("Dég. ant."),
        )
    elif type_out == "declaration":
        # Ajout d'une colonne degat Type avec la liste de tous les types de dégats en chaine de caractères
        stmt = stmt.add_columns(
            (
                select(func.string_agg(cast(TNomenclatures.mnemonique, String), ", "))
                .select_from(TDegat)
                .where(TDegat.id_declaration == TDeclaration.id_declaration)
                .where(
                    TNomenclatures.id_nomenclature == TDegat.id_nomenclature_degat_type
                )
                .group_by(TDegat.id_declaration)
                .correlate(TDeclaration)
            ).label("Deg. type"),
        )

    if type_file == "gpkg":
        stmt = stmt.add_columns(TDeclaration.geom.label("geom"))
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
        stmt = (
            stmt.select_from(TDeclaration)
            .join(VUsers, TDeclaration.id_declarant == VUsers.id_role)
            .join(TForet, TDeclaration.id_foret == TForet.id_foret)
            .order_by(TDeclaration.meta_create_date.desc())
        )
    elif type_out == "degat":
        stmt = (
            stmt.outerjoin(TDegatEssence, TDegat.id_degat == TDegatEssence.id_degat)
            .join(TDeclaration, TDegat.id_declaration == TDeclaration.id_declaration)
            .join(VUsers, TDeclaration.id_declarant == VUsers.id_role)
            .join(TForet, TDeclaration.id_foret == TForet.id_foret)
            .order_by(TDeclaration.meta_create_date.desc())
        )

    return stmt


def get_stmt_areas_declaration(id_declaration, area_code):
    """
    Crée une requête SQLAlchemy pour récupérer les noms des zones associées à une déclaration, en fonction du type de zone spécifié.
    area_code = code du type de zone (ex :
    OEASC_SECTEUR: Secteurs / Massifs OEASC
    OEASC_COMMUNE: Communes de l'OEASC
    OEASC_ONF_FRT: Forêts relevant du régime forestier
    OEASC_ONF_PRF: parcelles de forêt relevant du régime forestier
    OEASC_ONF_UG: Unités de gestion relevant du régime forestier
    OEASC_DGD: Forêts relevant du régime privé et possédant un document de gestion durable
    OEASC_CADASTRE: Parcelles issues du cadastre
    OEASC_SECTION: Sections cadastrales
    """

    stmt = (
        select(
            LAreas.id_area,
            LAreas.id_type,
            LAreas.area_name,
            LAreas.area_code,
            LAreas.source,
            LAreas.comment,
            LAreas.enable,
            LAreas.meta_create_date,
            LAreas.meta_update_date,
            LAreas.geom_4326,
        )
        .select_from(CorAreasDeclaration)
        .where(CorAreasDeclaration.id_declaration == id_declaration)
        .where(BibAreasType.type_code == area_code)
        .join(LAreas, LAreas.id_area == CorAreasDeclaration.id_area)
        .join(BibAreasType, BibAreasType.id_type == LAreas.id_type)
        .correlate(TDeclaration)
    )

    return stmt


def get_stmt_all_areas_declaration(id_declaration, list_id_types=[]):
    """Retourne les aires (via cor_area_intersect → vm_lareas_simples) concernant une déclaration.
    Utilisée pour afficher la carte dans voir_declaration.
    Pour les types de zone non-directs, les aires sont trouvées via cor_area_intersect à partir
    des parcelles liées à la déclaration. Pour CADASTRES (332) et UG_ONF (330), les parcelles
    elles-mêmes sont utilisées directement depuis cor_areas_declarations.
    """

    parcelles_q = (
        select(CorAreasDeclaration.id_area)
        .where(CorAreasDeclaration.id_declaration == id_declaration)
    )

    # Mapping id_type → colonne de cor_area_intersect
    col_map = {
        326: CorAreaIntersect.id_secteur,
        327: CorAreaIntersect.id_commune,
        328: CorAreaIntersect.id_foret_onf,
        329: CorAreaIntersect.id_parcelle_onf,
        331: CorAreaIntersect.id_foret_dgd,
        333: CorAreaIntersect.id_section_cadastrale,
    }
    # types dont les parcelles de la déclaration SONT les aires (pas besoin de cor_area_intersect)
    direct_types = [330, 332]

    if list_id_types:
        types_via_intersect = [t for t in col_map if t in list_id_types]
        types_direct = [t for t in direct_types if t in list_id_types]
    else:
        types_via_intersect = list(col_map.keys())
        types_direct = direct_types

    subqueries = []

    for id_type in types_via_intersect:
        col = col_map[id_type]
        q = (
            select(col.label("id_area"))
            .select_from(CorAreaIntersect)
            .where(CorAreaIntersect.id_parcelle.in_(parcelles_q))
            .where(col.isnot(None))
        )
        subqueries.append(q)

    if types_direct:
        q = (
            select(CorAreasDeclaration.id_area.label("id_area"))
            .where(CorAreasDeclaration.id_declaration == id_declaration)
        )
        subqueries.append(q)

    if not subqueries:
        return select(VMAreasSimples).where(VMAreasSimples.id_area == None)

    area_ids_union = union_all(*subqueries).subquery()

    stmt = (
        select(VMAreasSimples)
        .where(VMAreasSimples.id_area.in_(select(area_ids_union.c.id_area)))
    )

    if list_id_types:
        stmt = stmt.where(VMAreasSimples.id_type.in_(list_id_types))

    return stmt


def stmt_one_declaration_a_renouveler(id_declaration):
    """Requête pour récupérer les informations d'une déclaration à partir de son id, pour l'affichage de la page de détail d'une déclaration"""

    stmt = select(
        TDeclaration.id_declaration,
        TDeclaration.token_renouvellement,
        TDeclaration.date_fin_token,
        TDeclaration.date_fin,
    )
    stmt = filter_declarations_a_renouveler(stmt)
    stmt = stmt.where(TDeclaration.id_declaration == id_declaration)

    return stmt


def stmt_change_statut_declaration(id_declaration, new_statut):
    """Requête pour changer le statut d'une déclaration à partir de son id"""

    stmt = (
        update(TDeclaration)
        .where(TDeclaration.id_declaration == id_declaration)
        .values(statut=new_statut)
    )

    return stmt


def stmt_liste_declarations_a_renouveler(statut_declaration):
    """
    Requête pour avoir la liste des déclarations à renouveler, c'est à dire celles dont la date de fin est dépassée et qui ne sont pas archivées.
    Les colonnes récupérées sont les mêmes que celles de la page "alertes signalées" pour pouvoir afficher un tableau similaire,
    avec en plus les colonnes nécessaires à l'envoi des emails de relance.
    """
    # On récupère les informations concernant le déclarants des déclarations à renouveler

    # on récupère les mêmes colonnes que la page "alertes signalées" pour pouvoir afficher un tableau similaire.
    stmt_renew = get_stmt_liste_declaration()
    # On ajoute les quelques colonnes nécéssaires à l'envoi des emails.
    stmt_renew = stmt_renew.add_columns(
        VUsers.email,
        VUsers.nom_role,
        VUsers.prenom_role,
        VUsers.accept_email.label("accept_email"),
        TDeclaration.date_fin_token,
    )
    # on ajoute un filtre pour ne récupérer que les déclarations à renouveler. C'est à dire celles dont la date de fin est dépassée et qui ne sont pas archivées.
    stmt_renew = stmt_renew.where(
        TDeclaration.date_fin <= func.now(),  # date de fin dépassée
        or_(
            TDeclaration.statut == statut_declaration["Active"],
            TDeclaration.statut >= statut_declaration["Relance"],
        ),  # statut "Active" ou "Relance"
        TDeclaration.b_valid == True,
        # VUsers.accept_email == True
    )
    return stmt_renew

