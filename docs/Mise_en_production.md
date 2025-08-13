
# La base
    sudo apt update
    sudo apt-get install pip3
    sudo apt-get install python3-venv
# creation et activation d'un environement python
    python3 -m venv venv
    source venv/bin/activate
    sudo apt-get install python3-dev libpq-dev
    pip install psycopg2-binary

# Installation d'OEASC
    git clone https://github.com/PnCevennes/app_oeasc.git
    pip install -r requirements.txt

    ## si il y a un problème de clonage des lib du pnx git avec le ssh
    remplacher git+ssh: par git+https: dans requirement.txt

    ## A noter:
        la librairie UserHub-authentification est un fork. Il faut se mettre sur la branche fix/register_user
        la librairie TaxeHub  est un fork. Il faut se mettre sur la branche feat/sqlalchemy2
        la librairie Utils-flask-sqlalchemy est un fork. Il faut se mettre sur la branche feat/sql-alchemy2-rebase
        la librairie Utils-flask-sqlalchemy-Geo est un fork. Il faut se mettre sur la branche feat/sqlalchemy2

    ## Configuration
        - Dans backend/app.py
            - Si il y a Sentry d'actif, décommenter le code CONFIGURATION DE SENTRY (ligne 98)
            - En developpement ou en production, decommenter la bonne partie sur l'affichage des erreurs ou warning
        - Dans backend/config/config.py
            mettre les bonnes addresse ip, les identifiants de bdd etc..

    ## dans le repertoire oeasc
        pip install -e .




# MIGRATION DE LA BASE DE DONNÉE

## stamp de la base de l'oeasc d'origine
    flask db stamp 8857f2169f96

## migration utilisateur
    flask db stamp fa35dfe5ff27
    flask db upgrade 830cc8f4daef
    flask db upgrade 5b334b77f5f5
    flask db upgrade 951b8270a1cf
    flask db upgrade 10e87bc144cd
    flask db upgrade 112ccf1024ce
    flask db upgrade f4bf21ac6238
## mise à jour oeasc pour supprimer une vue en conflit
    flask db upgrade 3fc01cbe83a2

## mise a jour des nomenclatures
    flask db stamp 6015397d686a
    flask db upgrade 11e7741319fd
    flask db upgrade f8c2c8482419
    flask db upgrade b820c66d8daa

## ajout de clé primaire pour les cadastres. Retirer les doublons avant.
    flask db upgrade 437c188c6344
## ajout de clé primaire pour les communes. Retirer les doublons avant.
    flask db upgrade 0a44db773490

    flask db upgrade 3fc01cbe83a2

## passe de la mise à jour utilisateur en conflit avec la vue oeasc
    flask db upgrade f9d3b95946cd
    flask db upgrade b7c98935d9e8
    flask db upgrade cf38131bc247
    flask db upgrade b3dec57f13d8

## mise à jour oeasc pour remettre la vue supprimée
## Attention de bien être dans le dossier racine car cette requête récupère le contenu d'un autre fichier
    flask db upgrade f90cb83dcdfb

## lancer les script pour retirer les doublons dans oeasc_forets.cor_dgd_cadastre et commons.t_communes
## script dans correction_doublons_bdd.md
    flask db upgrade 437c188c6344
    flask db upgrade 0a44db773490
    flask db upgrade 96ebff8bac23


# Paramétrage du Frontend
    ### en cas d'erreur de segmentation:
        nvm use v10.15.3
    - mettre la bonne adresse du server dans
    frontend/config/config.js
    - Dans le repertoire frontend
    npm install



# Creation d'un processus systemd pour faire tourner flask
Executer
install/configure_systemd.sh





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