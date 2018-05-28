#!/bin/bash
set -e

source venv/bin/activate

if [ "$1" == "run" ]
then
    exec scrapyd
elif [ "$1" == "pump" ]
then
    exec python test.py
fi

exec "$@"
