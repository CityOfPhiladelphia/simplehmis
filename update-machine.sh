#!/usr/bin/env bash

# === After each pull...

# Update & upgrade the system files
sudo apt-get update
sudo apt-get upgrade -y

# Install application dependencies
sudo apt-get install libpq-dev -y  # For psycopg2. If I could just not install psycopg2...
sudo apt-get install supervisor -y
sudo apt-get install nginx -y

# Enter the app folder
cd /srv/simplehmis
pip install -r requirements.txt

# Update the app database
foreman run src/manage.py migrate --noinput
foreman run src/manage.py loaddata staff-groups

# Update the app static files
foreman run src/manage.py collectstatic --noinput

./restart-server.sh
