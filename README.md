simpleHMIS
==========

The main point of this project is to allow partner programs to enter those [Universal Data Elements](https://www.hudexchange.info/hmis/hmis-data-and-technical-standards/#elements) required by HUD. As such, it is currently not and does not try to be a full homeless management information system (HMIS) as specified by HUD.

As noted by HUD:

> Universal data elements enable the HMIS the ability to record unique, unduplicated client records, establish participation in a project within a date range, and identify clients who meet time criteria for chronic homelessness.


Setting Up
----------

To get the project set up and configured, first create and load a virtual environment for the project. There are several ways to do this and it is an optional but recommended step. Here's one way:

    virtualenv env -p python3
    source env/bin/activate

Now, install the project requirements:

    pip install -r requirements.txt

Next, set up the database and initialize the data:

    src/manage.py migrate
    src/manage.py loaddata staff-groups.yaml

Finally, load information specific to your structure. This could include: partner projects, project staff, etc. For information on doing that, run `src/manage.py load_projects -h`. As a superuser user you can always add this data manually. You can create a new superuser with the `src/manage.py createsuperuser` command.