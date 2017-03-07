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

# get JS dependencies and remove unused CSS which references unresolved file
bower install
rm bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker-standalone.css

[ -z $(sudo docker images -q bizwiz:latest) ] || sudo docker rmi -f bizwiz:latest
sudo docker build -t bizwiz:latest .
#sudo docker run -it bizwiz pytest test
#sudo docker login ...
#sudo docker push bizwiz mpagel/bizwiz:latest
