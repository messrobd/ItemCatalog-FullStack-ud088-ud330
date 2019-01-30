# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.provision "shell", privileged: false do |script|
    script.path = "tools/provisioning.sh"
    script.env = {
      "APP_HOME" => "/vagrant",
      "DB_USER" => "catalog",
      "APP_CONFIG" => "configuration.DevConfig",
      "SETUP_SCRIPT" => "setup_db.py"
    }
  end

end
