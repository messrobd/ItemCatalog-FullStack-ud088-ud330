# Initialise variables
SYS_USER=$(whoami)

[ ! -z ${APP_HOME} ] || { echo 'APP_HOME path must be defined'; exit; }

sudo mkdir -p ${APP_HOME} && sudo chown ${SYS_USER}:${SYS_USER} $_

cd ${APP_HOME} && git init
git remote add origin https://github.com/messrobd/ItemCatalog-FullStack-ud088-ud330.git
git fetch && git pull origin master
