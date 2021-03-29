'''
    modele chasse
'''

from flask import current_app
from utils_flask_sqla.serializers import serializable
from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property
from sqlalchemy import select, func, and_
from ..commons.models import TEspeces, TNomenclatures, TSecteurs   

config = current_app.config
DB = config['DB']


@serializable
class TPersonnes(DB.Model):
    '''
        Personne (tir & constat)
    '''
    __tablename__ = 't_personnes'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_personne = DB.Column(DB.Integer, primary_key=True)
    nom_personne = DB.Column(DB.Unicode)


@serializable
class TZoneCynegetiques(DB.Model):
    '''
        Zones Cynegetiques
    '''
    __tablename__ = 't_zone_cynegetiques'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_zone_cynegetique = DB.Column(DB.Integer, primary_key=True)
    code_zone_cynegetique = DB.Column(DB.Unicode)
    nom_zone_cynegetique = DB.Column(DB.Unicode)
    id_secteur = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_commons.t_secteurs.id_secteur')
    )
    secteur = DB.relationship(TSecteurs, foreign_keys=id_secteur)


@serializable
class TZoneInterets(DB.Model):
    '''
        Zones d'interet cynegetiques
    '''
    __tablename__ = 't_zone_interets'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_zone_interet = DB.Column(DB.Integer, primary_key=True)
    code_zone_interet = DB.Column(DB.Unicode)
    nom_zone_interet = DB.Column(DB.Unicode)
    id_zone_cynegetique = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique')
    )
    zone_cynegetique = DB.relationship(TZoneCynegetiques, foreign_keys=id_zone_cynegetique)

@serializable
class TLieuTirs(DB.Model):
    '''
        Lieu de tir
    '''
    __tablename__ = 't_lieu_tirs'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_lieu_tir = DB.Column(DB.Integer, primary_key=True)
    code_lieu_tir = DB.Column(DB.Unicode)
    nom_lieu_tir = DB.Column(DB.Unicode)
    geom = DB.Column(Geometry)
    id_area_commune = DB.Column(DB.Integer, DB.ForeignKey('ref_geo.l_areas.id_area'))
    id_zone_interet = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_chasse.t_zone_interets.id_zone_interet')
    )
    zone_interet = DB.relationship(TZoneInterets, foreign_keys=id_zone_interet)


@serializable
class TSaisons(DB.Model):
    '''
        Saison de chasse
    '''

    __tablename__ = 't_saisons'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_saison = DB.Column(DB.Integer, primary_key=True)
    nom_saison = DB.Column(DB.Unicode)
    date_debut = DB.Column(DB.Date)
    date_fin = DB.Column(DB.Date)
    current = DB.Column(DB.Boolean)
    commentaire = DB.Column(DB.Unicode)

@serializable
class TSaisonDates(DB.Model):
    '''
        Date de chasse des différentes especes
    '''

    __tablename__ = 't_saison_dates'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_saison_date = DB.Column(DB.Integer, primary_key=True)
    id_saison = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_saisons.id_saison'))
    saison = DB.relationship(TSaisons, foreign_keys=id_saison)
    id_espece = DB.Column(DB.Integer, DB.ForeignKey('oeasc_commons.t_especes.id_espece'))
    espece = DB.relationship(TEspeces, foreign_keys=id_espece)
    date_debut = DB.Column(DB.Date)
    date_fin = DB.Column(DB.Date)
    id_nomenclature_type_chasse = DB.Column(DB.Integer, DB.ForeignKey('ref_nomenclatures.t_nomenclatures.id_nomenclature'))
    nomenclature_type_chasse = DB.relationship(TNomenclatures, foreign_keys=id_nomenclature_type_chasse)
    


@serializable
class TAttributionMassifs(DB.Model):
    '''
        Attribution selon les années
    '''

    __tablename__ = 't_attribution_massifs'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_attribution_massif = DB.Column(DB.Integer, primary_key=True)
    id_saison = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_saisons.id_saison'))
    id_espece = DB.Column(DB.Integer, DB.ForeignKey('oeasc_commons.t_especes.id_espece'))
    id_zone_cynegetique = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique'))
    nb_affecte_min = DB.Column(DB.Integer)
    nb_affecte_max = DB.Column(DB.Integer)

    saison = DB.relationship(TSaisons)
    espece = DB.relationship(TEspeces)
    zone_cynegetique = DB.relationship(TZoneCynegetiques)



@serializable
class TTypeBracelets(DB.Model):
    '''
        Type de bracelet
    '''

    __tablename__ = 't_type_bracelets'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_type_bracelet = DB.Column(DB.Integer, primary_key=True)
    id_espece = DB.Column(DB.Integer, DB.ForeignKey('oeasc_commons.t_especes.id_espece'))
    espece = DB.relationship(TEspeces, foreign_keys=id_espece)
    code_type_bracelet = DB.Column(DB.Unicode)
    description_type_bracelet = DB.Column(DB.Unicode)


@serializable
class TAttributions(DB.Model):
    '''
        Attributions
    '''

    __tablename__ = 't_attributions'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_attribution = DB.Column(DB.Integer, primary_key=True)
    id_type_bracelet = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_type_bracelets.id_type_bracelet'))
    id_saison = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_saisons.id_saison'))
    numero_bracelet = DB.Column(DB.Unicode)
    id_zone_cynegetique_affectee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique'))
    id_zone_interet_affectee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_interets.id_zone_interet'))
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    saison = DB.relationship(TSaisons)
    zone_cynegetique_affectee = DB.relationship(TZoneCynegetiques)
    zone_interet_affectee = DB.relationship(TZoneInterets)
    type_bracelet = DB.relationship(TTypeBracelets)



@serializable
class TRealisationsChasse(DB.Model):
    '''
        Realisations
    '''

    __tablename__ = 't_realisations'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_realisation = DB.Column(DB.Integer, primary_key = True)
    id_attribution = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_attributions.id_attribution'), primary_key=True)

    attribution = DB.relationship(TAttributions)
    saison = DB.relationship(
        TSaisons,
        secondary='oeasc_chasse.t_attributions',
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_saison==TSaisons.id_saison",
        uselist=False
    )

    id_auteur_tir = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_personnes.id_personne'))
    auteur_tir = DB.relationship(TPersonnes, foreign_keys=id_auteur_tir)

    id_auteur_constat = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_personnes.id_personne'))
    auteur_constat = DB.relationship(TPersonnes, foreign_keys=id_auteur_constat)


    id_zone_cynegetique_realisee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique'))
    zone_cynegetique_realisee = DB.relationship(TZoneCynegetiques)
    zone_cynegetique_affectee = DB.relationship(
        TZoneCynegetiques,
        secondary='oeasc_chasse.t_attributions',
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_cynegetique_affectee==TZoneCynegetiques.id_zone_cynegetique",
        uselist=False
    )

    id_zone_interet_realisee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_interets.id_zone_interet'))
    zone_interet_realisee = DB.relationship(TZoneInterets)
    zone_interet_affectee = DB.relationship(
        TZoneInterets,
        secondary='oeasc_chasse.t_attributions',
        primaryjoin="TAttributions.id_attribution==TRealisationsChasse.id_attribution",
        secondaryjoin="TAttributions.id_zone_interet_affectee==TZoneInterets.id_zone_interet",
        uselist=False
    )

    id_lieu_tir = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_lieu_tirs.id_lieu_tir'))
    lieu_tir = DB.relationship(TLieuTirs)

    date_exacte = DB.Column(DB.Date)
    date_enreg = DB.Column(DB.Date)

    mortalite_hors_pc = DB.Column(DB.Boolean)
    parcelle_onf = DB.Column(DB.Boolean)

    id_nomenclature_sexe = DB.Column(DB.Integer, DB.ForeignKey('ref_nomenclatures.t_nomenclatures.id_nomenclature'))
    nomenclature_sexe = DB.relationship(TNomenclatures, foreign_keys=id_nomenclature_sexe)

    id_nomenclature_classe_age = DB.Column(DB.Integer, DB.ForeignKey('ref_nomenclatures.t_nomenclatures.id_nomenclature'))
    nomenclature_classe_age = DB.relationship(TNomenclatures, foreign_keys=id_nomenclature_classe_age)

    poid_entier = DB.Column(DB.Integer)
    poid_vide = DB.Column(DB.Integer)
    poid_c_f_p = DB.Column(DB.Integer)

    # long_dagues_droite = DB.Column(DB.Integer)
    # long_dagues_gauche = DB.Column(DB.Integer)
    # long_mandibules_droite = DB.Column(DB.Integer)
    # long_mandibules_gauche = DB.Column(DB.Integer)

    # cors_nb = DB.Column(DB.Integer)
    # cors_commentaires = DB.Column(DB.Unicode)

    # gestation = DB.Column(DB.Boolean)
    # id_nomenclature_mode_chasse = DB.Column(DB.Integer)
    # commentaire = DB.Column(DB.Unicode)

    # poid_indique = DB.Column(DB.Boolean)
    # cors_indetermine = DB.Column(DB.Boolean)
    # long_mandibule_indetermine = DB.Column(DB.Boolean)

    # id_numerisateur = DB.Column(DB.Integer)

    # meta_create_date = DB.Column(DB.DateTime)
    # meta_update_date = DB.Column(DB.DateTime)

    # id_zone_cynegetique_affectee = column_property(
    #     select([TAttributions.id_zone_cynegetique_affectee]).\
    #         where(TAttributions.id_attribution == id_attribution)
    # )

    # id_zone_interet_affectee = column_property(
    #     select([TAttributions.id_zone_interet_affectee]).\
    #         where(TAttributions.id_attribution == id_attribution)
    # )

