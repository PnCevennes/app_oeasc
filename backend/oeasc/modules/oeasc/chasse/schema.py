"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested, fields

# from utils_flask_sqla.schema import SmartRelationshipsMixin
from utils_flask_sqla_geo.schema import GeometryField
from utils_flask_sqla_geo.schema import GeoAlchemyAutoSchema
from marshmallow import EXCLUDE
from .models import *
from marshmallow import pre_load

config = current_app.config
DB = config["DB"]


class TZoneCynegetiquesSchema(SQLAlchemyAutoSchema):
    id_zone_cynegetique = fields.Integer(allow_none=True)

    class Meta:
        model = TZoneCynegetiques
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    secteur = Nested(
        "TSecteursSchema", many=False, dump_only=False, exclude=("circuits",)
    )


class TZoneIndicativesSchema(GeoAlchemyAutoSchema):
    id_zone_indicative = fields.Integer(allow_none=True)

    class Meta:
        model = TZoneIndicatives
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus
        # dump_only = ("id_zone_indicative",)  # éviter toute écriture
        # model_converter = SyntheseConverter

    geom = GeometryField(dump_only=True)

    zone_cynegetique = Nested(
        "TZoneCynegetiquesSchema", many=False, exclude=("secteur",)
    )


class TLieuTirsSchema(GeoAlchemyAutoSchema):
    id_lieu_tir = fields.Integer(allow_none=True)

    class Meta:
        model = TLieuTirs
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus
        # model_converter = SyntheseConverter

    geom = GeometryField(dump_only=True)
    zone_indicative = Nested(
        "TZoneIndicativesSchema",
        many=False,
        # metadata={"load_instance": True},
    )


class TLieuTirSynonymesSchema(SQLAlchemyAutoSchema):
    id_lieu_tir_synonyme = fields.Integer(allow_none=True)

    class Meta:
        model = TLieuTirSynonymes
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    lieu_tir = Nested("TLieuTirsSchema", many=False)
    lieu_tir_synonyme_display = fields.String(
        attribute="lieu_tir_synonyme_display", dump_only=True
    )


class TSaisonsSchema(SQLAlchemyAutoSchema):
    id_saison = fields.Integer(allow_none=True)

    class Meta:
        model = TSaisons
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TSaisonDatesSchema(SQLAlchemyAutoSchema):
    id_saison_date = fields.Integer(allow_none=True)

    class Meta:
        model = TSaisonDates
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    saison = Nested("TSaisonsSchema", many=False)
    espece = Nested("TEspecesSchema", many=False)
    nomenclature_type_chasse = Nested(
        "TNomenclaturesOeascSchema",
        many=False,
        only=(
            "id_nomenclature",
            "id_type",
            "cd_nomenclature",
            "mnemonique",
            "label_fr",
            "definition_default",
        ),
        allow_none=True,
        metadata={"load_instance": False},
        unknown=EXCLUDE,  # retire du schema les champs inconnus ou superflus
    )


class TAttributionMassifsSchema(SQLAlchemyAutoSchema):
    id_attribution_massif = fields.Integer(allow_none=True)

    class Meta:
        model = TAttributionMassifs
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    saison = Nested("TSaisonsSchema", many=False)
    espece = Nested("TEspecesSchema", many=False)
    zone_cynegetique = Nested("TZoneCynegetiquesSchema", many=False)


class VPlanChasseRealisationBilanSchema(SQLAlchemyAutoSchema):
    # id_attribution_massif = fields.Integer(dump_only=True)
    class Meta:
        model = VPlanChasseRealisationBilan
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    saison = Nested("TSaisonsSchema", many=False, metadata={"load_instance": True})
    espece = Nested("TEspecesSchema", many=False, metadata={"load_instance": True})
    zone_cynegetique = Nested(
        "TZoneCynegetiquesSchema", many=False, metadata={"load_instance": True}
    )
    zone_indicative = Nested(
        "TZoneIndicativesSchema", many=False, metadata={"load_instance": True}
    )
    secteur = Nested("TSecteursSchema", many=False, metadata={"load_instance": True})


class TTypeBraceletsSchema(SQLAlchemyAutoSchema):
    id_type_bracelet = fields.Integer(allow_none=True)

    class Meta:
        model = TTypeBracelets
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    espece = Nested(
        "TEspecesSchema",
        many=False,
    )


class TAttributionsSchema(SQLAlchemyAutoSchema):
    id_attribution = fields.Integer(allow_none=True)

    class Meta:
        model = TAttributions
        load_instance = True
        include_fk = True
        include_relationships = False
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    realisation = Nested(
        "TRealisationsChasseSchema",
        many=False,
        allow_none=True,
        exclude=(
            "attribution",
            "saison",
            "zone_cynegetique_affectee",
            "zone_indicative_affectee",
        ),
        metadata={
            "load_instance": True,
        },
    )

    saison = Nested("TSaisonsSchema", many=False, exclude=("commentaire",))
    zone_cynegetique_affectee = Nested(
        "TZoneCynegetiquesSchema", many=False, exclude=("secteur",)
    )
    zone_indicative_affectee = Nested(
        "TZoneIndicativesSchema", many=False, exclude=("zone_cynegetique",)
    )
    type_bracelet = Nested("TTypeBraceletsSchema", many=False)
    # has_realisation = fields.Boolean(attribute="has_realisation")
    id_realisation = fields.Integer(attribute="id_realisation", dump_only=True)


class TRealisationsChasseSchema(GeoAlchemyAutoSchema):
    id_realisation = fields.Integer(allow_none=True)

    class Meta:
        model = TRealisationsChasse
        load_instance = True
        include_fk = True
        include_relationships = False
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    def get_zone_indicative_realisee(self, obj):
        if obj.zone_indicative_realisee:
            return {
                "id_zone_indicative": obj.zone_indicative_realisee.id_zone_indicative,
                "code_zone_indicative": obj.zone_indicative_realisee.code_zone_indicative,
                "nom_zone_indicative": obj.zone_indicative_realisee.nom_zone_indicative,
                "id_zone_cynegetique": obj.zone_indicative_realisee.id_zone_cynegetique,
                "zone_cynegetique": {
                    "id_zone_cynegetique": obj.zone_indicative_realisee.zone_cynegetique.id_zone_cynegetique,
                    "nom_zone_cynegetique": obj.zone_indicative_realisee.zone_cynegetique.nom_zone_cynegetique,
                },
                "geom": obj.zone_indicative_realisee.geom,
            }
        return None

    attribution = Nested(
        "TAttributionsSchema",
        many=False,
        exclude=(
            "realisation",
            "zone_cynegetique_affectee",
            "zone_indicative_affectee",
            "saison",
        ),
        metadata={"load_instance": True},
    )
    saison = Nested(
        "TSaisonsSchema",
        many=False,
        metadata={"load_instance": True},
    )

    zone_cynegetique_realisee = Nested(
        "TZoneCynegetiquesSchema",
        many=False,
        metadata={"load_instance": True},
        exclude=("secteur",),
        # dump_only=True,  # Empêche la désérialisation, donc pas de création lors du load
    )
    zone_cynegetique_affectee = Nested(
        "TZoneCynegetiquesSchema",
        many=False,
        metadata={"load_instance": True},
        exclude=("secteur",),
        # dump_only=True,  # Empêche la désérialisation, donc pas de création lors du load
    )
    id_zone_indicative_realisee = fields.Integer()

    # 🔍 Lecture uniquement — on évite les nested write
    # zone_indicative_realisee = fields.Method("get_zone_indicative_realisee")

    zone_indicative_realisee = Nested(
        "TZoneIndicativesSchema",
        many=False,
        metadata={"load_instance": True},
        exclude=("zone_cynegetique",),
        # dump_only=True,  # Empêche la désérialisation, donc pas de création lors du load
    )

    zone_indicative_affectee = Nested(
        "TZoneIndicativesSchema",
        many=False,
        metadata={"load_instance": True},
        exclude=("zone_cynegetique",),
        # dump_only=True,  # Empêche la désérialisation, donc pas de création lors du load
    )
    lieu_tir_synonyme = Nested(
        "TLieuTirSynonymesSchema",
        many=False,
        allow_none=True,
        metadata={"load_instance": True},
    )
    nomenclature_sexe = Nested(
        "TNomenclaturesOeascSchema",
        many=False,
        allow_none=True,
        only=(
            "id_nomenclature",
            "id_type",
            "cd_nomenclature",
            "mnemonique",
            "label_fr",
            "definition_default",
        ),
        metadata={"load_instance": True},
    )
    nomenclature_classe_age = Nested(
        "TNomenclaturesOeascSchema",
        many=False,
        only=(
            "id_nomenclature",
            "id_type",
            "cd_nomenclature",
            "mnemonique",
            "label_fr",
            "definition_default",
        ),
        metadata={"load_instance": True},
    )
    nomenclature_mode_chasse = Nested(
        "TNomenclaturesOeascSchema",
        many=False,
        only=(
            "id_nomenclature",
            "id_type",
            "cd_nomenclature",
            "mnemonique",
            "label_fr",
            "definition_default",
        ),
        metadata={"load_instance": True},
    )


class VChasseBilanSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VChasseBilan
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus
