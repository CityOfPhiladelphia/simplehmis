simpleHMIS
==========

[![Build Status](https://travis-ci.org/CityOfPhiladelphia/simplehmis.svg?branch=master)](https://travis-ci.org/CityOfPhiladelphia/simplehmis)
[![Stories in Ready](https://badge.waffle.io/CityOfPhiladelphia/simplehmis.png?label=ready&title=Ready)](https://waffle.io/CityOfPhiladelphia/simplehmis)

The main point of this project is to allow partner programs to enter those [Universal Data Elements](https://www.hudexchange.info/hmis/hmis-data-and-technical-standards/#elements) required by HUD. As such, it is currently not and does not try to be a full homeless management information system (HMIS) as specified by HUD.

As noted by HUD:

> Universal data elements enable the HMIS the ability to record unique, unduplicated client records, establish participation in a project within a date range, and identify clients who meet time criteria for chronic homelessness.


Setting Up For Development
--------------------------

To get the project set up and configured, first create and load a virtual environment for the project. There are several ways to do this and it is an optional but recommended step. Here's one way:

    virtualenv env -p python3
    source env/bin/activate

Now, install the project requirements:

    pip install -r requirements.txt

These next commands will set up the database and initialize the data. If you are setting up a test or development instance, the default database connection settings should be sufficient (using [SQLite](https://www.sqlite.org/)). For production (or near-production staging) environments, create your database and set an environment variabled named `DATABASE_URL` to a [connection string](https://github.com/kennethreitz/dj-database-url#url-schema) for that database.

Install the schema and initial data into your database:

    src/manage.py migrate
    src/manage.py loaddata staff-groups.yaml

Finally, load information specific to your structure. This could include: partner projects, project staff, etc. For information on doing that, run `src/manage.py load_projects -h`. As a superuser user you can always add this data manually. You can create a new superuser with the `src/manage.py createsuperuser` command.

For testing convenience, you can load some test data if you just want to get started. This includes a few projects, an intake staff user with username `'intake-admin'`, and two project staff users with usernames `'project-admin1'` and `'project-admin2'`.

    src/manage.py loaddata hmis-test-data.yaml



Deploying to an EC2 instance, or a droplet, etc.
------------------------------------------------

Run the `init-machine.sh` script and your environment should get configuerd correctly.

In order to send login emails, set up Amazon SES (or another SMTP email service), and add the following variables to your environment:

    EMAIL_HOST
    EMAIL_PORT
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL

It is also recommended that you use SSL or TLS to send your emails. Set either the `EMAIL_USE_SSL` or `EMAIL_USE_TLS` environment variable to `True`.

The `DEFAULT_FROM_EMAIL` must be an address able to send mail for the given user on the given host.
