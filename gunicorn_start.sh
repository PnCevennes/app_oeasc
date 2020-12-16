#!/bin/bash

FLASKDIR=$(readlink -e "${0%/*}")

cd $FLASKDIR

. config/settings.ini


echo "Starting $app_name"

# activate the virtualenv
source venv/bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH

# # Start your unicorn
exec gunicorn server:app --error-log $FLASKDIR/var/log/errors_develop.log --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}"

echo done
