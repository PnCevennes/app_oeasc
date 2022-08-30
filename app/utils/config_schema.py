"""
    Description des options de configuration
"""

import os

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
    MAIL_HOST = fields.String(missing="")
    HOST_PORT = fields.Integer(missing=465)
    MAIL_FROM = fields.String(missing="")
    MAIL_USERNAME = fields.String(missing="")
    MAIL_PASS = fields.String(missing="")
    MAIL_TO = fields.List(fields.String(), missing=list())


class OeascAdminInfo(Schema):
    ADMIN_APPLICATION_LOGIN = fields.String()
    ADMIN_APPLICATION_MAIL = fields.String()


class OeascGeneralSchemaConf(Schema):
    appName = fields.String(missing="oeasc")
    PASS_METHOD = fields.String(missing="hash", validate=OneOf(["hash", "md5"]))
    DEBUG = fields.Boolean(missing=False)
    URL_APPLICATION = fields.Url(required=True)
    URL_FRONTEND = fields.Url(required=True)
    URL_USERSHUB = fields.Url(required=True)

    # API_ENDPOINT = fields.Url(required=True)
    # API_TAXHUB = fields.Url(required=True)
    # LOCAL_SRID = fields.Integer(required=True, missing=2154)
    ID_APP = fields.Integer(required=True)

    MAIL_ON_ERROR = fields.Boolean(missing=False)
    ANIMATEUR_APPLICATION_MAIL = fields.String(missing="")
    ADMIN_APPLICATION_PASSWORD = fields.String()
    MAIL_CONFIG = fields.Nested(MailConf, load_default=MailConf().load({}))
    ADMIN_INFO = fields.Nested(OeascAdminInfo, missing=dict())
