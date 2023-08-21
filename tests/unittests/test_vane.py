"""vane unit tests"""
from vane import tests_client

DEFINITIONS = "tests/unittests/fixtures/fixture_definitions.yaml"
DUTS = "tests/unittests/fixtures/fixture_duts.yaml"


def test_object_creation():
    """Verify spreadsheet can be inputted"""

    _ = tests_client.TestsClient(DEFINITIONS, DUTS)
