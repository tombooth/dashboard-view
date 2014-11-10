import json

from hamcrest import assert_that, equal_to

from performanceplatform.view.dashboard.formatting import format


def test_spec_formats():
    with open("tests/fixtures/format.spec.json") as spec_file:
        specs = json.load(spec_file)

        for spec in specs:
            assert_that(
                format(spec['input'], spec['format']),
                equal_to(spec['output']))
