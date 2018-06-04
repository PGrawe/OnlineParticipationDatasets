#!/bin/bash
set -e

source venv/bin/activate

until nc -z -w 5 $CONTENT_HOST $CONTENT_PORT; do
    sleep 1
done

if [ "$1" == "run" ]
then
    exec scrapyd
elif [ "$1" == "pump" ]
then
    exec python crawl_scheduler.py
fi

exec "$@"
