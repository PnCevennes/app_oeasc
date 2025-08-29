
# Prérequis serveur

```sh
sudo apt update
sudo apt-get install python3-venv  python3-dev libpq-dev build-essential curl git nginx
```

## installation de nvm
```sh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.bashrc
```

## Base de données


### Migration de serveur de base de données
```sh
# -- Suppresion, création et restauration de la base si nécessaire
psql -d postgres -h localhost -U pnc_dbadmin -c "DROP DATABASE oeasc_prod;"
psql -d postgres -h localhost -U pnc_dbadmin -c "CREATE DATABASE oeasc_prod WITH OWNER oeascadmin;"
pg_restore  -F c -h localhost -d oeasc_prod -U pnc_dbadmin ~/database/backup/dump_oeasc_prod2025-08-13.backup
# -- suppression de postgres_fdw qui est inutile
sudo su postgres psql -d oeasc_prod  -c "DROP SERVER data_oeasc_prod CASCADE;"
sudo su postgres psql -d oeasc_prod  -c "DROP EXTENSION postgres_fdw;"
# -- Correction des droits et des propriétés de la base
sudo su postgres psql -d oeasc_prod  -c "REASSIGN OWNED BY pnc_dbadmin TO oeascadmin;"
```


### Correction des données requises
Lancer le script sql de correction des doublons contenues dans le fichier correction_doublons_bdd.md


# Installation d'OEASC

## Installation du backend
```sh
mkdir ~/apps
cd ~/apps
git clone https://github.com/PnCevennes/app_oeasc.git
cd oeasc
python3 -m venv venv
source venv/bin/activate
pip install -e .
```


### Configuration du backend

```sh
cp backend/config/config.py.sample backend/config/config.py
```
mettre les bonnes addresse ip, les identifiants de bdd et sentry


### Installation de systemd
```sh
./install/configure_systemd.sh
```

## MIGRATION DE LA BASE DE DONNÉE

```sh
### stamp de la base de l'oeasc d'origine
    flask db stamp 8857f2169f96

## migration utilisateur
    flask db stamp fa35dfe5ff27
    # flask db upgrade 830cc8f4daef# inutile f4bf21ac6238 suffi
    # flask db upgrade 5b334b77f5f5 # inutile f4bf21ac6238 suffi
    # flask db upgrade 951b8270a1cf # inutile f4bf21ac6238 suffi
    # flask db upgrade 10e87bc144cd # inutile f4bf21ac6238 suffi
    # flask db upgrade 112ccf1024ce # inutile f4bf21ac6238 suffi
    flask db upgrade f4bf21ac6238

## mise à jour oeasc pour supprimer une vue en conflit
    flask db upgrade 3fc01cbe83a2

## passe de la mise à jour utilisateur en conflit avec la vue oeasc
    flask db upgrade f9d3b95946cd
    flask db upgrade b3dec57f13d8

## mise à jour oeasc pour remettre la vue supprimée
## Attention de bien être dans le dossier racine car cette requête récupère le contenu d'un autre fichier
    flask db upgrade f90cb83dcdfb

## lancer les script pour retirer les doublons dans oeasc_forets.cor_dgd_cadastre et commons.t_communes
## script dans correction_doublons_bdd.md
    flask db upgrade 96ebff8bac23


## mise a jour des nomenclatures
    flask db stamp 6015397d686a
    # flask db upgrade 11e7741319fd  # inutile b820c66d8daa suffi
    # flask db upgrade f8c2c8482419 # inutile b820c66d8daa suffi
    flask db upgrade b820c66d8daa

## ajout de clé primaire pour les cadastres. Retirer les doublons avant.
    flask db upgrade 437c188c6344
## ajout de clé primaire pour les communes. Retirer les doublons avant.
    flask db upgrade 0a44db773490






```

##  Frontend

### Configuration

```sh
cp src/frontend/config/config.js.sample src/frontend/config/config.js
```
mettre la bonne adresse du server dans src/frontend/config/config.js


### Installation et deploiement

```sh
cd frontend
nvm install 18
nvm use
npm ci
npm run build
```

### NGINX

Modifier le fichier de configuration pour pointer vers le build du frontend (root /home/oeasc/apps/app_oeasc/frontend/dist;) et l'utilisateur nginx si necessaire (nginx.conf)


##  Static
Copier les fichiers statics




-------------------------------------------------------------------------------------------------------
# Pour le dev

# partie concernant les librairies pnx à installer. A installer dans un autre dossier que app_oeasc pour le dev
1. ## les librairies d'orgine
- ### UserHub
    git clone https://github.com/PnX-SI/UsersHub.git
    voir son installation ici https://usershub.readthedocs.io/fr/latest/
- ### Nomenclature-api-module
    git clone https://github.com/PnX-SI/Nomenclature-api-module.git


2. ## les librairies qui ont été modifiées
- ### UserHub Authentification
    git clone https://github.com/Fargo48/UsersHub-authentification-oeasc-module.git
    dans le repertoire Userhub-authentification, executer
    git fetch origin
    git checkout -b fix/register_user origin/fix/register_user
    pip install -e .

- ### TaxeHub
    git clone https://github.com/Fargo48/TaxHub.git
    git fetch origin
    git checkout -b feat/sqlalchemy2 origin/feat/sqlalchemy2
    pip install -e .

- ### Utils-flask-sqlalchemy
    git clone https://github.com/Fargo48/Utils-Flask-SQLAlchemy.git
    git fetch origin
    git checkout -b feat/sql-alchemy2-rebase origin/feat/sql-alchemy2-rebase
    pip install -e .

- ### Utils-flask-sqlalchemy-Geo
    git clone https://github.com/Fargo48/Utils-Flask-SQLAlchemy-Geo.git
    git fetch origin
    git checkout -b feat/sqlalchemy2 origin/feat/sqlalchemy2
    pip install -e .