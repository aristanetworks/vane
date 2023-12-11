# Vane Test Case Setup

## Getting Started with writing your own test cases

In this section, we will delve into various components
essential for crafting your own Vane test case.

### I. Creating a test definitions file

The test case definition file is a yaml file that resides in the
same folder as the test. Test case input is described in the test
case definition file. Below are the fields that make up a test case
definition and what they should be used for.

!!! example

    ``` yaml title=" Sample test_definitions.yaml"
    - name: test_memory.py
    testcases:
        - name: test_memory_utilization_on_
        test_id: TN1.1
        description: Verify memory is not exceeding high utilization
        show_cmd: show version
        # memory process ceiling
        expected_output: 80
        report_style: modern
        test_criteria: Verify memory is not exceeding high utilization
        # Optionally filter duts by criteria: name, role, regex, or names
        criteria: names
        filter: 
            - DSR01
            - DCBBW1
        comment: null
    ```

| Field       | Required  | Description                |
| ----------- | --------- | -------------------------- |
| name        |  Yes      |  Name of the test suite |
| testcases   |   Yes     |  List of test case definitions.
One per test case. Note this is one per test case not per
test suite. For example, if test_memory.py has 5 testcases,
a test case definition for each of the test cases is required. |
| name        |  Yes      |  Name of test case. This will appear
in the test report. Use underscores to separate words and Vane will
remove them when publishing a report. || test_id     | Yes      |
Unique identifier for test case. This will be published in a test report. |
|  description   |  Yes       | Describes the purpose of the test case
and what it's testing. This will be published in a test report. |
| show_cmd |    No       |  Some test cases have simple logic.
These test cases send a show command to EOS and then validate a field in
the operational data. For efficiency these commands can be run in batch
before test case execution. This field inputs commands needing batch execution.
If show output is available, Vane will report the show command and its
output in human readable text. || expected_output  |    No       |
User defined output to be used for test validation.
This will vary from test to test and may have many key value pairs.
It is not a required field for test cases that do not need a configurable
test criteria. It can be published to the test report depending on report
template || report_style       |     No      |  Reporting template
to use when creating output. Vane will default to original reporting without it.|
| test criteria   |   Yes        |  Details which the test case
will use to determine pass or fail. This will be published in a test report. |
| criteria | No | Criteria on the basis of which duts can be filtered.
Eg: Name, Role || filter | No | Values which should pass the criteria
mentioned above. || comment     |     No      |  Additional information
about the test case. It can be published to the test report depending on the
report template. Example comment is a test case that cannot run because a
requirement is not met.  This could be a hardware test for vEOS
instance, or not having expected software configurations like TACACS
not being configured for TACACS test. |

!!! eos-config "Note"

    There are other fields as well which can be explored by viewing the
    [sample network tests](../test_case_style_guide/sample_network_tests.md)

### II. Creating a test case file

!!! important
    The aim of this section is to help you get started with writing a test case
    that would make use of a variety of features that Vane provides. There are no
    hard and fast rules, and user should practice their discretion while making the
    choice depending on the testing use case. We will try diving a sample test case
    into sections and briefly describe what each section achieves.

    Example Test Case File

    ??? example "test_memory.py"

        #### Example Test Case File



        ``` python title=" Sample test file: test_memory.py"
        """ Tests to validate memory utilization."""

        import pytest
        from pyeapi.eapilib import EapiError
        from vane import tests_tools
        from vane import test_case_logger
        from vane.config import dut_objs, test_defs


        TEST_SUITE = "test_memory.py"
        LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

        dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
        test1_duts = dut_parameters["test_memory_utilization_on_"]["duts"]
        test1_ids = dut_parameters["test_memory_utilization_on_"]["ids"]

        logging = test_case_logger.setup_logger(__file__)


        @pytest.mark.demo
        @pytest.mark.nrfu
        @pytest.mark.platform_status
        @pytest.mark.memory
        @pytest.mark.virtual
        @pytest.mark.physical
        class MemoryTests:
            """Memory Test Suite"""

            @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
            def test_memory_utilization_on_(self, dut, tests_definitions):
                """TD: Verify memory is not exceeding high utilization

                Args:
                    dut (dict): Encapsulates dut details including name, connection
                    tests_definitions (dict): Test parameters
                """

                tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

                try:
                    """
                    TS: Run show command 'show version' on dut
                    """
                    self.output = dut["output"][tops.show_cmd]["json"]
                    assert self.output, "Memory details are not collected."
                    logging.info(
                        f"On device {tops.dut_name} output of
                        {tops.show_cmd} command is: {self.output}"
                    )

                    memory_total = self.output["memTotal"]
                    memory_free = self.output["memFree"]
                    tops.actual_output = (float(memory_free) /
                    float(memory_total)) * 100

                except (AssertionError, AttributeError, LookupError, EapiError)
                as exception:
                    logging.error(
                        f"Error occurred during the testsuite execution on dut: "
                        f"{tops.dut_name} is {str(exception)}"
                    )
                    tops.actual_output = str(exception)

                if tops.actual_output < tops.expected_output:
                    tops.test_result = True
                    tops.output_msg = (
                        f"On router {tops.dut_name} memory utilization
                        percent is "
                        f"{tops.actual_output}% which is correct as it is "
                        f"under {tops.expected_output}%"
                    )
                else:
                    tops.test_result = False
                    tops.output_msg = (
                        f"On router {tops.dut_name} the actual memory
                        utilization percent is "
                        f"{tops.actual_output}% while it should be under "
                        f"{tops.expected_output}%"
                    )

                tops.parse_test_steps(self.test_memory_utilization_on_)
                tops.generate_report(tops.dut_name, self.output)
                assert tops.actual_output < tops.expected_output

        ```

#### Import modules

Include modules such as pytest, eapi, and other relevant tools
from the Vane library like tests tools, test case logger, and
dut objects to be utilized in the test case.

``` python
import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane import test_case_logger
from vane.config import dut_objs, test_defs
```

#### Parameterization of Test Cases

All test cases should either be parametrized or should use
parameterized vane fixture. ‘dut’ is one such parameterized
vane fixture.

Parameterized test cases solve the problem of grouping duts based on
name(s), name regex, or role. It can be easily extended to any other
dut property defined in duts.yaml. The test definition file will be used
to express a filtering criteria and a filter.
2 new key, value pairs (criteria, filter) will be introduced into a
test definition for this. These values are optional.

| key | type (of the value)  | value |
| ----------- | -------------------------- | -------------------------- |
criteria | string |Specifies the filtering criteria.  Valid criteria are:
name (scenario 1), role (scenario 2), names (scenario 3),
regex (scenario 4). If the criteria field is empty or does not match a
valid criteria, all duts will be tested (scenario 5). *Scenarios are shown below.*
|filter |string |Filter based on a DUT name.
There must be an exact match between
the DUT’s name in the duts.yaml file.|
|filter|string |Filter based on a role name.
There must be an exact match between
the role’s name in the duts.yaml file. |
|filter |list |Filter based on a list of roles.
There must be an exact match between
each role and the duts.yaml file.|
|filter | list | Filter based on a list of DUT names.
There must be an exact match
between each DUT’s name and the duts.yaml file. |
|filter | string | Filter based on a regular expression.
Regular expression  will
match all DUT’s names in the duts.yaml file that are valid. |

Six current scenarios exists for filtering DUTs:

- Scenario 1: Filter a single DUT named BLW1

    ``` yaml hl_lines="5-6"
    - name: test_1_sec_cpu_utlization_on_
    description: Verify 1 second CPU % is under specificied value
    show_cmd: show processes
    expected_output: 1
    criteria: name
    filter: BLW1
    ```

- Scenario 2: Filter all DUTs with role leaf

    ``` yaml hl_lines="5-6"
    - name: test_1_min_cpu_utlization_on_
    description: Verify 1 minute CPU % is under specificied value
    show_cmd: show processes
    expected_output: 10
    criteria: role
    filter: leaf
    ```

- Scenario 3: Filter  multiple DUTs named BLE2, BLW1

    ``` yaml hl_lines="5-8"
    - name: test_5_min_cpu_utlization_on_
    description: Verify 5 minute CPU % is under specificied value
    show_cmd: show processes
    expected_output: 10
    criteria: names
    filter:
        - BLE2
        - BLW1
    ```

- Scenario 4: Filter using a regular expression DUTs named BLE1, BLE2

    ``` yaml hl_lines="5-6"
    - name: test_1_sec_cpu_utlization_on_
    description: Verify 1 second CPU % is under specificied value
    show_cmd: show processes
    expected_output: 1
    criteria: name
    regex: BLE[1|2]
    ```

- Scenario 5: Filter all DUTs with roles spine and leaf

    ``` yaml hl_lines="5-8"
    - name: test_1_min_cpu_utlization_on_
    description: Verify 1 minute CPU % is under specified value
    show_cmd: show processes
    expected_output: 10
    criteria: role
    filter: 
        - leaf
        - spine
    ```

- Scenario 6: All DUTs, this is the default setting and no additional
  information needs to be added to the test definition file.

!!! important

    The following additions will have to be made to the test case file in order
    to parameterize the test case.

- The global duts object (dut_objs) and global test definitions (test_defs)
  are required for input.

    ``` python
    from vane.config import dut_objs, test_defs
    ```

- The method parametrize_duts must be run to create the input for a
    parameterized test. TEST_SUITE is passed to the method so the test
    suite’s definitions can be discovered in test_defs.  Test_defs
    contains the filter and criteria key, value pairs for each test case.
    The filter is executed against the duts_objs to create a subset of DUTs.

    The dut_parameters data structure returns parameters for all test keys.
    The data structure is a dictionary and organized by test case name.
    Each test case name contains the subset of duts and a list dut names.
    Below shows the data structure:

    ``` yaml
    { “test case name 1” :
        “duts”: {subset of duts 1}
        “ids”: [subset of duts names 1]
    },
    { “test case name 2” :
        “duts”: {subset of duts 2}
        “ids”: [subset of duts names 2]
    },
    …
    { “test case name N” :
        “duts”: {subset of duts N}
        “ids”: [subset of duts names N]
    },
    ```

    Lines 4, 5 are optional and are added for better readability
    in the parameterized decorator.

    ``` python linenums="1"
    TEST_SUITE = "test_memory.py"

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test1_duts = dut_parameters["test_memory_utilization_on_"]["duts"]
    test1_ids = dut_parameters["test_memory_utilization_on_"]["ids"]
    ```

- A parameterized decorator is added to each test. The second value
    is the subsets of duts that the parameterized decorator
    will iterate over. This was provided by the dut_parameters
    variable. The first value is the name assigned to the dut_parameter
    iteration and it is passed to the function definition.
    The third value is a list of names PyTest will display on test
    case iteration.

    ``` python
    class MemoryTests:
    """Memory Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_memory_utilization_on_(self, dut, tests_definitions):
    ```

#### Creating test case logs

Test cases can make use of the logging functionality to make logs
of various levels. We provide an inbuilt logger which can be
invoked and used as follows. The logs created by it get generated
in the **logs** folder and stored by the test case file name
within the outermost cloned vane directory.

```python
# Import the logger module
from vane import test_case_logger

# Set the logger with the test case file name
logging = test_case_logger.setup_logger(__file__)

# Invoke and make the logs
logging.info("This is an info log")
logging.debug("This is a debug log")
logging.warning("This is a warning log")
logging.error("This is an error log")
```

!!! eos-config "Note"
    By default the debug logs do not get logged, but this can be
    changed by changing the log levels within the
    [test case logger file]
    (https://github.com/aristanetworks/vane/blob/4f2775ca0af0496ec23095a9f8dc72bddf269e5b/vane/test_case_logger.py#L14)

#### Using markers

In Pytest, markers are a way to add metadata or labels to your test functions.
You can use markers to group tests together.
For example, you might have markers like @pytest.mark.nrfu or @pytest.mark.memory
to categorize tests based on their purpose.

``` python
    @pytest.mark.demo
    @pytest.mark.nrfu
    @pytest.mark.platform_status
    @pytest.mark.memory
    @pytest.mark.virtual
    @pytest.mark.physical
    class MemoryTests:
```

You can now run specific groups of tests using markers. For example,
if you only want to run nrfu tests, you can add the **nrfu** marker
in the [definitions.yaml markers field]
(https://github.com/aristanetworks/vane/blob/4c29cb4dba48ad312699b88e91a3f398b7dae81a/sample_network_tests/definitions.yaml#L11).

!!! tip

    You can use the --markers flag in Vane to see the markers supported by Vane

Markers make it easy to organize and manage your tests,
especially in larger test suites where you might have various
types of tests with different requirements.

!!! info

    You can see the official documentation of Pytest
    [Markers](https://docs.pytest.org/en/7.1.x/example/
    markers.html#marking-test-functions-and-selecting-them-for-a-run) here.

#### Integrating the test case logic

This is the actual crux of your test case. Its the testing logic which is woven
through the test case. It consists
of 3 main sections.

!!! eos-config "Note"

    In the example below we are checking if memory utilization is below a certain
    threshold by using the output from
    show version command

- Gathering and processing test data

    The tops object consists of all the essential data that gets used during
    a test case. Look at the
    [TestOps API section](../api_cli/api.md#vane-api) to get an idea of the
    different features available on the tops object.

    ``` python
    tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
    try:
        """
        TS: Run show command 'show version' on dut
        """
        self.output = dut["output"][tops.show_cmd]["json"]
        assert self.output, "Memory details are not collected."
        logging.info(
            f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
        )

        memory_total = self.output["memTotal"]
        memory_free = self.output["memFree"]
        tops.actual_output = (float(memory_free) / float(memory_total)) * 100

    except (AssertionError, AttributeError, LookupError, EapiError) as exception:
        logging.error(
            f"Error occurred during the testsuite execution on dut: "
            f"{tops.dut_name} is {str(exception)}"
        )
        tops.actual_output = str(exception)
    ```

- Comparing Actual and Expected data

    ``` python
    if tops.actual_output < tops.expected_output:
        tops.test_result = True
        tops.output_msg = (
            f"On router {tops.dut_name} memory utilization percent is "
            f"{tops.actual_output}% which is correct as it is "
            f"under {tops.expected_output}%"
        )
    else:
        tops.test_result = False
        tops.output_msg = (
            f"On router {tops.dut_name} the actual memory utilization
            percent is "
            f"{tops.actual_output}% while it should be under "
            f"{tops.expected_output}%"
        )
    ```

- Asserting test result.

    ``` python
    assert tops.actual_output < tops.expected_output
    ```

!!! eos-config "Note"

    As mentioned before this organization would  differ for each test case
    and user's discretion should be used while writing this section.
    The examples above refer to our sample network tests but your specific
    test case could be very different.

#### Generating test case reports

Vane produces diverse reports in formats such as .json, .html, and .docx.
By invoking the [generate_report api](../api_cli/api.md), all
pertinent test data is appended to the test object. This data is subsequently
utilized when generating documentation reports through a call to the
[write_results](https://github.com/aristanetworks/vane/blob/4c29cb4dba48ad312699b88e91a3f398b7dae81a/vane/vane_cli.py#L157)
method after the test case has finished executing.

Additionally, the generate_report method is responsible for generating
evidence files that exhibit various **show commands** and their
corresponding outputs from the devices. These evidence files are crafted
and stored in the reports/TEST RESULTS folder.

Finally, the generate_report method invokes another function to
generate HTML reports containing the results of the test cases.

=== "Call to generate report in the test case"
    ``` python
    tops.generate_report(tops.dut_name, self.output)
    ```
=== "generate_report in tests_tools.py"
    ``` python hl_lines="31-33"
    def generate_report(self, dut_name, output):
    """Utility to generate report

    Args:
        dut_name (str): name of the device
    """
    logging.debug(f"Output on device {dut_name} after SSH connection is: {output}")

    self.test_parameters["comment"] = self.comment
    self.test_parameters["test_result"] = self.test_result
    self.test_parameters["output_msg"] = self.output_msg
    self.test_parameters["actual_output"] = self.actual_output
    self.test_parameters["expected_output"] = self.expected_output
    self.test_parameters["dut"] = self.dut_name
    self.test_parameters["show_cmd"] = self.show_cmd
    self.test_parameters["test_id"] = self.test_id
    self.test_parameters["show_cmd_txts"] = self._show_cmd_txts
    self.test_parameters["test_steps"] = self.test_steps
    self.test_parameters["show_cmds"] = self._show_cmds
    self.test_parameters["skip"] = self.skip

    if str(self.show_cmd_txt):
        self.test_parameters["show_cmd"] += ":\n\n" + self.show_cmd_txt

    self.test_parameters["test_id"] = self.test_id
    self.test_parameters["fail_or_skip_reason"] = ""

    if not self.test_parameters["test_result"]:
        self.test_parameters["fail_or_skip_reason"] = self.output_msg

    self._html_report()
    self._write_results()
    self._write_text_results()
    ```
=== "write_results in vane_cli.py"
    ``` python
    def write_results(definitions_file):
    """Write results document

    Args:
        definitions_file (str): Path and name of definition file
    """
    logging.info("Using class ReportClient to create vane_report_client object")

    vane_report_client = report_client.ReportClient(definitions_file)
    vane_report_client.write_result_doc()
    ```

!!! Tip
    You can view the different kinds of reports that Vane generates in the
    [Executing Vane](../executing_vane/executing_vane.md#viewing-reports-generated-by-vane)section

#### Generating test case steps

Vane offers the capability to record test steps, facilitating later use for
reporting. To record and generate test steps within a test case, employ
the following syntax.

=== "test steps in a test case"

    ```python hl_lines="3 13-15 35-37 52-54 56"
        @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
        def test_if_hostname_is_correcet_on_(self, dut, tests_definitions):
            """TD: Verify hostname is set on device is correct

            Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
            """

            tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

            try:
                """
                TS: Collecting the output of 'show hostname' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                assert self.output.get("hostname"), "Show hostname details
                are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd}
                    command is: {self.output}"
                )

                tops.expected_output = {"hostname": tops.dut_name}
                tops.actual_output = {"hostname": self.output["hostname"]}

            except (AttributeError, LookupError, EapiError) as exp:
                tops.actual_output = str(exp)
                logging.error(
                    f"On device {tops.dut_name}: Error while running
                    testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating hostname name. Vane recorded error: {exp} "
                )

            """
            TS: Verify LLDP system name
            """
            if tops.actual_output == tops.expected_output:
                tops.test_result = True
                tops.output_msg = (
                    f"On router {tops.dut_name} the hostname is correctly "
                    f"set to {tops.expected_output['hostname']}"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"On router {tops.dut_name} the hostname is incorrectly "
                    f"set to {tops.actual_output['hostname']}.
                    Hostname should be set "
                    f"to {tops.expected_output['hostname']}"
                )

            """
            TS: Creating test report based on results
            """

            tops.parse_test_steps(self.test_if_hostname_is_correct_on_)
            tops.generate_report(tops.dut_name, self.output)
            assert tops.actual_output == tops.expected_output
    ```

!!! tip
    Additionally, besides generating test steps from within a test
    case you can also create .md and .json version of the test steps
    independently (without having to run a test case). We've outlined how you
    could achieve that using the --generate-test-steps flag in the
    [Vane CLI section](../api_cli/cli.md#using-the----generate-test-steps-flag).
