FROM python:3.5

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    gettext \
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
    bizwiz_appdir=/app/pybizwiz
EXPOSE 80
WORKDIR $bizwiz_appdir

# do not use shell form to have gunicorn start with PID 1 and handle TERM instead of shell
# docker stop --> SIGTERM to PID _1_ --> gunicorn graceful shutdown
ENTRYPOINT ["gunicorn", "-b 0.0.0.0:80", "bwsite.wsgi"]

# install application
COPY . .
RUN pip install -r requirements.txt && \
    pytest test && \
    rm -rf test && \
    python manage.py compilemessages && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', None, 'admin')" | python manage.py shell

# expose data volume after migration to ensure default DB is contained in image
VOLUME $bizwiz_appdir/data
