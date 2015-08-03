#!/usr/bin/env bash

# === When the machine is first created...

# Update & upgrade the system files
sudo apt-get update
sudo apt-get upgrade -y

# Install the source
sudo apt-get install git -y
sudo apt-get install python-virtualenv
sudo apt-get install ruby  # For foreman
sudo gem install foreman

# Download the source and set up the app folder
cd /srv
sudo git clone https://github.com/CityOfPhiladelphia/simplehmis.git
sudo chown -R ubuntu simplehmis/
sudo chgrp -R ubuntu simplehmis/

# Enter the app folder
cd simplehmis

# Create the log folder
mkdir log

# Create the virtual environment
virtualenv . --python=python3
# ...to activate the virtual environment whenever you log
# on to the machine.
echo "source /srv/simplehmis/bin/activate" >> ~/.bashrc
echo "echo \"***\"" >> ~/.bashrc
echo "echo \"*** SimpleHMIS application root is in /srv/simplehmis/\"" >> ~/.bashrc
echo "echo \"***\"" >> ~/.bashrc
# ...to reload the bash environment.
source ~/.bashrc

cat > .git/hooks/post-update <<EOF
#!/usr/bin/env bash

cd ..
sudo apt-get update
sudo apt-get upgrade -y
./update-machine
EOF

echo ""
echo "***"
echo "Next, copy the .env.template file to .env, and configure your environment variables."
echo ""
echo "After you've configured the environment, run the ./update-machine.sh command. This command will be re-run every time you pull from github."
echo "***"