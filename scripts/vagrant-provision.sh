#!/usr/bin/env bash
set -e
set -x

# ---- Register repositories ----
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt-get update

# ---- Install ----
sudo apt-get -y install docker-ce
sudo apt-get -y install nodejs-legacy npm
sudo npm install -g bower

# ---- Utilities ----
mkdir -p bin
cp /vagrant/scripts/deploy.sh bin/deploy.sh

echo export PATH=~/bin:$PATH >> ~/.bashrc
chmod a+x bin/*
