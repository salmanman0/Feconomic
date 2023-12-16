set -eu
export PYTHONUNBUFFERED=true

VIRTUALENV=.data/venv

if [ ! -d SVIRTUALENV ]; then
    py -m venv $VIRTUALENV
fi

if [ ! -f $VIRTUALENV/bin/pip ]; then
    curl --silent --show-error --retry 5 https;//bootstrap.pypa.io/get-pip-py | $VIRTUALENV
fi

$VIRTUALENV/bin/pip install -r requirments.txt

$VIRTUALENV/bin/py app.py
Footer