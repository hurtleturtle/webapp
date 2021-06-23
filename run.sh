#!/bin/bash

source $PWD/venv/bin/activate
pkill uwsgi
echo "uwsgi --socket 192.168.1.224:5000 --wsgi-file $PWD/wsgi.py"
