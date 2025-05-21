@echo off

REM Atualizar pip
python.exe -m pip install --upgrade pip

REM Instalar pacotes Python do requirements.txt
pip install -r requirements.txt

REM Configurar banco de dados MySQL
mysql -u root -p0000 -e "CREATE DATABASE IF NOT EXISTS leafy;"
mysql -u root -p0000 leafy < leafy.sql

pause
