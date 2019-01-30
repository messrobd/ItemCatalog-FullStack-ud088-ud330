# Initialise variables (default if not passed from VagrantFile)
SYS_USER=$(whoami)
APP_HOME=${APP_HOME:-$(pwd)}
DB_USER=${DB_USER:-'catalog'}
APP_CONFIG=${APP_CONFIG:-'configuration.DevConfig'}
SETUP_SCRIPT=${SETUP_SCRIPT:-'setup_db.py'}

# Fix locale w/in script
echo 'Fix locale'
declare -a locale_settings=("LC_CTYPE" "LC_ALL")
target_locale="C"
for l in ${locale_settings[@]}; do
        if ! [ ${l} = ${target_locale} ]; then
                export ${l}=${target_locale}
                echo "export ${l}=${target_locale}" >> ~/.bashrc
        fi
done

# Start provisioning resources
echo 'Get updates'
sudo apt-get update

# Set up python virtual environment
echo 'Set up python virtual environment'
sudo apt-get -y install python3-venv
sudo mkdir -p ${APP_HOME} && sudo chown ${SYS_USER}:${SYS_USER} $_
python3 -m venv ${APP_HOME}/venv
declare -a requirements=("Flask" "psycopg2-binary" "SQLAlchemy" "requests" "google-auth")
source ${APP_HOME}/venv/bin/activate
for r in ${requirements[@]}; do
        pip3 install ${r}
        [ ! -z $(pip3 freeze | grep ${r}) ] || { echo 'Missing requirement:' ${r}; exit; }
done
deactivate

# Set up database
echo 'Set up database'
# Add OS users
sudo useradd -m ${DB_USER}

# Install postgresql, create users and db
sudo apt-get -y install postgresql

sudo -u postgres createuser -d ${DB_USER}

sudo -u postgres createdb item_catalog

# Get app and create db tables with sample data
echo 'Get app'
cd ${APP_HOME} && git init
git remote add origin https://github.com/messrobd/ItemCatalog-FullStack-ud088-ud330.git
git fetch && git pull origin master

sudo -u ${DB_USER} bash << EOF
source ${APP_HOME}/venv/bin/activate
python3 ${APP_HOME}/${SETUP_SCRIPT}
deactivate
EOF

# Install and configure Apache mod-wsgi, and initialise
echo 'Install and initialise Apache'
sudo apt-get -y install apache2 libapache2-mod-wsgi-py3

sudo cat << EOF | sudo tee /etc/apache2/sites-available/ItemCatalog.conf
<VirtualHost *:80>
  SetEnv APP_CONFIG ${APP_CONFIG}
  WSGIDaemonProcess ItemCatalog python-home=${APP_HOME}/venv user=${DB_USER} threads=5
  WSGIScriptAlias / ${APP_HOME}/entry.wsgi

  <Directory ${APP_HOME}>
    WSGIProcessGroup ItemCatalog
    WSGIApplicationGroup %{GLOBAL}
    Require all granted
  </Directory>

</VirtualHost>
EOF

sudo a2dissite 000-default
sudo a2ensite ItemCatalog

sudo service apache2 reload
