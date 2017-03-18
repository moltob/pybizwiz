#!/usr/bin/env bash
set -e
set -x

# propagate SIGTERM to gunicorn
trap "ps h --ppid $BASHPID -o pid | xargs kill -TERM" SIGTERM

python manage.py migrate
gunicorn --bind 0.0.0.0:443 \
          --access-logfile data/gunicorn-access.log \
          --error-logfile data/gunicorn-error.log \
          --keyfile data/bizwiz.key \
          --certfile data/bizwiz.cert \
          bwsite.wsgi
