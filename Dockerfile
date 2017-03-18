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
    BIZWIZ_LOG_LEVEL=DEBUG \
    DJANGO_LOG_LEVEL=INFO \
    WEB_CONCURRENCY=6 \
    bizwiz_appdir=/app/pybizwiz \
    bizwiz_port=443
EXPOSE $bizwiz_port
WORKDIR $bizwiz_appdir

# call application from current process to ensure proper signal propagation
ENTRYPOINT source scripts/launch.sh

# install application
COPY . .
RUN pip install -r requirements-prod.txt && \
    pytest test && \
    rm -f data/*.log* && \
    python manage.py compilemessages && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', None, 'admin')" | python manage.py shell
