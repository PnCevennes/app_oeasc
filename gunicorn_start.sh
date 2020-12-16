#!/bin/bash

readlink -e "${0%/*}"


FLASKDIR=$(pwd)
FLASKDIR=$(readlink -e "${0%/*}")

echo FLASKDIR $FLASKDIR
. "$FLASKDIR"/config/settings.ini

echo "Starting OEASC"

# activate the virtualenv
echo cd $FLASKDIR/venv
cd $FLASKDIR/venv
source bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH

# cd $FLASKDIR
echo $PYTHONPATH


# # Start your unicorn
exec gunicorn  server:app --error-log $FLASKDIR/var/log/errors_develop.log --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}"

echo done
