#!/usr/bin/env bash

# Update the app supervisor configuration
foreman export supervisord . --log /home/ubuntu/simplehmis/log --app simplehmis --user nobody
sed -i 's/^command=\(.*\)$/command=bash -c "\1"/' simplehmis.conf
sudo mv simplehmis.conf /etc/supervisor/conf.d/

# Update the nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/simplehmis
sudo ln -fs /etc/nginx/sites-available/simplehmis /etc/nginx/sites-enabled/simplehmis

# Reload the app
sudo supervisorctl reread
sudo killall -HUP nginx
