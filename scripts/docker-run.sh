#!/usr/bin/env bash
set -e
set -x

mkdir -p docker-data
sudo docker run -v ~/docker-data:/app/pybizwiz/data -p 4443:443 $@
