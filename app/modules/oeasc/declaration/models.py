'''
    modeles alerte OEASC
'''
from flask import current_app

from pypnusershub.db.models import User

from utils_flask_sql    a.serializers import serializable

config = current_app.config
DB = config['DB']


@serializable
class CorAreasDeclaration(DB.Model):
    '''
        areas localisation
    '''
    __tablename__ = 'cor_areas_declarations'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )
    id_area = DB.Column(DB.Integer, primary_key=True)

    def __init__(self, id_area=None):

        super(CorAreasDeclaration, self).__init__()
        self.id_area = id_area


@serializable
class CorAreasForet(DB.Model):
    '''
        areas foret
    '''

    __tablename__ = 'cor_areas_forets'
    __table_args__ = {'schema': 'oeasc_forets', 'extend_existing': True}

    id_area = DB.Column(DB.Integer, primary_key=True)
    id_foret = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_forets.t_forets.id_foret'),
        primary_key=True
    )

    def __init__(self, id_area=None):

        super(CorAreasForet, self).__init__()
        self.id_area = id_area


@serializable
class CorNomenclatureDeclarationEssenceSecondaire(DB.Model):
    '''
        nomenclatures essences secondaires
    '''

    __tablename__ = 'cor_nomenclature_declarations_essence_secondaire'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationEssenceSecondaire, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationEssenceComplementaire(DB.Model):
    '''
        nomenclatures essences complementaires
    '''

    __tablename__ = 'cor_nomenclature_declarations_essence_complementaire'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationEssenceComplementaire, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationMaturite(DB.Model):
    '''
        nomenclatures peuplement maturite
    '''

    __tablename__ = 'cor_nomenclature_declarations_maturite'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationMaturite, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationOrigine(DB.Model):
    '''
        nomenclatures peuplement origine
    '''

    __tablename__ = 'cor_nomenclature_declarations_origine'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationOrigine, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationProtectionType(DB.Model):
    '''
        nomenclatures protection type
    '''

    __tablename__ = 'cor_nomenclature_declarations_protection_type'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationProtectionType, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationPaturageType(DB.Model):
    '''
        nomenclatures paturage type
    '''

    __tablename__ = 'cor_nomenclature_declarations_paturage_type'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationPaturageType, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationPaturageSaison(DB.Model):
    '''
        nomenclatures paturage saison
    '''

    __tablename__ = 'cor_nomenclature_declarations_paturage_saison'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationPaturageSaison, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationEspece(DB.Model):
    '''
        nomenclatures especes
    '''

    __tablename__ = 'cor_nomenclature_declarations_espece'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration'),
        primary_key=True
    )

    def __init__(self, id_nomenclature=None):

        super(CorNomenclatureDeclarationEspece, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class TProprietaire(DB.Model):
    '''
        modeles proprietaires
    '''
    __tablename__ = 't_proprietaires'
    __table_args__ = {'schema': 'oeasc_forets', 'extend_existing': True}

    id_proprietaire = DB.Column(DB.Integer, primary_key=True)

    id_declarant = DB.Column(DB.Integer)

    nom_proprietaire = DB.Column(DB.String(250))
    telephone = DB.Column(DB.String(20))
    email = DB.Column(DB.String(250))
    adresse = DB.Column(DB.String(250))
    s_code_postal = DB.Column(DB.String(10))
    s_commune_proprietaire = DB.Column(DB.String(100))

    id_nomenclature_proprietaire_type = DB.Column(DB.Integer)


@serializable
class TForet(DB.Model):
    '''
        modele foret
    '''
    __tablename__ = 't_forets'
    __table_args__ = {'schema': 'oeasc_forets', 'extend_existing': True}

    id_foret = DB.Column(DB.Integer, primary_key=True)

    id_proprietaire = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_forets.t_proprietaires.id_proprietaire')
    )

    b_statut_public = DB.Column(DB.Boolean)
    b_document = DB.Column(DB.Boolean)

    nom_foret = DB.Column(DB.String(250))
    code_foret = DB.Column(DB.String(250))
    label_foret = DB.Column(DB.String(250))

    surface_calculee = DB.Column(DB.Float)
    surface_renseignee = DB.Column(DB.Float)

    areas_foret = DB.relationship(
        CorAreasForet,
        cascade="save-update, merge, delete, delete-orphan"
    )


@serializable
class TDegatEssence(DB.Model):
    '''
        modele degat essence
    '''
    __tablename__ = 't_degat_essences'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_degat_essence = DB.Column(DB.Integer, primary_key=True)

    id_nomenclature_degat_essence = DB.Column(DB.Integer)
    id_nomenclature_degat_etendue = DB.Column(DB.Integer)
    id_nomenclature_degat_gravite = DB.Column(DB.Integer)
    id_nomenclature_degat_anteriorite = DB.Column(DB.Integer)

    id_degat = DB.Column(DB.Integer, DB.ForeignKey('oeasc_declarations.t_degats.id_degat'))


@serializable
class TDegat(DB.Model):
    '''
        modele degat
    '''
    __tablename__ = 't_degats'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_degat = DB.Column(DB.Integer, primary_key=True)

    id_nomenclature_degat_type = DB.Column(DB.Integer)

    id_declaration = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_declarations.t_declarations.id_declaration')
    )

    degat_essences = DB.relationship(
        TDegatEssence,
        cascade="save-update, merge, delete, delete-orphan"
    )


@serializable
class TDeclaration(DB.Model):
    '''
        modele declaration
    '''
    __tablename__ = 't_declarations'
    __table_args__ = {'schema': 'oeasc_declarations', 'extend_existing': True}

    id_declaration = DB.Column(DB.Integer, primary_key=True)

    id_declarant = DB.Column(DB.Integer, DB.ForeignKey(User.id_role))

    id_nomenclature_proprietaire_declarant = DB.Column(DB.Integer)

    id_foret = DB.Column(DB.Integer, DB.ForeignKey('oeasc_forets.t_forets.id_foret'))

    id_nomenclature_peuplement_origine = DB.Column(DB.Integer)
    id_nomenclature_peuplement_type = DB.Column(DB.Integer)
    id_nomenclature_peuplement_paturage_frequence = DB.Column(DB.Integer)
    id_nomenclature_peuplement_paturage_statut = DB.Column(DB.Integer)
    id_nomenclature_peuplement_acces = DB.Column(DB.Integer)
    id_nomenclature_peuplement_essence_principale = DB.Column(DB.Integer)

    b_peuplement_protection_existence = DB.Column(DB.Boolean)
    b_peuplement_paturage_presence = DB.Column(DB.Boolean)
    b_autorisation = DB.Column(DB.Boolean)
    b_valid = DB.Column(DB.Boolean)

    areas_localisation = DB.relationship(
        CorAreasDeclaration,
        cascade="save-update, merge, delete, delete-orphan"
        )

    nomenclatures_peuplement_essence_secondaire = DB.relationship(
        CorNomenclatureDeclarationEssenceSecondaire,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_essence_complementaire = DB.relationship(
        CorNomenclatureDeclarationEssenceComplementaire,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_maturite = DB.relationship(
        CorNomenclatureDeclarationMaturite,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_protection_type = DB.relationship(
        CorNomenclatureDeclarationProtectionType,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_paturage_type = DB.relationship(
        CorNomenclatureDeclarationPaturageType,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_paturage_saison = DB.relationship(
        CorNomenclatureDeclarationPaturageSaison,
        cascade="save-update, merge, delete, delete-orphan"
    )
    nomenclatures_peuplement_espece = DB.relationship(
        CorNomenclatureDeclarationEspece,
        cascade="save-update, merge, delete, delete-orphan"
    )

    nomenclatures_peuplement_origine2 = DB.relationship(
        CorNomenclatureDeclarationOrigine,
        cascade="save-update, merge, delete, delete-orphan"
    )


    peuplement_surface = DB.Column(DB.Float)

    degats = DB.relationship(TDegat, cascade="save-update, merge, delete, delete-orphan")

    autre_protection = DB.Column(DB.Text)
    precision_localisation = DB.Column(DB.Text)
    commentaire = DB.Column(DB.Text)

    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)
