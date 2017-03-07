FROM python:3.5

# german locale installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq && apt-get install -y locales -qq && locale-gen de_DE.utf8 && dpkg-reconfigure locales && /usr/sbin/update-locale LANG=de_DE.utf8
ENV LANG de_DE.utf8
ENV LANGUAGE de_DE.utf8
ENV LC_ALL de_DE.utf8

# copy application
ENV appdir=/app/pybizwiz
COPY . ${appdir}/

# install packages and assets
WORKDIR ${appdir}
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
