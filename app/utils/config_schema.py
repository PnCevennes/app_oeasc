"""
    Description des options de configuration
"""

from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Regexp


class OeascPySchemaConf(Schema):
    SQLALCHEMY_DATABASE_URI = fields.String(
        required=True,
        validate=Regexp(
            "^postgresql:\/\/.*:.*@[^:]+:\w+\/\w+$",
            0,
            """Database uri is invalid ex:
             postgresql://monuser:monpass@server:port/db_name""",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = fields.Boolean(missing=False)
    SESSION_TYPE = fields.String(missing="filesystem")
    SECRET_KEY = fields.String(required=True)
    COOKIE_EXPIRATION = fields.Integer(missing=7200)
    COOKIE_AUTORENEW = fields.Boolean(missing=True)
    TRAP_ALL_EXCEPTIONS = fields.Boolean(missing=False)
    SENTRY_DSN = fields.String()


class MailConf(Schema):
    MAIL_SERVER = fields.String(required=False)
    MAIL_PORT = fields.Integer(required=False)
    MAIL_USE_TLS = fields.Boolean(required=False)
    MAIL_USE_SSL = fields.Boolean(required=False)
    MAIL_USERNAME = fields.String(required=False)
    MAIL_PASSWORD = fields.String(required=False)
    MAIL_DEFAULT_SENDER = fields.String(required=False)
    MAIL_MAX_EMAILS = fields.Integer(required=False)
    MAIL_SUPPRESS_SEND = fields.Boolean(required=False)
    MAIL_ASCII_ATTACHMENTS = fields.Boolean(required=False)
    # ERROR_MAIL_TO = EmailStrOrListOfEmailStrField(load_default=None)


class OeascGeneralSchemaConf(Schema):
    appName = fields.String(missing="oeasc")
    PASS_METHOD = fields.String(
        missing="hash",
        validate=OneOf(["hash", "md5"])
    )
    DEBUG = fields.Boolean(missing=False)
    URL_APPLICATION = fields.Url(required=True)
    URL_FRONTEND = fields.Url(required=True)
    URL_USERSHUB = fields.Url(required=True)

    ID_APP = fields.Integer(required=True)

    MAIL_ON_ERROR = fields.Boolean(missing=False)
    ANIMATEUR_APPLICATION_MAIL = fields.String(missing="")
    ADMIN_APPLICATION_PASSWORD = fields.String()
    ADMIN_APPLICATION_LOGIN = fields.String()
    ADMIN_APPLICATION_MAIL = fields.String()
    MAIL_CONFIG = fields.Nested(MailConf, load_default=MailConf().load({}))

    # Paramètre de pypnnomenclature
    ENABLE_NOMENCLATURE_TAXONOMIC_FILTERS = fields.Boolean(missing=True)
