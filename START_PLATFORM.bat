@echo off
set DJANGO_SETTINGS_MODULE=core.settings.dev
echo Starting DevHub Platform...
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
