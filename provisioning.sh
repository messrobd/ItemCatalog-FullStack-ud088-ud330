# Initialise APP_HOME
APP_HOME=${1:-'/vagrant'}
DB_USER=${2:-'catalog'}

# Fix locale
cat <<- EOF >> ~/.bashrc
  LC_CTYPE=en_US.UTF-8
  LC_ALL=en_US.UTF-8
EOF

# Add OS users
sudo useradd -m ${DB_USER}

# Start provisioning resources
sudo apt-get update

# Set up python virtual environment
sudo apt-get -y install python3-venv
sudo mkdir -p ${APP_HOME} && sudo chown vagrant:vagrant $_
python3 -m venv ${APP_HOME}/venv
source ${APP_HOME}/venv/bin/activate
pip3 install wheel
pip3 install Flask psycopg2-binary SQLAlchemy
pip3 install requests google-auth
deactivate

# Install postgresql, create users and db
sudo apt-get -y install postgresql

sudo -u postgres createuser -d ${DB_USER}

sudo -u postgres createdb item_catalog

# Get app



# Install and configure Apache mod-wsgi
sudo apt-get -y install apache2 libapache2-mod-wsgi-py3

sudo cat << EOF | sudo tee /etc/apache2/sites-available/ItemCatalog.conf

<VirtualHost *:80>
  WSGIDaemonProcess ItemCatalog python-home=${APP_HOME}/venv user=${DB_USER} threads=5
  WSGIScriptAlias / ${APP_HOME}/entry.wsgi

  Alias /static/ ${APP_HOME}/static

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
