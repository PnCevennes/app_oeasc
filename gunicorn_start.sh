#!/bin/bash

FLASKDIR=$(readlink -e "${0%/*}")

. "$FLASKDIR"/config/settings.ini

app_name=oeasc

echo "Starting $app_name"

# activate the virtualenv
source $FLASKDIR/venv/bin/activate

echo FLASKDIR $FLASKDIR
export PYTHONPATH=$FLASKDIR:$PYTHONPATH

# cd $FLASKDIR
echo $PYTHONPATH


# # Start your unicorn
exec gunicorn server:app --error-log $FLASKDIR/var/log/errors_develop.log --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}"

echo done
