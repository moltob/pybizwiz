FROM python:3.5

# german locale installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends locales
RUN locale-gen de_DE.UTF-8 && dpkg-reconfigure locales && /usr/sbin/update-locale LANG=de_DE.UTF-8
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE.UTF-8
ENV LC_ALL de_DE.UTF-8

# copy application
ENV appdir=/app/pybizwiz
COPY . ${appdir}/

# install packages and assets
WORKDIR ${appdir}
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
