#!/usr/bin/env bash
#
# Create and push docker image for Bizwiz.

export build-folder=bizwiz-build

rm -rf $(build-folder)
mkdir $(build-folder)
cd $(build-folder)

git clone --depth 1 git@github.com:moltob/pybizwiz.git
cd pybizwiz

bower install
docker build -t bizwiz .
docker exec -it bizwiz pytest test
docker login ...
docker push bizwiz mpagel/bizwiz:latest
