# env
sudo apt update
sudo apt install -y git
sudo apt-get install -y --no-install-recommends apt-utils

sudo apt install -y python3 python3-pip
sudo apt install -y libpq-dev
sudo apt install -y libgeos-dev
sudo apt-get install -y apache2 libapache2-mod-wsgi libapache2-mod-perl2
sudo apt install -y supervisor
sudo sh -c 'echo "ServerName localhost" >> /etc/apache2/apache2.conf'
sudo a2enmod rewrite
sudo a2dismod mod_pyth
sudo a2enmod wsgi
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo apache2ctl restart


pip3 install virtualenv


# nvm
# make nvm available
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.37.2/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion


echo "Installation de Node et Npm"
cd frontend
nvm install 8.11.0
nvm use 8.11.0

echo " ############"
echo "Installation des paquets Npm"
npm install

npm run build

cd ..

# python 
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt