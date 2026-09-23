#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
export PORT="${PORT:-20550}"
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -r requirements.txt -q
python3 manage.py migrate --noinput
exec python3 manage.py runserver 0.0.0.0:$PORT
