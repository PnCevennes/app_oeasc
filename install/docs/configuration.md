# Configuration de l'application

Toute la configuration est centralisée dans **`install/config_principal.yaml`**
(copie de `install/config_principal.yaml.sample`, ignorée par git car elle contient des secrets).
Le chemin peut être surchargé avec la variable d'environnement `OEASC_CONFIG`.

Elle remplace les anciens `config/config.py`, `config/settings.ini` et `config/variables/declaration.json`.

## Qui lit le fichier ?

| Lecteur | Fichier | Contenu utilisé |
|---|---|---|
| Backend Flask | `backend/config.py` (`app.config.from_object`) | tout, exposé sous les anciens noms (`SQLALCHEMY_DATABASE_URI`, `URL_FRONTEND`, `MAIL_*`, `DECLARATION`…) |
| Scripts bash d'installation | `eval "$(install/install.sh --env [fichier.yaml])"` | variables `db_host`, `db_port`, `db_name`, `user_pg`, `user_pg_pass`, `URL_*`, `ID_APP`… |
| Frontend (build Vite) | plugin `configPrincipal` de `frontend/vite.config.js`, modules `virtual:config-declaration` et `virtual:config-frontend` | **uniquement** `declaration.STATUT_DECLARATION`, `urls.application`, `urls.frontend`, `application.id_app` et la section `frontend` (matomo, mapbox) |

`SQLALCHEMY_DATABASE_URI` est construite par `backend/config.py` à partir de la section `base_de_donnees`
(identifiant et mot de passe sont échappés).

## Sections

`base_de_donnees`, `urls`, `application`, `administrateur`, `gunicorn`, `mail`, `sentry`, `frontend`, `tuiles`, `declaration`
(détail et commentaires dans le `.sample`).

La section `declaration` reprend l'ancien `declaration.json` (statuts, délais de relance, durée de validité,
mails animateurs). Ses clés restent en majuscules. Un changement nécessite de relancer le backend, et de
reconstruire le frontend pour `STATUT_DECLARATION`.

## Dépendances

PyYAML (`requirements.txt`) côté Python, `js-yaml` (devDependency) côté frontend.

## Dans un script bash

```bash
eval "$("$ROOT_DIR/install/install.sh" --env)"            # lit install/config_principal.yaml
eval "$("$ROOT_DIR/install/install.sh" --env autre.yaml)" # ou un autre fichier
```

`frontend/src/config/config.js` est versionné et lit ces valeurs via `virtual:config-frontend` (plus de génération par script).
