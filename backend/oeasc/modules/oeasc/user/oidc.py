"""
Connexion OpenID Connect (flux « authorization code » + PKCE) auprès du
Nextcloud « Échange ».

Le navigateur est redirigé vers le fournisseur, qui renvoie un `code` sur
`redirect_uri` (page du front). Le front transmet ce code au back, qui
l'échange contre un jeton d'accès (avec le secret client, qui ne quitte jamais
le serveur) puis lit le endpoint userinfo.

L'utilisateur est cherché dans `utilisateurs.t_roles` par identifiant (claim
configurable, `preferred_username` par défaut). S'il est inconnu (ni identifiant
ni e-mail déjà présents), son compte est créé automatiquement (voir
`creer_compte`) : droit 3 (groupe « Référent »), rôle « Salarié », organisme
« EP PNC », réception des e-mails acceptée. Un compte existant n'est jamais
modifié ni rapproché par e-mail : un e-mail déjà utilisé par un autre compte
fait refuser la connexion (pas de doublon, pas de prise de contrôle d'un compte).

Configuration : section `oidc` de install/config_principal.yaml (voir
install/docs/oidc.md). Sans `discovery_url` ni `client_id`, tout est désactivé.
"""

import base64
import json
import re
import secrets
from datetime import datetime
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


# valeurs données aux comptes créés à la première connexion via Échange
CREATION_DESC_ROLE = "Salarié, agent, fonctionnaire"
CREATION_ORGANISME = "EP PNC"
CREATION_CODE_PROFIL = 3


def _refuse(message, *args):
    current_app.logger.warning("Connexion OpenID refusée : " + message, *args)
    raise InvalidAuthError


def _utilisateurs_par(champ, valeur):
    """Comptes (hors groupes) dont `champ` vaut `valeur`, sans tenir compte de la casse."""
    return (
        db.session.execute(
            sa.select(models.User)
            .where(sa.func.lower(champ) == valeur.lower())
            .where(models.User.groupe.is_(False))
        )
        .scalars()
        .unique()
        .all()
    )


def creer_compte(login, claims):
    """
    Crée le compte d'un utilisateur Échange absent de UsersHub : droit 3 sur
    l'application (par appartenance au groupe de profil 3), rôle « Salarié »,
    organisme « EP PNC », accept_email = true. Mot de passe aléatoire inutilisable
    (la connexion se fait via Échange ; « mot de passe oublié » reste possible).
    """
    email = str(claims.get("email") or (login if "@" in login else "")).strip()
    # un e-mail déjà porté par un autre compte : on ne crée pas de doublon
    if email and (
        _utilisateurs_par(models.User.email, email)
        or _utilisateurs_par(models.User.identifiant, email)
    ):
        _refuse("e-mail %r déjà utilisé par un autre compte (identifiant %r)", email, login)

    organisme = db.session.execute(
        sa.select(models.Organisme).where(
            models.Organisme.nom_organisme == CREATION_ORGANISME
        )
    ).scalar_one_or_none()
    groupe = db.session.execute(
        sa.select(models.User)
        .join(
            models.UserApplicationRight,
            models.UserApplicationRight.id_role == models.User.id_role,
        )
        .join(
            models.Profils, models.UserApplicationRight.id_profil == models.Profils.id_profil
        )
        .join(
            models.Application,
            models.UserApplicationRight.id_application == models.Application.id_application,
        )
        .where(models.User.groupe.is_(True))
        .where(models.Profils.code_profil == CREATION_CODE_PROFIL)
        .where(models.Application.code_application == current_app.config["CODE_APPLICATION"])
    ).scalars().unique().all()
    if organisme is None or len(groupe) != 1:
        current_app.logger.error(
            "Création de compte OpenID impossible : organisme %r %s, groupes de profil %s : %d",
            CREATION_ORGANISME,
            "introuvable" if organisme is None else "ok",
            CREATION_CODE_PROFIL,
            len(groupe),
        )
        raise InvalidAuthError

    nom = claims.get("family_name") or claims.get("name") or login
    prenom = claims.get("given_name") or ""
    user = models.User(
        identifiant=login,
        email=email or None,
        nom_role=nom,
        prenom_role=prenom,
        desc_role=CREATION_DESC_ROLE,
        id_organisme=organisme.id_organisme,
        champs_addi={"accept_email": True},
        active=True,
        date_insert=datetime.now(),
    )
    user.password = secrets.token_urlsafe(32)
    user.groups.append(groupe[0])
    db.session.add(user)
    db.session.commit()
    current_app.logger.info("Compte créé via Échange : %r (droit %d)", login, CREATION_CODE_PROFIL)
    return user


def find_user(claims):
    """
    Compte `t_roles` correspondant aux claims, autorisé sur cette application ;
    créé s'il n'existe pas (voir `creer_compte`).
    Lève InvalidAuthError si inactif, sans droit sur l'application ou ambigu.
    """
    claim = _conf().get("claim_identifiant") or "preferred_username"
    login = str(claims.get(claim) or "").strip()
    if not login:
        raise InvalidAuthError

    existants = _utilisateurs_par(models.User.identifiant, login)
    if not existants:
        if _conf().get("creer_compte", True) is False:
            _refuse("aucun compte pour %s=%r (création désactivée)", claim, login)
        return creer_compte(login, claims)

    # compte existant : jamais modifié ; il doit être unique, actif et avoir un droit sur l'application
    autorises = (
        db.session.execute(
            sa.select(models.User)
            .where(models.User.id_role.in_([u.id_role for u in existants]))
            .where(models.User.filter_by_app())
        )
        .scalars()
        .unique()
        .all()
    )
    if len(existants) != 1 or len(autorises) != 1 or autorises[0].active is False:
        _refuse("compte %s=%r inactif, ambigu ou sans droit sur l'application", claim, login)
    return autorises[0]
