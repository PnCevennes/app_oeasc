"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested, fields
from marshmallow import EXCLUDE
from .models import *

config = current_app.config
DB = config["DB"]


class CorAreasDeclarationSchema(SQLAlchemyAutoSchema):
    id_declaration = fields.Integer(allow_none=True)
    id_area = fields.Integer(allow_none=True)

    class Meta:
        model = CorAreasDeclaration
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationEssenceSecondaireSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationEssenceSecondaire
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationEssenceComplementaireSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationEssenceComplementaire
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationMaturiteSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationMaturite
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationOrigineSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationOrigine
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationProtectionTypeSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationProtectionType
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationPaturageTypeSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationPaturageType
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationPaturageSaisonSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationPaturageSaison
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class CorNomenclatureDeclarationEspeceSchema(SQLAlchemyAutoSchema):
    id_nomenclature = fields.Integer(allow_none=True)
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = CorNomenclatureDeclarationEspece
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TDegatEssenceSchema(SQLAlchemyAutoSchema):
    id_degat_essence = fields.Integer(allow_none=True)

    class Meta:
        model = TDegatEssence
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TDegatSchema(SQLAlchemyAutoSchema):
    id_degat = fields.Integer(allow_none=True)
    degat_essences = Nested(
        TDegatEssenceSchema,
        many=True,
        # exclude=("id_degat",),
    )

    class Meta:
        model = TDegat
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TDeclarationSchema(SQLAlchemyAutoSchema):
    id_declaration = fields.Integer(allow_none=True)
    areas_localisation = Nested(
        CorAreasDeclarationSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_essence_secondaire = Nested(
        CorNomenclatureDeclarationEssenceSecondaireSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_essence_complementaire = Nested(
        CorNomenclatureDeclarationEssenceComplementaireSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_maturite = Nested(
        CorNomenclatureDeclarationMaturiteSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_protection_type = Nested(
        CorNomenclatureDeclarationProtectionTypeSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_paturage_type = Nested(
        CorNomenclatureDeclarationPaturageTypeSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_paturage_saison = Nested(
        CorNomenclatureDeclarationPaturageSaisonSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_espece = Nested(
        CorNomenclatureDeclarationEspeceSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    nomenclatures_peuplement_origine2 = Nested(
        CorNomenclatureDeclarationOrigineSchema,
        many=True,
        metadata={"load_instance": True},
        # exclude=("id_declaration",),
    )
    degats = Nested(TDegatSchema, many=True, metadata={"load_instance": True})

    class Meta:
        model = TDeclaration
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


################################################################
############ TABLES DU SCHEMAS OEASC_FORETS ############
################################################################


class CorAreasForetSchema(SQLAlchemyAutoSchema):
    id_area = fields.Integer(allow_none=True)
    id_foret = fields.Integer(allow_none=True)

    class Meta:
        model = CorAreasForet
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE


class CorDgdCadastreSchema(SQLAlchemyAutoSchema):
    area_code_dgd = fields.String(allow_none=True)
    area_code_cadastre = fields.String(allow_none=True)

    class Meta:
        model = CorDgdCadastre
        load_instance = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE


class TProprietaireSchema(SQLAlchemyAutoSchema):
    id_proprietaire = fields.Integer(allow_none=True)

    class Meta:
        model = TProprietaire
        load_instance = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE


class TForetSchema(SQLAlchemyAutoSchema):
    id_foret = fields.Integer(allow_none=True)
    areas_foret = Nested(
        CorAreasForetSchema, many=True, metadata={"include_fk": True}, unknown=EXCLUDE
    )

    class Meta:
        model = TForet
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE
