"""
Connexion OpenID Connect (flux « authorization code » + PKCE) auprès du
Nextcloud « Échange ».

Le navigateur est redirigé vers le fournisseur, qui renvoie un `code` sur
`redirect_uri` (page du front). Le front transmet ce code au back, qui
l'échange contre un jeton d'accès (avec le secret client, qui ne quitte jamais
le serveur) puis lit le endpoint userinfo.

Aucun compte n'est créé : l'utilisateur est cherché dans `utilisateurs.t_roles`
par identifiant (claim configurable, `preferred_username` par défaut), jamais
par e-mail sauf configuration explicite, un e-mail pouvant être modifié par
l'utilisateur côté Nextcloud.

Configuration : section `oidc` de install/config_principal.yaml (voir
install/docs/oidc.md). Sans `discovery_url` ni `client_id`, tout est désactivé.
"""

import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request

import sqlalchemy as sa
from flask import current_app
from pypnusershub.db import db, models

TIMEOUT = 10

_discovery = {}


class InvalidAuthError(Exception):
    """Code refusé ou compte inconnu / inactif."""


def _conf():
    return current_app.config.get("OIDC") or {}


def is_enabled():
    c = _conf()
    return bool(c.get("discovery_url") and c.get("client_id"))


def provider_name():
    return _conf().get("provider_name") or "Échange"


def _http_json(req):
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discovery():
    """Document de découverte du fournisseur, lu une fois par process."""
    if not _discovery:
        _discovery.update(_http_json(_conf()["discovery_url"]))
    return _discovery


# PKCE (RFC 7636) : empreinte SHA-256 en base64url (43 caractères) et
# code_verifier de 43 à 128 caractères, générés par le front
RE_CHALLENGE = re.compile(r"^[A-Za-z0-9_-]{43}$")
RE_VERIFIER = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")


def authorize_url(state, code_challenge, silencieux=False):
    """
    URL vers laquelle rediriger le navigateur pour s'authentifier.

    `silencieux` : `prompt=none`, le fournisseur ne montre aucune page et
    renvoie aussitôt soit un code (utilisateur déjà connecté à Échange), soit
    une erreur (`login_required`…) sur `redirect_uri`. C'est ce qui permet de
    n'afficher le bouton que pour les personnes connectées à Échange.
    """
    c = _conf()
    params = {
        "response_type": "code",
        "client_id": c["client_id"],
        "redirect_uri": c["redirect_uri"],
        "scope": c.get("scope") or "openid profile email",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if silencieux:
        params["prompt"] = "none"
    return discovery()["authorization_endpoint"] + "?" + urllib.parse.urlencode(params)


def exchange_code(code, code_verifier):
    """Échange le code (+ code_verifier PKCE) contre les claims userinfo."""
    c = _conf()
    disc = discovery()
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": c["redirect_uri"],
        "code_verifier": code_verifier,
    }
    headers = {"Accept": "application/json"}
    methods = disc.get("token_endpoint_auth_methods_supported", ["client_secret_basic"])
    if "client_secret_post" in methods:
        form["client_id"] = c["client_id"]
        form["client_secret"] = c["client_secret"]
    else:
        creds = "%s:%s" % (
            urllib.parse.quote(c["client_id"], safe=""),
            urllib.parse.quote(c["client_secret"], safe=""),
        )
        headers["Authorization"] = "Basic " + base64.b64encode(
            creds.encode("utf-8")
        ).decode("ascii")

    try:
        tokens = _http_json(
            urllib.request.Request(
                disc["token_endpoint"],
                data=urllib.parse.urlencode(form).encode("utf-8"),
                headers=headers,
                method="POST",
            )
        )
        return _http_json(
            urllib.request.Request(
                disc["userinfo_endpoint"],
                headers={
                    "Authorization": "Bearer " + tokens["access_token"],
                    "Accept": "application/json",
                },
            )
        )
    except (urllib.error.HTTPError, KeyError) as err:
        raise InvalidAuthError from err


def find_user(claims):
    """
    Compte `t_roles` correspondant aux claims, autorisé sur cette application.
    Lève InvalidAuthError si inconnu, inactif ou sans droit sur l'application.
    """
    claim = _conf().get("claim_identifiant") or "preferred_username"
    login = str(claims.get(claim) or "").strip()
    if not login:
        raise InvalidAuthError
    users = (
        db.session.execute(
            sa.select(models.User)
            .where(sa.func.lower(models.User.identifiant) == login.lower())
            .where(models.User.filter_by_app())
        )
        .scalars()
        .unique()
        .all()
    )
    # unicité exigée : en cas de doute, on refuse
    if len(users) != 1 or users[0].active is False:
        current_app.logger.warning(
            "Connexion OpenID refusée : aucun compte actif unique pour %s=%r",
            claim,
            login,
        )
        raise InvalidAuthError
    return users[0]
