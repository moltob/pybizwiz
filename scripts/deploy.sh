#!/usr/bin/env bash
#
# Create and push docker image for Bizwiz.

export build-folder=bizwiz-build

rm -rf $(build-folder)
mkdir $(build-folder)
cd $(build-folder)

git clone --depth 1 https://github.com/moltob/pybizwiz.git
cd pybizwiz

bower install
#sudo docker build -t bizwiz .
#sudo docker exec -it bizwiz pytest test
#sudo docker login ...
#sudo docker push bizwiz mpagel/bizwiz:latest
