'''
    modele chasse
'''

from flask import current_app
from utils_flask_sqla.serializers import serializable
from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property
from sqlalchemy import select, func, and_
from ..commons.models import TEspeces

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
    id_espece = DB.Column(DB.Integer, DB.ForeignKey('oeasc_commons.t_especes.id_espece'))
    date_debut = DB.Column(DB.Date)
    date_fin = DB.Column(DB.Date)
    id_nomenclature_type_chasse = DB.Column(DB.Integer)

    


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


@serializable
class TTypeBracelets(DB.Model):
    '''
        Type de bracelet
    '''

    __tablename__ = 't_type_bracelets'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_type_bracelet = DB.Column(DB.Integer, primary_key=True)
    id_espece = DB.Column(DB.Integer, DB.ForeignKey('oeasc_commons.t_especes.id_espece'))
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

    label = column_property(
        select(
            [
                func.concat(
                    TSaisons.nom_saison,
                    '  ',
                    TEspeces.nom_espece,
                    '  ',
                    numero_bracelet,
                )
            ]).\
            where(
                and_(
                    TTypeBracelets.id_type_bracelet == id_type_bracelet,
                    TEspeces.id_espece == TTypeBracelets.id_espece,
                    TSaisons.id_saison == id_saison
                )
        )
    )



@serializable
class TRealisations(DB.Model):
    '''
        Realisations
    '''

    __tablename__ = 't_realisations'
    __table_args__ = {'schema': 'oeasc_chasse', 'extend_existing': True}

    id_realisation = DB.Column(DB.Integer, primary_key = True)
    id_attribution = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_attributions.id_attribution'), primary_key=True)
    id_zone_cynegetique_realisee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_cynegetiques.id_zone_cynegetique'))
    id_zone_interet_realisee = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_zone_interets.id_zone_interet'))
    id_lieu_tir = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_lieu_tirs.id_lieu_tir'))

    date_exacte = DB.Column(DB.Date)
    date_enreg = DB.Column(DB.Date)

    mortalite_hors_pc = DB.Column(DB.Boolean)

    id_auteur_tir = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_personnes.id_personne'))
    id_auteur_constat = DB.Column(DB.Integer, DB.ForeignKey('oeasc_chasse.t_personnes.id_personne'))

    auteur_tir = DB.relationship(TPersonnes, primaryjoin=TPersonnes.id_personne == id_auteur_tir)
    auteur_constat = DB.relationship(TPersonnes, primaryjoin=TPersonnes.id_personne == id_auteur_constat)

    id_nomenclature_sexe = DB.Column(DB.Integer)
    id_nomenclature_classe_age = DB.Column(DB.Integer)

    poid_entier = DB.Column(DB.Integer)
    poid_vide = DB.Column(DB.Integer)
    poid_c_f_p = DB.Column(DB.Integer)

    long_dagues_droite = DB.Column(DB.Integer)
    long_dagues_gauche = DB.Column(DB.Integer)
    long_mandibules_droite = DB.Column(DB.Integer)
    long_mandibules_gauche = DB.Column(DB.Integer)

    cors_nb = DB.Column(DB.Integer)
    cors_commentaires = DB.Column(DB.Unicode)

    gestation = DB.Column(DB.Boolean)
    id_nomenclature_mode_chasse = DB.Column(DB.Integer)
    commentaire = DB.Column(DB.Unicode)

    parcelle_onf = DB.Column(DB.Boolean)
    poid_indique = DB.Column(DB.Boolean)
    cors_indetermine = DB.Column(DB.Boolean)
    long_mandibule_indetermine = DB.Column(DB.Boolean)

    id_numerisateur = DB.Column(DB.Integer)

    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    attribution = DB.relationship(TAttributions)

    id_zone_cynegetique_affectee = column_property(
        select([TAttributions.id_zone_cynegetique_affectee]).\
            where(TAttributions.id_attribution == id_attribution)
    )

    id_zone_interet_affectee = column_property(
        select([TAttributions.id_zone_interet_affectee]).\
            where(TAttributions.id_attribution == id_attribution)
    )

