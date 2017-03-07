FROM python:3.5

ENV appdir=/app/pybizwiz

COPY bizwiz           ${appdir}/bizwiz
COPY bower_components ${appdir}/bower_components
COPY bwsite           ${appdir}/bwsite
COPY test             ${appdir}/test
COPY test *.*         ${appdir}/

WORKDIR ${appdir}
RUN pip install -r requirements.txt

# remove unused CSS which references unresolved file before collecting static files for production:
RUN rm bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker-standalone.css
RUN python manage.py collectstatic --noinput
