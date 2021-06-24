#!/bin/bash

WEBAPP_HOME=$(dirname $(dirname $(readlink -f "$0")))
source $WEBAPP_HOME/venv/bin/activate
pkill uwsgi
nohup uwsgi --socket 0.0.0.0:5000 --wsgi-file "$WEBAPP_HOME/wsgi.py"
