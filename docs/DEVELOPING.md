Regenerating test fixture data
------------------------------

Sometimes it may be useful to regenrate the `hmis-test-data.yaml` test fixture file. To do so, use the following command:

    src/manage.py dumpdata \
    	--natural-primary --natural-foreign --format yaml \
    	auth simplehmis > src/simplehmis/fixtures/hmis-test-data.yaml

Then, make sure the tests pass:

    src/manage.py test simplehmis

You may get a bunch of errors related to timezone after running the tests. This is due to how Django exports dates in YAML files. To fix, open *src/simplehmis/hmis-test-data.yaml* and perform the following find-and-replaces:

* `" (\d+-\d+-\d+ \d+:\d+:\d+(\.\d+)?\+00:00)"

  becomes

  `" '$1'"`

* `"! '(\d+-\d+-\d+[\n ]+\d+:\d+:\d+(\.\d+)?\+00:00)'"`

  becomes

  `"'$1'"`