# env
sudo apt update
sudo apt install -y git
sudo apt-get install -y --no-install-recommends apt-utils

# nvm
# make nvm available
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.6/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion


echo "Installation de Node et Npm"
cd ../frontend
nvm install
nvm use

echo " ############"
echo "Installation des paquets Npm"
npm ci --only=prod

npm run build