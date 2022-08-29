"""
    modele chasse
"""

from flask import current_app
from utils_flask_sqla.serializers import serializable
from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property, object_session
from sqlalchemy import select, func, and_, join, exists
from sqlalchemy.sql.expression import case

from ..commons.models import TEspeces, TNomenclatures, TSecteurs

config = current_app.config
DB = config["DB"]


@serializable
class TPersonnes(DB.Model):
    """
    Personne (tir & constat)
    """

    __tablename__ = "t_personnes"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_personne = DB.Column(DB.Integer, primary_key=True)
    nom_personne = DB.Column(DB.Unicode)


@serializable
class TZoneCynegetiques(DB.Model):
    """
    Zones Cynegetiques
    """

    __tablename__ = "t_zone_cynegetiques"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_zone_cynegetique = DB.Column(DB.Integer, primary_key=True)
    code_zone_cynegetique = DB.Column(DB.Unicode)
    nom_zone_cynegetique = DB.Column(DB.Unicode)
    id_secteur = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    secteur = DB.relationship(TSecteurs, foreign_keys=id_secteur)


@serializable
class TZoneIndicatives(DB.Model):
    """
    Zones d'interet cynegetiques
    """

    __tablename__ = "t_zone_indicatives"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_zone_indicative = DB.Column(DB.Integer, primary_key=True)
    code_zone_indicative = DB.Column(DB.Unicode)
    nom_zone_indicative = DB.Column(DB.Unicode)
    id_zone_cynegetique = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique"),
    )
    zone_cynegetique = DB.relationship(
        TZoneCynegetiques, foreign_keys=id_zone_cynegetique
    )
    geom = DB.Column(Geometry)


@serializable
class TLieuTirs(DB.Model):
    """
    Lieu de tir
    """

    __tablename__ = "t_lieu_tirs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir = DB.Column(DB.Integer, primary_key=True)
    code_lieu_tir = DB.Column(DB.Unicode)
    nom_lieu_tir = DB.Column(DB.Unicode)
    geom = DB.Column(Geometry)
    id_area_commune = DB.Column(DB.Integer, DB.ForeignKey("ref_geo.l_areas.id_area"))
    label_commune = DB.Column(DB.Unicode)
    id_zone_indicative = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative = DB.relationship(TZoneIndicatives, foreign_keys=id_zone_indicative)


@serializable
class TLieuTirSynonymes(DB.Model):
    """
    Lieu de tir synonymes
    """

    __tablename__ = "t_lieu_tir_synonymes"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir_synonyme = DB.Column(DB.Integer, primary_key=True)
    id_lieu_tir = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_lieu_tirs.id_lieu_tir")
    )
    nom_lieu_tir_synonyme = DB.Column(DB.Unicode)

    lieu_tir = DB.relationship(TLieuTirs)
    # lieu_tir_synonyme_display = DB.Column(DB.Unicode)

    lieu_tir_synonyme_display = column_property(
        func.oeasc_chasse.get_lieu_tir_synonyme_label(id_lieu_tir_synonyme)
    )


@serializable
class TSaisons(DB.Model):
    """
    Saison de chasse
    """

    __tablename__ = "t_saisons"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison = DB.Column(DB.Integer, primary_key=True)
    nom_saison = DB.Column(DB.Unicode)
    date_debut = DB.Column(DB.Date)
    date_fin = DB.Column(DB.Date)
    current = DB.Column(DB.Boolean)
    commentaire = DB.Column(DB.Unicode)


@serializable
class TSaisonDates(DB.Model):
    """
    Date de chasse des différentes especes
    """

    __tablename__ = "t_saison_dates"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison_date = DB.Column(DB.Integer, primary_key=True)
    id_saison = DB.Column(DB.Integer, DB.ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    saison = DB.relationship(TSaisons, foreign_keys=id_saison)
    id_espece = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece = DB.relationship(TEspeces, foreign_keys=id_espece)
    date_debut = DB.Column(DB.Date)
    date_fin = DB.Column(DB.Date)
    id_nomenclature_type_chasse = DB.Column(
        DB.Integer, DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_type_chasse = DB.relationship(
        TNomenclatures, foreign_keys=id_nomenclature_type_chasse
    )


@serializable
class TAttributionMassifs(DB.Model):
    """
    Attribution selon les années
    """

    __tablename__ = "t_attribution_massifs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif = DB.Column(DB.Integer, primary_key=True)
    id_saison = DB.Column(DB.Integer, DB.ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    id_espece = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    id_zone_cynegetique = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique"),
    )
    nb_affecte_min = DB.Column(DB.Integer)
    nb_affecte_max = DB.Column(DB.Integer)

    saison = DB.relationship(TSaisons)
    espece = DB.relationship(TEspeces)
    zone_cynegetique = DB.relationship(TZoneCynegetiques)


@serializable
class VPlanChasseRealisationBilan(DB.Model):
    """
    Attribution selon les années
    """

    __tablename__ = "v_plan_chasse_realisation_bilan"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif = DB.Column(DB.Integer, primary_key=True)
    id_saison = DB.Column(DB.Integer, DB.ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    id_espece = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    id_secteur = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    id_zone_cynegetique = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique"),
    )
    id_zone_indicative = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    nb_affecte_min = DB.Column(DB.Integer)
    nb_affecte_max = DB.Column(DB.Integer)
    nb_realisation = DB.Column(DB.Integer)
    nb_realisation_avant_11 = DB.Column(DB.Integer)

    saison = DB.relationship(TSaisons)
    espece = DB.relationship(TEspeces)
    zone_cynegetique = DB.relationship(TZoneCynegetiques)
    zone_indicative = DB.relationship(TZoneIndicatives)
    secteur = DB.relationship(TSecteurs)


@serializable
class TTypeBracelets(DB.Model):
    """
    Type de bracelet
    """

    __tablename__ = "t_type_bracelets"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_type_bracelet = DB.Column(DB.Integer, primary_key=True)
    id_espece = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece = DB.relationship(TEspeces, foreign_keys=id_espece)
    code_type_bracelet = DB.Column(DB.Unicode)
    description_type_bracelet = DB.Column(DB.Unicode)


@serializable
class TAttributions(DB.Model):
    """
    Attributions
    """

    __tablename__ = "t_attributions"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution = DB.Column(DB.Integer, primary_key=True)
    id_type_bracelet = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_type_bracelets.id_type_bracelet")
    )
    id_saison = DB.Column(DB.Integer, DB.ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    numero_bracelet = DB.Column(DB.Unicode)
    id_zone_cynegetique_affectee = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique"),
    )
    id_zone_indicative_affectee = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    saison = DB.relationship(TSaisons)
    zone_cynegetique_affectee = DB.relationship(TZoneCynegetiques)
    zone_indicative_affectee = DB.relationship(TZoneIndicatives)
    type_bracelet = DB.relationship(TTypeBracelets)


@serializable
class TRealisationsChasse(DB.Model):
    """
    Realisations
    """

    __tablename__ = "t_realisations"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_realisation = DB.Column(DB.Integer, primary_key=True)
    id_attribution = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_attributions.id_attribution")
    )
    attribution = DB.relationship(TAttributions)

    saison = DB.relationship(
        TSaisons,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_saison==TSaisons.id_saison",
        uselist=False,
        viewonly=True,
    )

    id_auteur_tir = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_personnes.id_personne")
    )
    auteur_tir = DB.relationship(TPersonnes, foreign_keys=id_auteur_tir)

    id_auteur_constat = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_personnes.id_personne")
    )
    auteur_constat = DB.relationship(TPersonnes, foreign_keys=id_auteur_constat)

    id_zone_cynegetique_realisee = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique"),
    )
    zone_cynegetique_realisee = DB.relationship(TZoneCynegetiques)
    zone_cynegetique_affectee = DB.relationship(
        TZoneCynegetiques,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_cynegetique_affectee==TZoneCynegetiques.id_zone_cynegetique",
        uselist=False,
        viewonly=True,
    )

    id_zone_indicative_realisee = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative_realisee = DB.relationship(TZoneIndicatives)
    zone_indicative_affectee = DB.relationship(
        TZoneIndicatives,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_indicative_affectee==TZoneIndicatives.id_zone_indicative",
        uselist=False,
        viewonly=True,
    )

    id_lieu_tir_synonyme = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_chasse.t_lieu_tir_synonymes.id_lieu_tir_synonyme"),
    )
    lieu_tir_synonyme = DB.relationship(TLieuTirSynonymes)

    date_exacte = DB.Column(DB.Date)
    date_enreg = DB.Column(DB.Date)

    mortalite_hors_pc = DB.Column(DB.Boolean)
    parcelle_onf = DB.Column(DB.Boolean)

    id_nomenclature_sexe = DB.Column(
        DB.Integer, DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_sexe = DB.relationship(
        TNomenclatures, foreign_keys=id_nomenclature_sexe
    )

    id_nomenclature_classe_age = DB.Column(
        DB.Integer, DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_classe_age = DB.relationship(
        TNomenclatures, foreign_keys=id_nomenclature_classe_age
    )

    poid_entier = DB.Column(DB.Float)
    poid_vide = DB.Column(DB.Float)
    poid_c_f_p = DB.Column(DB.Float)

    long_dagues_droite = DB.Column(DB.Integer)
    long_dagues_gauche = DB.Column(DB.Integer)
    long_mandibules_droite = DB.Column(DB.Integer)
    long_mandibules_gauche = DB.Column(DB.Integer)

    cors_nb = DB.Column(DB.Integer)
    cors_commentaires = DB.Column(DB.Unicode)

    gestation = DB.Column(DB.Boolean)

    id_nomenclature_mode_chasse = DB.Column(
        DB.Integer, DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_mode_chasse = DB.relationship(
        TNomenclatures, foreign_keys=id_nomenclature_mode_chasse
    )

    commentaire = DB.Column(DB.Unicode)

    # poid_indique = DB.Column(DB.Boolean)
    # cors_indetermine = DB.Column(DB.Boolean)
    # long_mandibule_indetermine = DB.Column(DB.Boolean)

    # id_numerisateur = DB.Column(DB.Integer)

    # meta_create_date = DB.Column(DB.DateTime)
    # meta_update_date = DB.Column(DB.DateTime)


"""
relation : TAttributions.realisation

ou

column_property : TAttributions.has_realisation
"""

# TAttributions.realisation = DB.relationship(TRealisationsChasse)
TAttributions.has_realisation = column_property(
    exists().where(TRealisationsChasse.id_attribution == TAttributions.id_attribution)
)

TAttributions = serializable(TAttributions)


@serializable
class VChasseBilan(DB.Model):
    """
    Realisations
    """

    __tablename__ = "v_bilan_pretty"
    __table_args__ = {
        "schema": "oeasc_chasse",
        "extend_existing": True,
    }

    id_espece = DB.Column(DB.Integer(), primary_key=True)
    id_zone_cynegetique = DB.Column(DB.Integer(), primary_key=True)
    id_zone_indicative = DB.Column(DB.Integer(), primary_key=True)
    id_saison = DB.Column(DB.Integer(), primary_key=True)
    nom_saison = DB.Column(DB.Unicode())
    nom_zone_indicative = DB.Column(DB.Unicode())
    nom_zone_cynegetique = DB.Column(DB.Unicode())
    nom_espece = DB.Column(DB.Unicode())
    nb_affecte_max = DB.Column(DB.Integer())
    nb_affecte_min = DB.Column(DB.Integer())
    nb_realise = DB.Column(DB.Integer())
    nb_realise_avant_11 = DB.Column(DB.Integer())


# @serializable
# class VChassePreBilan(DB.Model):
#     '''
#         Realisations
#     '''

#     __tablename__ = 'v_pre_bilan_pretty'
#     __table_args__ = {
#         'schema': 'oeasc_chasse',
#         'extend_existing': True,
#     }

#     id_espece = DB.Column(DB.Integer(), primary_key=True)
#     id_zone_cynegetique = DB.Column(DB.Integer(), primary_key=True)
#     id_zone_indicative = DB.Column(DB.Integer(), primary_key=True)
#     id_saison = DB.Column(DB.Integer(), primary_key=True)
#     nom_saison = DB.Column(DB.Unicode())
#     nom_zone_indicative = DB.Column(DB.Unicode())
#     nom_zone_cynegetique = DB.Column(DB.Unicode())
#     nom_espece = DB.Column(DB.Unicode())
#     nb_affecte_max = DB.Column(DB.Integer())
#     nb_affecte_min = DB.Column(DB.Integer())
#     nb_realise = DB.Column(DB.Integer())
#     nb_realise_avant_11 = DB.Column(DB.Integer())
