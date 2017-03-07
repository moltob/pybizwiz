FROM python:3.5

ENV appdir=/app/pybizwiz

COPY . ${appdir}/

WORKDIR ${appdir}
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
