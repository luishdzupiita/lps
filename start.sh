#!/bin/bash

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn project.wsgi:application \
    --bind 0.0.0.0:80 \
    --timeout 1800 \
    --log-level=debug \
    --workers 3
