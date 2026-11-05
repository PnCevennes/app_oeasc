# Mise en production

Deux scénarios :

- **nouvelle installation** (base vide) : § 1 à 4, la base est créée par `flask init-db` ;
- **reprise d'une base existante** (dump de production) : § 1, 2, 3, puis § « Base existante ».

La configuration (`install/config_principal.yaml`) est décrite dans [configuration.md](configuration.md).

## 1. Prérequis serveur

PostgreSQL + PostGIS (base et utilisateurs créés, voir `base_de_donnees` dans le yaml), un serveur web
(Apache, vhost fourni) et un accès sudo. Le reste (paquets apt, Node ≥ 24, virtualenv, build, service systemd)
est installé par `install/install.sh`.

## 2. Récupérer le code et configurer

```sh
mkdir ~/apps && cd ~/apps
git clone https://github.com/PnCevennes/app_oeasc.git
cd app_oeasc
cp install/config_principal.yaml.sample install/config_principal.yaml
# renseigner : urls, base de données, mail, sentry, administrateur, tuiles... (voir configuration.md)
```

Fichiers à copier à la main (ignorés par git, cf. `data/README.md`) : `data/ref_geo/*.gpkg`,
`data/degat_agricoles/*`, `static/medias/`.

## 3. Installation complète

```sh
./install/install.sh            # idempotent, peut être relancé à chaque mise à jour
./install/install.sh --help     # --skip-apt --skip-npm --skip-restart --force-npm --remove-venv --with-apache
```

Le script sert **uniquement en production** (en développement : `flask run` et `npm run serve`). Il se lance
avec l'utilisateur qui fera tourner le service, **pas en root ni avec sudo** : il appelle sudo lui-même
(mot de passe demandé une fois au début).

Il refuse de continuer si le yaml n'est pas prêt pour la production : `application.debug` ou
`application.mode_developpement` à `true`, `secret_key` d'exemple ou de moins de 16 caractères, mots de passe
d'exemple (base, administrateur). Il prévient aussi si `gunicorn.host` vaut `0.0.0.0` (backend exposé sans
Apache), si la section mail contient les valeurs d'exemple ou si le port est déjà occupé.

Le script installe les paquets, crée le virtualenv (`venv/`) et installe `requirements.txt`, lit le yaml,
installe les dépendances npm (Node ≥ 24, installé avec nvm s'il manque) et construit le frontend (`frontend/dist`), puis installe
le service systemd `oeasc` (gunicorn, port `urls.port`, variable `OEASC_CONFIG` pointant sur le yaml utilisé
pour le build) et logrotate. Il vérifie ensuite que gunicorn répond en HTTP. Il affiche enfin les branches
Alembic dont la révision courante n'est pas la tête, sans rien appliquer. Avec `--with-apache`, il installe aussi
la configuration `install/assets/apache2/oeasc.conf`. Si `apache2ctl configtest` la refuse, l'ancienne est remise
en place et Apache n'est pas rechargé. Le script signale aussi si `www-data` ne peut pas lire `frontend/dist` :

- le frontend est servi sous `/front/` depuis `frontend/dist` ;
- l'API est relayée de `/oeasc/api` vers gunicorn (`127.0.0.1:5005`).

**La base de données n'est jamais touchée par `install.sh`.**

## 4. Nouvelle base : `flask init-db`

```sh
source venv/bin/activate
cd backend
flask init-db
```

Détail des étapes et limites : [install_db.md](install_db.md). Ensuite, charger le référentiel géographique
(`flask refresh-ref-geo`, voir [mise_a_jour_ref_geo.md](mise_a_jour_ref_geo.md)).

## Base existante (reprise d'un dump)

```sh
# Suppression, création et restauration de la base (utilisateur d'administration PostgreSQL)
psql -d postgres -h localhost -U <admin_pg> -c "DROP DATABASE oeasc_prod;"
psql -d postgres -h localhost -U <admin_pg> -c "CREATE DATABASE oeasc_prod WITH OWNER <user_oeasc>;"
pg_restore -F c -h localhost -d oeasc_prod -U <admin_pg> <dump>.backup
# postgres_fdw (si présent dans le dump) est inutile
sudo -u postgres psql -d oeasc_prod -c "DROP SERVER data_oeasc_prod CASCADE;"
sudo -u postgres psql -d oeasc_prod -c "DROP EXTENSION postgres_fdw;"
# propriétaire des objets
sudo -u postgres psql -d oeasc_prod -c "REASSIGN OWNED BY <admin_pg> TO <user_oeasc>;"
```

Puis aligner les migrations Alembic : voir [alembic.md](alembic.md). Cible : `flask db upgrade <révision>`
**avec une révision explicite** (la base contient plusieurs branches Alembic).
Une base issue de l'ancien OEASC peut contenir des doublons à nettoyer avant certaines migrations
(clés primaires sur `oeasc_commons.t_communes` et `oeasc_forets.cor_dgd_cadastre`) :
[correction_doublon_bdd.md](correction_doublon_bdd.md).

## Cartes : proxy des tuiles

Les cartes de la fiche déclaration (`voir_declaration.vue`) ne chargent pas leur fond directement depuis le
navigateur : elles passent par la route backend

```
GET /api/declaration/tiles/v2/<z>/<x>/<y>.png
```

qui relaie le **Géoportail IGN** (couche « Plan IGN v2 », `data.geopf.fr`, sans clé d'API) et met les tuiles en
cache disque dans `data/cache/tile/<dossier_cache>/` (7 jours par défaut, tuile périmée resservie si l'IGN est
injoignable). Objectif : que le poste client n'ait pas à atteindre l'IGN (réseaux filtrants, antivirus qui casse
le HTTPS/CORS → « cartes grises ») et que l'export PDF puisse capturer les tuiles.

Paramétrage : section `tuiles` du yaml (`url`, `user_agent`, `cache_jours`, `timeout`, `dossier_cache`). Si
le fournisseur change, changer `dossier_cache` et incrémenter le préfixe `v2/` de la route (sinon les
navigateurs resservent leur cache pendant 7 jours). Le cache peut être vidé sans risque.

### Vérifier l'accès sortant du serveur

```sh
# avec l'utilisateur du service systemd
sudo -u <user_du_service> curl -sS -o /dev/null -w "HTTP %{http_code}\n" \
  "https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX=9&TILEROW=178&TILECOL=256&FORMAT=image%2Fpng"

# bout en bout, après déploiement
curl -sS -o /dev/null -w "%{http_code} %{content_type}\n" https://<domaine>/oeasc/api/declaration/tiles/v2/9/256/178.png
```

`200 image/png` attendu. `502` : le backend n'atteint pas l'IGN (ou cache non inscriptible). Si un proxy
sortant est imposé, l'ajouter dans le fichier `environ` du service (`HTTPS_PROXY=...`, `NO_PROXY=127.0.0.1,localhost`)
puis `sudo systemctl restart oeasc`.

### (Optionnel) Cache Apache `mod_cache_disk`

Le cache disque du backend suffit en général ; `mod_cache_disk` n'économise que l'aller-retour Apache → gunicorn.

```sh
sudo a2enmod cache cache_disk
```

Dans le `<VirtualHost>` (le backend envoie déjà `Cache-Control: public, max-age=...`) :

```apache
CacheRoot /var/cache/apache2/oeasc_tiles
CacheDirLevels 2
CacheDirLength 1

<Location /oeasc/api/declaration/tiles>
    CacheEnable disk
    CacheHeader on
</Location>
```

```sh
sudo mkdir -p /var/cache/apache2/oeasc_tiles && sudo chown www-data:www-data /var/cache/apache2/oeasc_tiles
sudo systemctl enable --now apache-htcacheclean
sudo apachectl configtest && sudo systemctl reload apache2
```

## Commandes de maintenance

Toutes se lancent depuis `backend/`, virtualenv activé.

| Commande | Rôle |
|---|---|
| `flask init-db` | crée la base (voir [install_db.md](install_db.md)) |
| `flask refresh-ref-geo` | reconstruit `ref_geo.l_areas` depuis `data/ref_geo/*.gpkg` ([mise_a_jour_ref_geo.md](mise_a_jour_ref_geo.md)) |
| `flask fix-vm-lareas-simples-simplification` | recrée `ref_geo.vm_lareas_simples` avec la simplification limitée |
| `flask send-relance` | envoie les mails de relance des déclarations |
| `flask archive-medias-orphelins [--apply]` | déplace dans `archive/media_orphelins/` les médias de `static/medias/` plus référencés (simulation sans `--apply`) |
| `flask db ...` | migrations Alembic ([alembic.md](alembic.md)) |
