#!/usr/bin/env bash

# Update the app supervisor configuration
foreman export supervisord . --log /home/ubuntu/simplehmis/log --app simplehmis --user nobody
# Explicitly run the server command with bash, so that
# environment variables are properly replaced.
sed -i 's/^command=\(.*\)$/command=bash -c "\1"/' simplehmis.conf
# Move the generated config file into the supervisor conf
# folder.
sudo mv simplehmis.conf /etc/supervisor/conf.d/

# Update the nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/simplehmis
sudo ln -fs /etc/nginx/sites-available/simplehmis /etc/nginx/sites-enabled/simplehmis

# Reload the app
sudo supervisorctl reread
sudo killall -HUP nginx
