#!/bin/bash

WEBAPP_HOME=$(dirname $(dirname $(readlink -f "$0")))
SCRIPTS_DIR=$(dirname $(readlink -f "$0"))
INSTANCE_HOME="$WEBAPP_HOME/instance"

# Install webapp
echo 'Installing webapp...'
cd $WEBAPP_HOME
pip install .
mkdir instance
cd $SCRIPTS_DIR

echo 'Creating webapp service...'
cat webapp.service
sed -E 's+(ExecStart=)(.*)$+\1'"$SCRIPTS_DIR\/run.sh+" webapp.service > /lib/systemd/system/webapp.service

echo 'Creating log folder...'
mkdir -p /var/log/webapp
ln -s /var/log/webapp $INSTANCE_HOME/logs

echo 'Creating config...'
read -p "Enter IP address of database host: " DATABASE
read -s -p "Enter database password: " PASSWORD
sed -E 's/<host>/'"$DATABASE"'/' $SCRIPTS_DIR/config_template.py | sed -E 's/<password>/'"$PASSWORD"'/' > $INSTANCE_HOME/config.py

echo 'Installing service...'
systemctl enable webapp

echo 'Starting service...'
systemctl start webapp

echo 'Done.'
