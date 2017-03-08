FROM python:3.5

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    locales

RUN DEBIAN_FRONTEND=noninteractive \
    echo "Europe/Berlin" > /etc/timezone && \
    dpkg-reconfigure tzdata && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="de_DE.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure locales && \
    update-locale LANG=de_DE.UTF-8

#ENV LANG de_DE.UTF-8
#ENV LANGUAGE de_DE.UTF-8
#ENV LC_ALL de_DE.UTF-8

# copy application
ENV appdir=/app/pybizwiz
COPY . $appdir/

# install packages and assets
WORKDIR $appdir
RUN pip install -r requirements.txt && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate
