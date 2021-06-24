#!/bin/bash

WEBAPP_HOME=$(dirname $(dirname $(readlink -f "$0")))
SCRIPTS_DIR=$(dirname $(readlink -f "$0"))
INSTANCE_HOME="$WEBAPP_HOME/instance"

# Install webapp
echo 'Installing webapp...'
$WEBAPP_HOME/setup.py install

echo 'Creating webapp service...'
sed -E 's+(ExecStart=)(.*)$+\1'"$SCRIPTS_DIR\/run.sh+" webapp.service > webapp.service
cp webapp.service /lib/systemd/system/

echo 'Creating log folder...'
mkdir -p /var/log/webapp
ln -s /var/log/webapp $INSTANCE_HOME/logs

echo 'Creating config...'
cp config.py $INSTANCE_HOME
read -p "Enter IP address of database host: " DATABASE
read -s -p "Enter database password: " PASSWORD
sed -E 's/(DATABASE_HOST\s*=\s*).*$/\1'"\'$DATABASE\'"'/' $INSTANCE_HOME/config.py > $INSTANCE_HOME/config.py
sed -E 's/(DATABASE_PASS\s*=\s*).*$/\1'"\'$PASSWORD\'"'/' $INSTANCE_HOME/config.py > $INSTANCE_HOME/config.py

echo 'Installing service...'
systemctl enable webapp

echo 'Starting service...'
systemctl start webapp

echo 'Done.'
