"""
modele chasse
"""

from flask import current_app
from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable
from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property, relationship
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

from ..commons.models import TEspeces, TSecteurs, TNomenclatures_oeasc
# from pypnnomenclature.models import TNomenclatures

config = current_app.config
DB = config["DB"]


# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True


@serializable
class TPersonnes(CustomModel):
    __tablename__ = "t_personnes"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_personne = Column(Integer, primary_key=True)
    nom_personne = Column(Unicode)


@serializable
class TZoneCynegetiques(CustomModel):
    __tablename__ = "t_zone_cynegetiques"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_zone_cynegetique = Column(Integer, primary_key=True)
    code_zone_cynegetique = Column(Unicode)
    nom_zone_cynegetique = Column(Unicode)
    id_secteur = Column(Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur"))
    secteur = relationship(TSecteurs, foreign_keys=id_secteur)


@serializable
@geoserializable
class TZoneIndicatives(CustomModel):
    __tablename__ = "t_zone_indicatives"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_zone_indicative = Column(Integer, primary_key=True)
    code_zone_indicative = Column(Unicode)
    nom_zone_indicative = Column(Unicode)
    id_zone_cynegetique = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    zone_cynegetique = relationship(TZoneCynegetiques, foreign_keys=id_zone_cynegetique)
    geom = Column(Geometry)


@serializable
@geoserializable
class TLieuTirs(CustomModel):
    __tablename__ = "t_lieu_tirs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir = Column(Integer, primary_key=True)
    code_lieu_tir = Column(Unicode)
    nom_lieu_tir = Column(Unicode)
    geom = Column(Geometry)
    id_area_commune = Column(Integer, ForeignKey("ref_geo.l_areas.id_area"))
    label_commune = Column(Unicode)
    id_zone_indicative = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative = relationship(TZoneIndicatives, foreign_keys=id_zone_indicative)


@serializable
class TLieuTirSynonymes(CustomModel):
    __tablename__ = "t_lieu_tir_synonymes"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_lieu_tir_synonyme = Column(Integer, primary_key=True)
    id_lieu_tir = Column(Integer, ForeignKey("oeasc_chasse.t_lieu_tirs.id_lieu_tir"))
    nom_lieu_tir_synonyme = Column(Unicode)
    lieu_tir = relationship(TLieuTirs)
    lieu_tir_synonyme_display = column_property(
        func.oeasc_chasse.get_lieu_tir_synonyme_label(id_lieu_tir_synonyme)
    )


@serializable
class TSaisons(CustomModel):
    __tablename__ = "t_saisons"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison = Column(Integer, primary_key=True)
    nom_saison = Column(Unicode)
    date_debut = Column(Date)
    date_fin = Column(Date)
    current = Column(Boolean)
    commentaire = Column(Unicode)


@serializable
class TSaisonDates(CustomModel):
    __tablename__ = "t_saison_dates"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_saison_date = Column(Integer, primary_key=True)
    id_saison = Column(Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    saison = relationship(TSaisons, foreign_keys=id_saison)
    id_espece = Column(Integer, ForeignKey("oeasc_commons.t_especes.id_espece"))
    espece = relationship(TEspeces, foreign_keys=id_espece)
    date_debut = Column(Date)
    date_fin = Column(Date)
    id_nomenclature_type_chasse = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_type_chasse = relationship(
        TNomenclatures_oeasc, foreign_keys=id_nomenclature_type_chasse
    )


@serializable
class TAttributionMassifs(CustomModel):
    __tablename__ = "t_attribution_massifs"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif = Column(Integer, primary_key=True)
    id_saison = Column(Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    id_espece = Column(Integer, ForeignKey("oeasc_commons.t_especes.id_espece"))
    id_zone_cynegetique = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    nb_affecte_min = Column(Integer)
    nb_affecte_max = Column(Integer)
    saison = relationship(TSaisons)
    espece = relationship(TEspeces)
    zone_cynegetique = relationship(TZoneCynegetiques)


@serializable
class VPlanChasseRealisationBilan(CustomModel):
    __tablename__ = "v_plan_chasse_realisation_bilan"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution_massif = Column(Integer, primary_key=True)
    id_saison = Column(Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    id_espece = Column(Integer, ForeignKey("oeasc_commons.t_especes.id_espece"))
    id_secteur = Column(Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur"))
    id_zone_cynegetique = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    id_zone_indicative = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    nb_affecte_min = Column(Integer)
    nb_affecte_max = Column(Integer)
    nb_realisation = Column(Integer)
    nb_realisation_avant_11 = Column(Integer)
    saison = relationship(TSaisons)
    espece = relationship(TEspeces)
    zone_cynegetique = relationship(TZoneCynegetiques)
    zone_indicative = relationship(TZoneIndicatives)
    secteur = relationship(TSecteurs)


@serializable
class TTypeBracelets(CustomModel):
    __tablename__ = "t_type_bracelets"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_type_bracelet = Column(Integer, primary_key=True)
    id_espece = Column(Integer, ForeignKey("oeasc_commons.t_especes.id_espece"))
    espece = relationship(TEspeces, foreign_keys=id_espece)
    code_type_bracelet = Column(Unicode)
    description_type_bracelet = Column(Unicode)


@serializable
class TAttributions(CustomModel):
    __tablename__ = "t_attributions"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_attribution = Column(Integer, primary_key=True)
    id_type_bracelet = Column(
        Integer, ForeignKey("oeasc_chasse.t_type_bracelets.id_type_bracelet")
    )
    id_saison = Column(Integer, ForeignKey("oeasc_chasse.t_saisons.id_saison"))
    numero_bracelet = Column(Unicode)
    id_zone_cynegetique_affectee = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    id_zone_indicative_affectee = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    meta_create_date = Column(DateTime)
    meta_update_date = Column(DateTime)
    saison = relationship(TSaisons)
    zone_cynegetique_affectee = relationship(TZoneCynegetiques)
    zone_indicative_affectee = relationship(TZoneIndicatives)
    type_bracelet = relationship(TTypeBracelets)


@serializable
class TRealisationsChasse(CustomModel):
    __tablename__ = "t_realisations"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_realisation = Column(Integer, primary_key=True)
    id_attribution = Column(
        Integer, ForeignKey("oeasc_chasse.t_attributions.id_attribution")
    )
    attribution = relationship(TAttributions)
    saison = relationship(
        TSaisons,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_saison==TSaisons.id_saison",
        uselist=False,
        viewonly=True,
    )
    id_auteur_tir = Column(Integer, ForeignKey("oeasc_chasse.t_personnes.id_personne"))
    auteur_tir = relationship(TPersonnes, foreign_keys=id_auteur_tir)
    id_auteur_constat = Column(
        Integer, ForeignKey("oeasc_chasse.t_personnes.id_personne")
    )
    auteur_constat = relationship(TPersonnes, foreign_keys=id_auteur_constat)
    id_zone_cynegetique_realisee = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique")
    )
    zone_cynegetique_realisee = relationship(TZoneCynegetiques)
    zone_cynegetique_affectee = relationship(
        TZoneCynegetiques,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_cynegetique_affectee==TZoneCynegetiques.id_zone_cynegetique",
        uselist=False,
        viewonly=True,
    )
    id_zone_indicative_realisee = Column(
        Integer, ForeignKey("oeasc_chasse.t_zone_indicatives.id_zone_indicative")
    )
    zone_indicative_realisee = relationship(TZoneIndicatives)
    zone_indicative_affectee = relationship(
        TZoneIndicatives,
        secondary="oeasc_chasse.t_attributions",
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_indicative_affectee==TZoneIndicatives.id_zone_indicative",
        uselist=False,
        viewonly=True,
    )
    id_lieu_tir_synonyme = Column(
        Integer, ForeignKey("oeasc_chasse.t_lieu_tir_synonymes.id_lieu_tir_synonyme")
    )
    lieu_tir_synonyme = relationship(TLieuTirSynonymes)
    date_exacte = Column(Date)
    date_enreg = Column(Date)
    mortalite_hors_pc = Column(Boolean)
    parcelle_onf = Column(Boolean)
    id_nomenclature_sexe = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_sexe = relationship(TNomenclatures_oeasc, foreign_keys=id_nomenclature_sexe)
    id_nomenclature_classe_age = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_classe_age = relationship(
        TNomenclatures_oeasc, foreign_keys=id_nomenclature_classe_age
    )
    poid_entier = Column(Float)
    poid_vide = Column(Float)
    poid_c_f_p = Column(Float)
    long_dagues_droite = Column(Integer)
    long_dagues_gauche = Column(Integer)
    long_mandibules_droite = Column(Integer)
    long_mandibules_gauche = Column(Integer)
    cors_nb = Column(Integer)
    cors_commentaires = Column(Unicode)
    gestation = Column(Boolean)
    id_nomenclature_mode_chasse = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_mode_chasse = relationship(
        TNomenclatures_oeasc, foreign_keys=id_nomenclature_mode_chasse
    )
    commentaire = Column(Unicode)



# Définition de la propriété de colonne après les définitions de classes pour éviter les références circulaires
TAttributions.has_realisation = column_property(
    exists().where(TRealisationsChasse.id_attribution == TAttributions.id_attribution)
)

# Cette ligne semble redondante car TAttributions est déjà décorée avec @serializable
# TAttributions = serializable(TAttributions)


@serializable
class VChasseBilan(CustomModel):
    __tablename__ = "v_bilan_pretty"
    __table_args__ = {"schema": "oeasc_chasse", "extend_existing": True}

    id_espece = Column(Integer, primary_key=True)
    id_zone_cynegetique = Column(Integer, primary_key=True)
    id_zone_indicative = Column(Integer, primary_key=True)
    id_saison = Column(Integer, primary_key=True)
    nom_saison = Column(Unicode)
    nom_zone_indicative = Column(Unicode)
    nom_zone_cynegetique = Column(Unicode)
    nom_espece = Column(Unicode)
    nb_affecte_max = Column(Integer)
    nb_affecte_min = Column(Integer)
    nb_realise = Column(Integer)
    nb_realise_avant_11 = Column(Integer)
