#!/bin/bash

source $0/venv/bin/activate
echo "uwsgi --socket localhost:8000 --wsgi-app $0/wsgi.py"
