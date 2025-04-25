#!/bin/bash

################################################################
##### Met à jour la base de donnée via alembic de toutes les ###
##### applications utilisé par oeasc.                       ####
################################################################


usage ()
{
    echo 'Usage upgrade_db.sh'
    echo 'Met à jour la base de donnée via alembic de toutes les applications utilisé par oeasc via flask alembic'
    echo 'Options :'
    echo '    --downgrade : remove the venv directory'
    exit
}


if [ "$1" = "--downgrade" ]
then
    echo "Downgrade database"

    # downgrade oeasc supprime la vue problèmatique
    # flask db downgrade 3fc01cbe83a2
    # # downgrade utilisateur
    # flask db downgrade f4bf21ac6238
    # flask db downgrade 112ccf1024ce
    # #  downgrade oeasc. remet la vue problèmatique
    # flask db downgrade 3fc01cbe83a2



else
    echo "Upgrade database"
    # début mise à jour oeasc
    flask db upgrade 8857f2169f96

    # migration utilisateur
    flask db stamp fa35dfe5ff27
    #flask db upgrade fa35dfe5ff27
    flask db upgrade 830cc8f4daef
    flask db upgrade 5b334b77f5f5
    flask db upgrade 951b8270a1cf
    flask db upgrade 10e87bc144cd
    flask db upgrade 112ccf1024ce
    flask db upgrade f4bf21ac6238
    # mise à jour oeasc pour supprimer une vue en conflit
    flask db upgrade 3fc01cbe83a2 
    # passe de la mise à jour utilisateur en conflit avec la vue oeasc
    flask db upgrade f9d3b95946cd
    flask db upgrade b7c98935d9e8
    flask db upgrade cf38131bc247
    flask db upgrade b3dec57f13d8


    # mise à jour oeasc pour remettre la vue suppriméé
    flask db upgrade f90cb83dcdfb


    # mise a jour des nomenclatures
    flask db stamp 6015397d686a
    flask db upgrade 11e7741319fd
    flask db upgrade f8c2c8482419
    flask db upgrade b820c66d8daa

fi


