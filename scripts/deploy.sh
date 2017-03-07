#!/usr/bin/env bash
#
# Create and push docker image for Bizwiz.

export build=bizwiz-build

rm -rf ${build}
mkdir ${build}
cd ${build}

git clone --depth 1 git@github.com:moltob/pybizwiz.git
cd pybizwiz

bower install

sudo docker build -t bizwiz .
sudo docker run -it bizwiz pytest test



#docker login ...
#docker push bizwiz mpagel/bizwiz:latest
