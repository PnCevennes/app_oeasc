"""
Traduction des exceptions techniques (Marshmallow, SQLAlchemy, ...) en réponses JSON
compréhensibles par un utilisateur non technique.

Toutes les routes d'écriture génériques (POST / PATCH / DELETE) renvoient, en cas
d'erreur, un corps JSON de la forme :

    {
        "success": false,
        "message": "<phrase claire, sans jargon>",
        "field_errors": { "<nom_du_champ>": ["<explication>", ...] },
        "code": <code HTTP>
    }

Le front (App.vue / snackbar) se contente d'afficher `message` (et, si présent,
la liste des champs concernés en les traduisant via les libellés du formulaire).
Le détail technique n'est ajouté (clé `system_error`) qu'en mode développement.
"""

from flask import current_app
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError


def _report_to_sentry(exc):
    """Signale à Sentry une erreur réellement inattendue (5xx), si Sentry est actif."""
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exc)
    except Exception:
        pass


# --- Marshmallow : messages EN renvoyés par défaut -> formulation FR -----------
_MARSHMALLOW_FR = {
    "Missing data for required field.": "information obligatoire non renseignée",
    "Field may not be null.": "information obligatoire non renseignée",
    "Not a valid integer.": "un nombre entier est attendu",
    "Not a valid number.": "un nombre est attendu",
    "Not a valid string.": "un texte est attendu",
    "Not a valid boolean.": "une valeur « oui » ou « non » est attendue",
    "Not a valid date.": "une date valide est attendue",
    "Not a valid datetime.": "une date valide est attendue",
    "Not a valid email address.": "l'adresse e-mail n'est pas valide",
    "Not a valid URL.": "l'adresse (URL) n'est pas valide",
}


def _translate_marshmallow_message(message):
    if not isinstance(message, str):
        return str(message)
    return _MARSHMALLOW_FR.get(message, message)


def _flatten_marshmallow_errors(messages, prefix=""):
    """
    Transforme l'arbre d'erreurs Marshmallow ({champ: [msg] | {sous-champ: ...}})
    en dictionnaire plat {champ: ["msg fr", ...]}.
    """
    field_errors = {}
    if isinstance(messages, dict):
        for key, value in messages.items():
            key_str = str(key)
            new_prefix = f"{prefix}.{key_str}" if prefix else key_str
            field_errors.update(_flatten_marshmallow_errors(value, new_prefix))
    elif isinstance(messages, (list, tuple)):
        field_errors.setdefault(prefix or "_", [])
        for item in messages:
            if isinstance(item, (dict, list, tuple)):
                field_errors.update(_flatten_marshmallow_errors(item, prefix))
            else:
                field_errors[prefix or "_"].append(_translate_marshmallow_message(item))
    else:
        field_errors.setdefault(prefix or "_", []).append(
            _translate_marshmallow_message(messages)
        )
    return field_errors


def _pg_diag(exc):
    """Récupère (pgcode, nom_colonne, nom_contrainte) d'une IntegrityError psycopg2."""
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)
    column_name = None
    constraint_name = None
    diag = getattr(orig, "diag", None)
    if diag is not None:
        column_name = getattr(diag, "column_name", None)
        constraint_name = getattr(diag, "constraint_name", None)
    return pgcode, column_name, constraint_name


def build_error_payload(exc, action="enregistrement"):
    """
    Construit (payload_dict, status_code) à partir d'une exception.

    `action` : "enregistrement", "modification" ou "suppression" — utilisé pour
    formuler le message par défaut.
    """
    field_errors = {}

    # 1) Erreurs de validation (données manquantes / non conformes)
    if isinstance(exc, ValidationError):
        field_errors = _flatten_marshmallow_errors(exc.messages)
        message = (
            "Certaines informations saisies sont manquantes ou ne sont pas au bon "
            "format. Merci de vérifier les champs signalés puis de recommencer."
        )
        status = 400

    # 2) Objet introuvable (id inconnu lors d'une modification)
    elif isinstance(exc, ValueError):
        message = (
            "L'élément que vous essayez de modifier est introuvable. "
            "Il a peut-être été supprimé entre-temps : rechargez la page."
        )
        status = 404

    # 3) Violation de contrainte en base (doublon, champ obligatoire, lien...)
    elif isinstance(exc, IntegrityError):
        pgcode, column_name, constraint_name = _pg_diag(exc)
        status = 409
        if pgcode == "23505":  # unique_violation
            message = (
                "Un enregistrement avec ces mêmes valeurs existe déjà. "
                "Merci de modifier les informations qui doivent être uniques."
            )
        elif pgcode == "23502":  # not_null_violation
            if column_name:
                field_errors = {column_name: ["information obligatoire non renseignée"]}
            message = (
                "Une information obligatoire n'a pas été renseignée. "
                "Merci de compléter tous les champs requis."
            )
            status = 400
        elif pgcode == "23503":  # foreign_key_violation
            if action == "suppression":
                message = (
                    "Cet élément est utilisé ailleurs dans l'application : "
                    "il ne peut pas être supprimé tant qu'il est rattaché à d'autres données."
                )
            else:
                message = (
                    "Une des valeurs sélectionnées n'existe pas (ou plus) "
                    "dans la liste de référence. Merci de rafraîchir la page et de recommencer."
                )
        elif pgcode == "23514":  # check_violation
            message = (
                "Une des valeurs saisies n'est pas autorisée. "
                "Merci de vérifier les informations du formulaire."
            )
            status = 400
        else:
            message = (
                "L'opération n'a pas pu être réalisée car elle entre en conflit "
                "avec des données déjà enregistrées."
            )

    # 4) Type / longueur de donnée incompatible côté base
    elif isinstance(exc, DataError):
        message = (
            "Une des valeurs saisies n'est pas au bon format ou est trop longue. "
            "Merci de vérifier les informations du formulaire."
        )
        status = 400

    # 5) Autre erreur base de données
    elif isinstance(exc, SQLAlchemyError):
        message = (
            f"Une erreur est survenue lors de l'{action} en base de données. "
            "Merci de réessayer ; si le problème persiste, prévenez l'administrateur."
        )
        status = 500
        _report_to_sentry(exc)

    # 6) Filet de sécurité
    else:
        message = (
            f"Une erreur inattendue est survenue lors de l'{action}. "
            "Merci de réessayer ; si le problème persiste, prévenez l'administrateur."
        )
        status = 500
        _report_to_sentry(exc)

    payload = {
        "success": False,
        "message": message,
        "field_errors": field_errors,
        "code": status,
    }

    # Détail technique réservé au mode développement (jamais affiché à l'utilisateur)
    if current_app.config.get("DEBUG") or current_app.config.get("MODE_DEVELOPPEMENT"):
        payload["system_error"] = f"{type(exc).__name__}: {exc}"

    return payload, status
