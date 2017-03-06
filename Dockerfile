###################################################################
#
# - create container serving static data via apache
# - create container serving a Python web application
# - combine the two
# - serve via https
# - deploy Bizwiz
#
###################################################################

FROM httpd:2.4
COPY ./*.html /usr/local/apache2/htdocs/
