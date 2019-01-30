# Initialise variables
SYS_USER=$(whoami)
APP_HOME=${APP_HOME:-'/var/www/Flask/ItemCatalog'}

sudo mkdir -p ${APP_HOME} && sudo chown ${SYS_USER}:${SYS_USER} $_

cd ${APP_HOME} && git init
git remote add origin https://github.com/messrobd/ItemCatalog-FullStack-ud088-ud330.git
git fetch && git pull origin master
