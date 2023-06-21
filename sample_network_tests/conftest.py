#!/usr/bin/env python3
#
# Copyright (c) 2019, Arista Networks EOS+
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Arista nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

""" Alter behavior of PyTest """

import re
import pytest
from py.xml import html

pytest_plugins = ("vane.fixtures")


def pytest_addoption(parser):
    """Receive command line value from pytest

    Args:
        parser (str): Command line value from pytest
    """

    parser.addoption(
        "--definitions",
        action="store",
        default="definitons.yaml",
        help="my option: type1 or type2",
    )


@pytest.fixture
def definitions(request):
    """Place holder for passing args to test

    Args:
        request (str): Pass value to test

    Returns:
        [str]: Pass value to test
    """

    cli_arg = request.config.getoption("--definitions")
    return cli_arg


def find_nodeid(nodeid):
    """Return device parameter

    Args:
        nodeid (str): Device Name

    Return: Name of device

    """

    if re.match(r".*\[(.*)\]", nodeid):
        return re.match(r".*\[(.*)\]", nodeid)[1]
    else:
        return "NONE"


def pytest_html_results_table_header(cells):
    """Create custom PyTest-HTML Header Row

    Args:
        cells: Cell data
    """

    cells.insert(2, html.th("Description"))
    cells.insert(1, html.th("Device", class_="sortable string", col="device"))
    cells.pop()


def pytest_html_results_table_row(report, cells):
    """Create custom PyTest-HTML report row

    Args:
        report: pytest report
        cells: Cell data
    """

    cells.insert(2, html.td(getattr(report, 'description', '')))
    cells.insert(1, html.td(find_nodeid(report.nodeid), class_="col-device"))
    cells.pop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Called to create a _pytest.reports.TestReport for each of the setup,
    call and teardown runtest phases of a test item.

    """

    outcome = yield
    report = outcome.get_result()

    if str(item.function.__doc__).split("Args:")[0]:
        report.description = str(item.function.__doc__).split("Args:")[0]
    elif str(item.function.__doc__):
        report.description = str(item.function.__doc__)
    else:
        report.description = "No Description"

