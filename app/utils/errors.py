import logging

log = logging.getLogger(__name__)
"""
    Erreurs propres à l'oeasc
"""


class OeascError(Exception):
    pass


class ConfigError(OeascError):
    """
    Configuration error class
    Quand un fichier de configuration n'est pas conforme aux attentes
    """

    def __init__(self, file, value):
        self.value = value
        self.file = file

    def __str__(self):
        msg = "Error in the config file '{}'. Fix the following:\n"
        msg = msg.format(self.file)
        for key, errors in self.value.items():
            errors = "\n\t\t-".join(errors)
            msg += "\n\t{}:\n\t\t-{}".format(key, errors)
        return msg


class OeascApiError(Exception):
    def __init__(self, message, status_code=500):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        raised_error = self.__class__.__name__

    def to_dict(self):
        return {
            "message": self.message,
            "status_code": self.status_code,
            "raisedError": self.__class__.__name__,
        }

    def __str__(self):
        message = "Error {}, Message: {}, raised error: {}"
        return message.format(self.status_code, self.message, self.__class__.__name__)


class InsufficientRightsError(OeascApiError):
    pass


class AuthentificationError(OeascApiError):
    pass


class CasAuthentificationError(OeascApiError):
    pass
