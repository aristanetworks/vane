#!/usr/bin/env python3
#
# Copyright (c) 2023, Arista Networks EOS+
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

"""
Collection of misc functions that dont fit anywhere else but are still required.
"""

import sys
import collections
import datetime


def make_iterable(value):
    """Converts the supplied value to a list object
    This function will inspect the supplied value and return an
    iterable in the form of a list.
    Args:
        value (object): An valid Python object
    Returns:
        An iterable object of type list
    """
    if sys.version_info <= (3, 0) and isinstance(value, str):
        # Convert unicode values to strings for Python 2
        value = str(value)
    if isinstance(value, (dict, str)):
        value = [value]

    if sys.version_info <= (3, 3):
        if not isinstance(value, collections.Iterable):
            raise TypeError("value must be an iterable object")
    else:
        if not isinstance(value, collections.abc.Iterable):
            raise TypeError("value must be an iterable object")

    return value


def get_current_fixture_testclass(request):
    """
    Method to get the name of the Test Function's class
    from the request fixture.
    Args: request - is the pytest request fixture
    Returns: Name of the test functions's class
    """

    nodeid = request.node.nodeid.split("::")
    test_class = nodeid[1] if len(nodeid) >= 2 else None
    return test_class


def get_current_fixture_testname(request):
    """
    Method to get the name of the Test Function
    from the request fixture.
    Args: request - is the pytest request fixture
    Returns: Name of the test function
    """

    nodeid = request.node.nodeid.split("::")
    test_name = nodeid[2] if len(nodeid) >= 3 else None
    return test_name.split("[")[0]


def remove_comments(input_string):
    """
    Method to remove a line that starts with #

    Args: input_string - string (possibly multiline)
    Returns: output_string - is the input_string with lines starting
    with # removed.
    """

    # if input_string is empty
    if not input_string:
        return input_string

    output_string_arr = []
    for line in input_string.splitlines():
        if not line.strip().startswith("#"):
            output_string_arr.append(line)

    output_string = "\n".join(output_string_arr)
    return output_string


def now():
    """Return current date and time"""

    return (datetime.datetime.now()).strftime("%d-%m-%Y %H:%M:%S")


def return_date():
    """Generate a formatted date and return to calling
    function.
    """

    date_obj = datetime.datetime.now()
    format_date = date_obj.strftime("%B %d, %Y %I:%M:%S%p")
    file_date = date_obj.strftime("%y%m%d%H%M")

    return format_date, file_date
