@echo off
python -m venv venv
call .\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
mysql -u root -p0000 -e "CREATE DATABASE IF NOT EXISTS leafy;"
mysql -u root -p0000 leafy < leafy.sql
pause
