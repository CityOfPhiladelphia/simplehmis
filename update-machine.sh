#!/usr/bin/env bash

# === After each pull...
echo
echo "=== Update & upgrade all dependencies..."
echo

echo "    Install system dependencies..."
sudo apt-get install libpq-dev -y  # For psycopg2. If I could just not install psycopg2...
sudo apt-get install supervisor -y
sudo apt-get install nginx -y

echo "    Make sure library dependencies are installed..."
cd /srv/simplehmis
pip install -r requirements.txt

echo "    Update the app database..."
foreman run src/manage.py migrate --noinput
foreman run src/manage.py loaddata staff-groups

echo "    Update the app static files..."
foreman run src/manage.py collectstatic --noinput

./restart-server.sh
