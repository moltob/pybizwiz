#!/usr/bin/env bash
set -e
set -x

# Create and push docker image for Bizwiz.

export builddir=bizwiz-build

rm -rf ${builddir}
mkdir ${builddir}
cd ${builddir}

git clone --depth 1 https://github.com/moltob/pybizwiz.git
cd pybizwiz

bower install
#sudo docker build -t bizwiz .
#sudo docker exec -it bizwiz pytest test
#sudo docker login ...
#sudo docker push bizwiz mpagel/bizwiz:latest
