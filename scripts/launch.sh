#@IgnoreInspection BashAddShebang
# script is sourced into calling shell process, so no shebang is used
python manage.py migrate
gunicorn --bind 0.0.0.0:$bizwiz_port \
          --access-logfile data/gunicorn-access.log \
          --error-logfile data/gunicorn-error.log \
          --keyfile data/bizwiz.key \
          --certfile data/bizwiz.cert \
          bwsite.wsgi
