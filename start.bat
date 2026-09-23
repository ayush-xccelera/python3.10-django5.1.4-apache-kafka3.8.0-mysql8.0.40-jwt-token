@echo off
if not defined PORT set PORT=20550
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:%PORT%
