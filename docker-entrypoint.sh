#!/bin/bash
set -e

source venv/bin/activate

if [ "$1" == "run" ]
then
    exec scrapyd
fi

exec "$@"
