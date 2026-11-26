# Connexion via Échange (OpenID Connect)

Bouton **« Se connecter via Échange »** sur la page `/login`, affiché **uniquement** aux personnes
déjà connectées à leur Nextcloud « Échange ». La connexion par identifiant / mot de passe
(pypnusershub / UsersHub) reste inchangée.

## Fonctionnement

1. À l'ouverture de `/login`, le front lance une **sonde silencieuse** (`prompt=none`) : le navigateur
   part chez Échange, qui le renvoie aussitôt sur `/oidc/retour` sans afficher de page.
   - connecté à Échange → un `code` est renvoyé : il est gardé 3 min dans le `sessionStorage`, le bouton s'affiche ;
   - non connecté → erreur `login_required` : pas de bouton (résultat mémorisé 3 min, pas de boucle).
2. Au clic, le code (+ `code_verifier` PKCE) est envoyé à `POST /api/user/oidc/callback`. Le back l'échange
   avec le secret client (qui ne quitte jamais le serveur), lit `userinfo`, puis ouvre la session
   comme `auth/login` (cookie `token`, `session["current_user"]`).
3. Code périmé (> 3 min) : le front repasse par Échange (sans page si la session Échange est active).

Aucun compte n'est créé : l'utilisateur doit déjà exister dans `utilisateurs.t_roles`, actif et avec un
droit sur l'application (`filter_by_app`). Sinon : message « compte Échange non rattaché ».
Rapprochement par **identifiant** (claim configurable) et jamais par e-mail par défaut.

## Configuration

Section facultative `oidc` dans `install/config_principal.yaml` (désactivé si absente / vide) :

```yaml
oidc:
  provider_name: "Échange"                # libellé du bouton
  discovery_url: "https://echange.exemple.fr/index.php/apps/oidc/openid-configuration"  # .well-known de Nextcloud
  client_id: "..."
  client_secret: "..."
  scope: "openid profile email"
  redirect_uri: ""                         # vide : <urls.frontend>oidc/retour
  claim_identifiant: "preferred_username"  # claim comparé à t_roles.identifiant (ex. "email")
```

Côté Nextcloud (app « OpenID Connect » / OIDC Identity Provider) : créer un client dont l'URL de
redirection est **exactement** `redirect_uri` (prod : `https://<site>/front/oidc/retour`,
dev : `http://localhost:8080/oidc/retour`).

## Fichiers

- back : `backend/oeasc/modules/oeasc/user/oidc.py`, routes `api/user/oidc/{config,authorize,callback}` dans `user/api.py`, `OIDC` dans `backend/config.py`
- front : `frontend/src/modules/user/oidc.js`, `oidc-retour.vue`, bouton dans `login.vue`, route `/oidc/retour`

## Limites connues

- La sonde provoque un aller-retour de page (redirection) à la 1re visite de `/login` (puis toutes les 3 min).
- Se déconnecter d'OEASC ne déconnecte pas d'Échange : le bouton réapparaît.
- Inspiré de `intranet` / `tizoutis` (`core/auth/oidc.py`).
