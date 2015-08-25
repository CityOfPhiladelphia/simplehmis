Configuring Email
-----------------

SimpleHMIS uses email for transactional tasks (logging users in) and administrative tasks (sending onboarding instructions and other mass communication to site users).

The default settings use Django's `console.EmailBackend`. This will output email data into the stream of console logs. This is useful for developing locally.

In order to send real emails, you must configure SimpleHMIS to use an SMTP server by settings several environment variables:

    EMAIL_HOST
    EMAIL_PORT
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL

It is also recommended that you use SSL or TLS to send your emails. Set either the `EMAIL_USE_SSL` or `EMAIL_USE_TLS` environment variable to `True`. See the Django [documentation](https://docs.djangoproject.com/en/1.8/ref/settings/#email-use-tls) for more information on each option.


Regenerating test fixture data
------------------------------

Sometimes it may be useful to regenrate the `hmis-test-data.yaml` test fixture file. To do so, use the following command:

    src/manage.py dumpdata \
    	--natural-primary \
    	--natural-foreign \
    	--format yaml \
    	auth simplehmis > src/simplehmis/fixtures/hmis-test-data.yaml

Then, make sure the tests pass:

    src/manage.py test simplehmis

You may get a bunch of warnings related to timezone after running the tests. This is due to how Django exports dates in YAML files. The test data is functional even with these warnings, but they can get annoying. To fix, open *src/simplehmis/hmis-test-data.yaml* and perform the following find-and-replaces:

* `" (\d+-\d+-\d+ \d+:\d+:\d+(\.\d+)?\+00:00)"`

  becomes

  `" '$1'"`

* `"! '(\d+-\d+-\d+[\n ]+\d+:\d+:\d+(\.\d+)?\+00:00)'"`

  becomes

  `"'$1'"`