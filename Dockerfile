FROM python:3.5

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    locales

RUN echo "Europe/Berlin" > /etc/timezone && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure tzdata && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="de_DE.UTF-8"'>/etc/default/locale && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales && \
    update-locale LANG=de_DE.UTF-8

# application configuration
ENV LANG=de_DE.UTF-8 \
    LANGUAGE=de_DE.UTF-8 \
    LC_ALL=de_DE.UTF-8 \
    bizwiz_appdir=/app/pybizwiz \
    bizwiz_port=80
EXPOSE $bizwiz_port
WORKDIR $bizwiz_appdir
CMD ["gunicorn", "bwsite.wsgi", "-b 0.0.0.0:$bizwiz_port"]

# install application
COPY . .
RUN pip install -r requirements.txt && \
    pytest test && \
    rm -rf test && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate