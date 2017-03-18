#!/usr/bin/env bash
set -e
set -x

# ---- Utilities ----
mkdir -p bin
cat /vagrant/scripts/deploy.sh | fromdos > bin/deploy.sh
cat /vagrant/scripts/docker-run.sh | fromdos > bin/docker-run.sh

echo export PATH=~/bin:$PATH >> ~/.bashrc
chmod a+x bin/*
