FROM python:3.5

# german locale installation
ENV LANG de_DE.UTF-8
ENV LANGUAGE $LANG
ENV LC_ALL $LANG
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils locales
RUN sed -i -e "s/# $LANG.*/$LANG.UTF-8 UTF-8/" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$LANG

# copy application
ENV appdir=/app/pybizwiz
COPY . $appdir/

# install packages and assets
WORKDIR $appdir
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
