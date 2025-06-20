#!/usr/bin/env bash
set -e

source /home/pdlab/labook/venv/bin/activate
cd /home/pdlab/labook
exec gunicorn \
  --workers 9 \
  --bind 127.0.0.1:5000 \
  app:app
