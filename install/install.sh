#!/bin/bash

REMOVE_VENV=0
REMOVE_NODE=0

usage ()
{
    echo 'Usage install.sh'
    echo 'Options :'
    echo '    -remove-venv : remove the venv directory'
    exit
}

# gestion des options
optspec=":-:"
while getopts "$optspec" optchar; do
    case "${OPTARG}" in
        help)
usage
exit 1
;;
remove-venv)
REMOVE_VENV=1
;;
remove-node)
REMOVE_NODE=1
;;
remove-all)
REMOVE
;;
h)
usage
exit 1
;;
esac
done

ROOT_DIR=$(readlink -e "${0%/*}")/..

if ! [ -f server.py ]
then
cp $ROOT_DIR/server.py.sample $ROOT_DIR/server.py
fi

$ROOT_DIR/install/init_config.sh $ROOT_DIR/config/settings.ini

echo "Installation"
echo "Aucune suppression du venv configuré pour le test; Refaire le fichier d'installation pour la phase de production"

echo "Installation du virtual env"
# Suppression du venv s'il existe
if [ "$REMOVE_VENV" = "1" ] && [ -d 'venv/' ]
then
  echo "Suppression du virtual env existant..."
  rm -rf venv
fi

#pour pygdal
# sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable && sudo apt-get update
# if [[ -z $(which curl) ]]; then
#     sudo apt-get install python3.6-dev
#     sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable && sudo apt-get update
#     sudo apt-get install libgdal-dev
# fi

#python3 -m venv venv

echo "Activation du virtual env..."
source venv/bin/activate

echo "Installation des dépendances python..."
pip install --upgrade pip
pip install -r requirements.txt

# # node et npm installation
echo "Instalation de npm"

cd $ROOT_DIR/static/

if [ "REMOVE_NODE" = "1" ]
then
    echo "supression de node_modules"
    rm -Rf node_modules
fi

if [[ -z  $(which nvm) ]]; then

    sudo apt install curl
    sudo apt install nodejs

    # installation de nvm pour gérer les versions de node
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    # cette partie permet d'eviter de relancer le terminal
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

    # installation de la version 10 de node
    nvm install 10

fi


echo "Installation des paquets npm"
npm install
cd frontend/
npm install
# la route du frontent est défini dans frontend/vue.config.js et est actuellement à /front/ en production et / en devellopement
npm run build



cd $ROOT_DIR