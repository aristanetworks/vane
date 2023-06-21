import vane.tests_client as tests_client

DEFINITIONS = 'sample_network_tests/definitions.yaml'
DUTS = 'sample_network_tests/duts.yaml'
def test_assert():
    assert True

def test_object_creation():
    """ Verify spreadsheet can be inputted
    """

    _ = tests_client.TestsClient(DEFINITIONS, DUTS)
