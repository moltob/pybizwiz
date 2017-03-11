#!/usr/bin/env bash
set -e
set -x

# Create and push docker image for Bizwiz.

export builddir=~/bizwiz-build

rm -rf ${builddir}
mkdir ${builddir}
cd ${builddir}

git clone --depth 1 https://github.com/moltob/pybizwiz.git
cd pybizwiz

# get JS dependencies and remove unused CSS which references unresolved file
bower install
rm bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker-standalone.css

export version=`python3 -c "from bizwiz.version import *; print('v%s' % BIZWIZ_VERSION);"`
export image=mpagel/bizwiz:$version
[ -z $(sudo docker images -q $image) ] || sudo docker rmi -f $image
sudo docker build -t $image .
#sudo docker push $image
