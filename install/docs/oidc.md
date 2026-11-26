# Connexion via Échange (OpenID Connect)

Bouton **« Se connecter via Échange »** sur la page `/login`, affiché **uniquement** aux personnes
déjà connectées à leur Nextcloud « Échange ». La connexion par identifiant / mot de passe
(pypnusershub / UsersHub) reste inchangée.

## Fonctionnement

1. À l'ouverture de `/login`, le front lance une **sonde silencieuse** (`prompt=none`) : le navigateur
   part chez Échange, qui le renvoie aussitôt sur `/oidc/retour` sans afficher de page.
   - connecté à Échange → un `code` est renvoyé : il est gardé 3 min dans le `sessionStorage`, le bouton s'affiche ;
   - connecté mais accord à donner (`consent_required` / `interaction_required`) : Échange ne peut pas afficher
     de page en mode silencieux, mais la personne est bien connectée : le bouton s'affiche et son clic lance
     une connexion **avec page** (demande d'autorisation d'Échange, une fois) ;
   - non connecté → erreur `login_required` : pas de bouton (résultat mémorisé 20 s seulement, pas de boucle ; la sonde est relancée au retour sur l'onglet, pour qui se connecte à Échange après avoir ouvert `/login`).
2. Au clic, le code (+ `code_verifier` PKCE) est envoyé à `POST /api/user/oidc/callback`. Le back l'échange
   avec le secret client (qui ne quitte jamais le serveur), lit `userinfo`, puis ouvre la session
   comme `auth/login` (cookie `token`, `session["current_user"]`).
3. Code périmé (> 3 min) : le front repasse par Échange (sans page si la session Échange est active).

## Comptes

Rapprochement par **identifiant** (`t_roles.identifiant` = claim `claim_identifiant`, sans tenir compte de la casse).
- **Compte existant** : jamais modifié. Il doit être unique, actif et avoir un droit sur l'application, sinon refus.
- **Compte inconnu** : créé automatiquement (`oidc.py: creer_compte`) avec
  droit 3 (appartenance au groupe « Grp OEASC Referent », profil 3), rôle « Salarié, agent, fonctionnaire »,
  organisme « Parc national des Cévennes », `champs_addi.accept_email = true`, mot de passe aléatoire inutilisable.
  Nom / prénom / e-mail viennent des claims `family_name`, `given_name`, `email`.
- **Garde-fou anti-doublon** : si l'e-mail du compte à créer est déjà l'e-mail ou l'identifiant d'un autre
  compte, la connexion est refusée (message dans les logs). Les identifiants OEASC étant en général des
  e-mails, `claim_identifiant: "email"` évite ce cas pour les comptes existants.
- Désactiver la création : `creer_compte: false` dans la section `oidc`.

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
  creer_compte: true                       # crée le compte d'un utilisateur Échange inconnu (droit 3, salarié, Parc national des Cévennes)
```

Côté Nextcloud (app « OpenID Connect » / OIDC Identity Provider) : créer un client dont l'URL de
redirection est **exactement** `redirect_uri` (prod : `https://<site>/front/oidc/retour`,
dev : `http://localhost:8080/oidc/retour`).

## Fichiers

- back : `backend/oeasc/modules/oeasc/user/oidc.py`, routes `api/user/oidc/{config,authorize,callback}` dans `user/api.py`, `OIDC` dans `backend/config.py`
- front : `frontend/src/modules/user/oidc.js`, `oidc-retour.vue`, bouton dans `login.vue`, route `/oidc/retour`

## Diagnostic

`/front/login?diag=1` affiche un encadré « Diagnostic Échange » : état de l'API (`api/user/oidc/config`),
résultat de la dernière sonde et réponse d'Échange (`login_required`, `consent_required`…). La réponse est
aussi écrite dans la console du navigateur (`[OIDC Échange] sonde sans code`). Utile quand le bouton
n'apparaît pas :

| Message | Cause |
|---|---|
| `login_required` | Échange ne voit pas la session (autre navigateur, fenêtre privée, cookies bloqués) |
| `consent_required` | normal à la 1re connexion : le bouton s'affiche quand même |
| `invalid_*` | client Nextcloud mal configuré (redirect_uri, scope) |
| « désactivée dans la configuration » | section `oidc` absente ou worker gunicorn pas redémarré |
| « l'API … ne répond pas » | URL d'API ou routage Apache |

## Limites connues

- La sonde provoque un aller-retour de page (redirection) à la visite de `/login` si le dernier résultat a plus de 20 s (3 min pour un code d'autorisation).
- Se déconnecter d'OEASC ne déconnecte pas d'Échange : le bouton réapparaît.
- Inspiré de `intranet` / `tizoutis` (`core/auth/oidc.py`).
