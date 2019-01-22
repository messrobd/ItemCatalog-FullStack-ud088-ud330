# Initialise APP_HOME
APP_HOME=${1:-'/vagrant'}

# Fix locale
export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Start provisioning resources
sudo apt-get update

# Set up python virtual environment
sudo apt-get -y install python3-venv
sudo mkdir -p ${APP_HOME} && sudo chown vagrant:vagrant $_
python3 -m venv ${APP_HOME}/venv
source ${APP_HOME}/venv/bin/activate
pip3 install wheel
pip3 install Flask psycopg2-binary SQLAlchemy
deactivate

# Get app


# Install and configure Apache mod-wsgi
sudo apt-get -y install apache2 libapache2-mod-wsgi-py3

sudo cat << EOF | sudo tee /etc/apache2/sites-available/ItemCatalog.conf

<VirtualHost *:80>
  WSGIDaemonProcess ItemCatalog python-home=${APP_HOME}/venv threads=5
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

# Install postgresql
sudo apt-get -y install postgresql

sudo -u postgres createuser catalog
