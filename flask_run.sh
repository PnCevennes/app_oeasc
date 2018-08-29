
export FLASK_APP=server.py
export FLASK_ENV=development


ROOT_DIR=$(readlink -e "${0%/*}")

# export PYTHONPATH=$PYTHONPATH:$ROOT_DIR/app

echo $PYTHONPATH


source $ROOT_DIR/venv/bin/activate
flask run --host=0.0.0.0
