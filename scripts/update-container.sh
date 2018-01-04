#!/usr/bin/env sh
set -e
set -x

export PATH=$PATH:/usr/local/bin

sudo docker rm -f bizwiz || true
sudo docker image pull mpagel/bizwiz:latest
sudo docker run -v /volume1/docker/bizwiz/data:/app/bizwiz/data -p 4443:443 --name bizwiz mpagel/bizwiz:latest &
sleep 10
