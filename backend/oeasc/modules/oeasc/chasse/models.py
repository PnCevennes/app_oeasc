"""
modele chasse
"""

from flask import current_app
from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable
from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property, relationship, Mapped
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    func,
    exists,
)

from ..commons.models import TEspeces, TSecteurs, TNomenclaturesOeasc

# from pypnnomenclature.models import TNomenclatures
# from sqlalchemy import select
# from sqlalchemy.ext.hybrid import hybrid_property
# from typing import Optional, List

config = current_app.config
DB = config["DB"]


# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True



@serializable
class TZoneCynegetiques(CustomModel):
    __tablename__ = "t_zone_cynegetiques"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_zone_cynegetique: Mapped[int] = Column(Integer, primary_key=True)
    code_zone_cynegetique: Mapped[str] = Column(Unicode, unique=True)
    nom_zone_cynegetique: Mapped[str] = Column(Unicode)
    id_secteur: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    secteur: Mapped["TSecteurs"] = relationship(TSecteurs, foreign_keys=id_secteur)


@serializable
@geoserializable  # pour serialiser geom
class TZoneIndicatives(CustomModel):
    __tablename__ = "t_zone_indicatives"
    __table_args__ = (
        # UniqueConstraint("code_zone_indicative", "id_zone_cynegetique", name="unique_code_zone_indicative_id_zone_cynegetique"),
        {"schema": "oeasc_chasse", "extend_existing": True},
    )

    id_zone_indicative: Mapped[int] = Column(Integer, primary_key=True)
    code_zone_indicative: Mapped[str] = Column(Unicode, unique=True)
    nom_zone_indicative: Mapped[str] = Column(Unicode)
    id_zone_cynegetique: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    zone_cynegetique: Mapped["TZoneCynegetiques"] = relationship(
        TZoneCynegetiques, foreign_keys=id_zone_cynegetique
    )

    geom: Mapped[object] = Column(Geometry("GEOMETRY", 4326))


@serializable
@geoserializable  # pour serialiser geom
class TLieuTirs(CustomModel):
    __tablename__ = "t_lieu_tirs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir: Mapped[int] = Column(Integer, primary_key=True)
    code_lieu_tir: Mapped[str] = Column(Unicode)
    nom_lieu_tir: Mapped[str] = Column(Unicode)
    geom: Mapped[object] = Column(Geometry("GEOMETRY", 4326))

    id_area_commune: Mapped[int] = Column(
        Integer, ForeignKey("ref_geo.l_areas.id_area")
    )
    label_commune: Mapped[str] = Column(Unicode)
    id_zone_indicative: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative: Mapped["TZoneIndicatives"] = relationship(
        TZoneIndicatives, foreign_keys=id_zone_indicative
    )


@serializable
class TLieuTirSynonymes(CustomModel):
    __tablename__ = "t_lieu_tir_synonymes"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir_synonyme: Mapped[int] = Column(Integer, primary_key=True)
    id_lieu_tir: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_lieu_tirs.id_lieu_tir")
    )
    nom_lieu_tir_synonyme: Mapped[str] = Column(Unicode)
    lieu_tir: Mapped["TLieuTirs"] = relationship(TLieuTirs)
    lieu_tir_synonyme_display: Mapped[str] = column_property(
        func.oeasc_chasse.get_lieu_tir_synonyme_label(id_lieu_tir_synonyme)
    )


@serializable
class TSaisons(CustomModel):
    __tablename__ = "t_saisons"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison: Mapped[int] = Column(Integer, primary_key=True)
    nom_saison: Mapped[str] = Column(Unicode)
    date_debut: Mapped[Date] = Column(Date)
    date_fin: Mapped[Date] = Column(Date)
    current: Mapped[bool] = Column(Boolean)
    commentaire: Mapped[str] = Column(Unicode)


@serializable
class TSaisonDates(CustomModel):
    __tablename__ = "t_saison_dates"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison_date: Mapped[int] = Column(Integer, primary_key=True)
    id_saison: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison")
    )
    saison: Mapped["TSaisons"] = relationship(TSaisons, foreign_keys=id_saison)
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece: Mapped["TEspeces"] = relationship(TEspeces, foreign_keys=id_espece)
    date_debut: Mapped[Date] = Column(Date)
    date_fin: Mapped[Date] = Column(Date)
    id_nomenclature_type_chasse: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_type_chasse: Mapped["TNomenclaturesOeasc"] = relationship(
        TNomenclaturesOeasc,
        foreign_keys=id_nomenclature_type_chasse,
        # single_parent=True,
        primaryjoin="TSaisonDates.id_nomenclature_type_chasse == TNomenclaturesOeasc.id_nomenclature"
    )


@serializable
class TAttributionMassifs(CustomModel):
    __tablename__ = "t_attribution_massifs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif: Mapped[int] = Column(Integer, primary_key=True)
    id_saison: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison")
    )
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    id_zone_cynegetique: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    nb_affecte_min: Mapped[int] = Column(Integer)
    nb_affecte_max: Mapped[int] = Column(Integer)
    saison: Mapped["TSaisons"] = relationship(TSaisons)
    espece: Mapped["TEspeces"] = relationship(TEspeces)
    zone_cynegetique: Mapped["TZoneCynegetiques"] = relationship(TZoneCynegetiques)


@serializable
class VPlanChasseRealisationBilan(CustomModel):
    __tablename__ = "v_plan_chasse_realisation_bilan"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif: Mapped[int] = Column(Integer, primary_key=True)
    id_saison: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison")
    )
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    id_secteur: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    id_zone_cynegetique: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    id_zone_indicative: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    nb_affecte_min: Mapped[int] = Column(Integer)
    nb_affecte_max: Mapped[int] = Column(Integer)
    nb_realisation: Mapped[int] = Column(Integer)
    nb_realisation_avant_11: Mapped[int] = Column(Integer)
    saison: Mapped["TSaisons"] = relationship(TSaisons)
    espece: Mapped["TEspeces"] = relationship(TEspeces)
    zone_cynegetique: Mapped["TZoneCynegetiques"] = relationship(TZoneCynegetiques)
    zone_indicative: Mapped["TZoneIndicatives"] = relationship(TZoneIndicatives)
    secteur: Mapped["TSecteurs"] = relationship(TSecteurs)


@serializable
class TTypeBracelets(CustomModel):
    __tablename__ = "t_type_bracelets"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_type_bracelet: Mapped[int] = Column(Integer, primary_key=True)
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece: Mapped["TEspeces"] = relationship(TEspeces, foreign_keys=id_espece)
    code_type_bracelet: Mapped[str] = Column(Unicode)
    description_type_bracelet: Mapped[str] = Column(Unicode)


@serializable
class TAttributions(CustomModel):
    __tablename__ = "t_attributions"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution: Mapped[int] = Column(Integer, primary_key=True)
    id_type_bracelet: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_type_bracelets.id_type_bracelet")
    )
    id_saison: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison")
    )
    numero_bracelet: Mapped[str] = Column(Unicode)
    id_zone_cynegetique_affectee: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    id_zone_indicative_affectee: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    
    realisations:Mapped["TRealisationsChasse"] = relationship(
        'TRealisationsChasse',
        back_populates='attribution',
        lazy='select' 
    )

    saison: Mapped["TSaisons"] = relationship(TSaisons)
    zone_cynegetique_affectee: Mapped["TZoneCynegetiques"] = relationship(
        TZoneCynegetiques
    )
    zone_indicative_affectee: Mapped["TZoneIndicatives"] = relationship(
        TZoneIndicatives
    )
    type_bracelet: Mapped["TTypeBracelets"] = relationship(TTypeBracelets)

    meta_create_date: Mapped[DateTime] = Column(DateTime)
    meta_update_date: Mapped[DateTime] = Column(DateTime)


@serializable
class TRealisationsChasse(CustomModel):
    __tablename__ = "t_realisations"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_realisation: Mapped[int] = Column(Integer, primary_key=True)
    id_attribution: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_attributions.id_attribution")
    )
    # attribution: Mapped["TAttributions"] = relationship(TAttributions)
    attribution: Mapped["TAttributions"] = relationship(
        'TAttributions',
        back_populates='realisations'
    )
    
    saison: Mapped["TSaisons"] = relationship(
        TSaisons,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_saison==TSaisons.id_saison",
        uselist=False,
        viewonly=True,
    )

   
    auteur_tir_str: Mapped[str] = Column(Unicode) # champ texte libre pour l'auteur du tir
    auteur_constat_str: Mapped[str] = Column(Unicode) # champ texte libre pour l'auteur du constat

    
    id_zone_cynegetique_realisee: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    zone_cynegetique_realisee: Mapped["TZoneCynegetiques"] = relationship(
        TZoneCynegetiques
    )
    zone_cynegetique_affectee: Mapped["TZoneCynegetiques"] = relationship(
        TZoneCynegetiques,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_cynegetique_affectee==TZoneCynegetiques.id_zone_cynegetique",
        uselist=False,
        viewonly=True,
    )

    id_zone_indicative_realisee: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative_realisee: Mapped["TZoneIndicatives"] = relationship(
        TZoneIndicatives
    )
    zone_indicative_affectee: Mapped["TZoneIndicatives"] = relationship(
        TZoneIndicatives,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_indicative_affectee==TZoneIndicatives.id_zone_indicative",
        uselist=False,
        viewonly=True,
    )

    id_lieu_tir_synonyme: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_chasse.t_lieu_tir_synonymes.id_lieu_tir_synonyme")
    )
    lieu_tir_synonyme: Mapped["TLieuTirSynonymes"] = relationship(TLieuTirSynonymes)
    date_exacte: Mapped[Date] = Column(Date)
    date_enreg: Mapped[Date] = Column(Date)
    mortalite_hors_pc: Mapped[bool] = Column(Boolean)
    parcelle_onf: Mapped[bool] = Column(Boolean)
    id_nomenclature_sexe: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_sexe: Mapped["TNomenclaturesOeasc"] = relationship(
        TNomenclaturesOeasc, foreign_keys=id_nomenclature_sexe
    )
    id_nomenclature_classe_age: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_classe_age: Mapped["TNomenclaturesOeasc"] = relationship(
        TNomenclaturesOeasc, foreign_keys=id_nomenclature_classe_age
    )
    poid_entier: Mapped[float] = Column(Float)
    poid_vide: Mapped[float] = Column(Float)
    poid_c_f_p: Mapped[float] = Column(Float)
    long_dagues_droite: Mapped[int] = Column(Integer)
    long_dagues_gauche: Mapped[int] = Column(Integer)
    long_mandibules_droite: Mapped[int] = Column(Integer)
    long_mandibules_gauche: Mapped[int] = Column(Integer)
    cors_nb: Mapped[int] = Column(Integer)
    cors_commentaires: Mapped[str] = Column(Unicode)
    gestation: Mapped[bool] = Column(Boolean)
    id_nomenclature_mode_chasse: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_mode_chasse: Mapped["TNomenclaturesOeasc"] = relationship(
        TNomenclaturesOeasc, foreign_keys=id_nomenclature_mode_chasse
    )
    commentaire: Mapped[str] = Column(Unicode)


# Définition de la propriété de colonne après les définitions de classes pour éviter les références circulaires
TAttributions.has_realisation = column_property(
    exists().where(TRealisationsChasse.id_attribution == TAttributions.id_attribution)
)


@serializable
class VChasseBilan(CustomModel):
    __tablename__ = "v_bilan_pretty"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_espece: Mapped[int] = Column(Integer, primary_key=True)
    id_zone_cynegetique: Mapped[int] = Column(Integer, primary_key=True)
    id_zone_indicative: Mapped[int] = Column(Integer, primary_key=True)
    id_saison: Mapped[int] = Column(Integer, primary_key=True)
    nom_saison: Mapped[str] = Column(Unicode)
    nom_zone_indicative: Mapped[str] = Column(Unicode)
    nom_zone_cynegetique: Mapped[str] = Column(Unicode)
    nom_espece: Mapped[str] = Column(Unicode)
    nb_affecte_max: Mapped[int] = Column(Integer)
    nb_affecte_min: Mapped[int] = Column(Integer)
    nb_realise: Mapped[int] = Column(Integer)
    nb_realise_avant_11: Mapped[int] = Column(Integer)
