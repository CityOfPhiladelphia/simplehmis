#!/usr/bin/env bash

echo
echo "=== Restarting the server..."
echo

# Supervisor configuration
# ------------------------
echo "    Updating the supervisor configuration..."
foreman export supervisord . --log /srv/simplehmis/log --app simplehmis --user nobody
# Explicitly run the server command with bash, so that
# environment variables are properly replaced.
sed -i 's/^command=\(.*\)$/command=bash -c "\1"/' simplehmis.conf
# Move the generated config file into the supervisor conf
# folder.
sudo mv simplehmis.conf /etc/supervisor/conf.d/

# Nginx configuration
# -------------------
echo "    Updating the nginx configuration"
sudo cp nginx.conf /etc/nginx/sites-available/simplehmis
sudo ln -fs /etc/nginx/sites-available/simplehmis /etc/nginx/sites-enabled/simplehmis

# Restart the server processes
# ----------------------------
echo "    Restarting the supervisor & nginx..."
sudo supervisorctl reread
sudo supervisorctl restart simplehmis:*
sudo killall -HUP nginx
