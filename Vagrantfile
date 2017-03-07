# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 8000, host: 8001

  config.vm.provision :shell, path: "scripts/vagrant-provision.sh"
  config.vm.provision :shell, path: "scripts/vagrant-provision-user.sh", privileged: false
end
