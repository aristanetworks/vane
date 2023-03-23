import pytest, sys
from vane import vane_cli
import logging
 
logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)


def test_parse_cli():

    output = vane_cli.parse_cli() 
    print(output)
    sys.stderr.write("Example 3")
    log.warning('Error: Hello World')

    #validating if number of arguments parsed is correct
    actual_number_of_arguments = 7
    expected_number_of_arguments = len(vars(output))
    assert actual_number_of_arguments == expected_number_of_arguments 

    #validating if default values are set correctly via the config file
    definitions_file = "definitions.yaml"
    duts_file = "duts.yaml"
    environment = "test"
    generate_duts_file = None
    generate_duts_from_topo = None
    generate_test_steps = None
    markers = False

    assert definitions_file == output.definitions_file
    assert duts_file == output.duts_file
    assert environment == output.environment
    assert generate_duts_file == output.generate_duts_file
    assert generate_duts_from_topo == output.generate_duts_from_topo
    assert generate_test_steps == output.generate_test_steps
    assert markers == output.markers

def test_setup_vane():
    assert 0 == 0


    



