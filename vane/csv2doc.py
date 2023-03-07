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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE AR
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

""" Utility script for taking a manual testing spreadsheet and converting it
    it into a formattted word doc.

    Input Variables:
        CSVFILE (str): Path + file name for CSV input data
        DOCFILE (str): Path + file name for output Word doc
        TESTCASE_ID (int): CSV column number with test case ID
        CASE_NAME (int): CSV column  number with test case name
        PROCEDURE (int): CSV column  number with test steps / procedures
        EXPECTED_RESULT (int): CSV column  number with test criteria
        PASS_FAIL (int): CSV column  number with test status: pass or fail
        OBSERVATION (int): CSV column  number with test completion note
"""

import csv
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.text import WD_COLOR_INDEX

# GLOBAL Variables
# test suite header
TEST_SUITE_HEADER = r"\d{1,2}\.\d{1,2}"
# Input Variables
# Name of CSV to use for test output
CSVFILE = "../Arista Agora Test Plan V9.3 - EOS Test Items.csv"
DOCFILE = "../test_summary_results.docx"
# Column number of interesting values
TESTCASE_ID = 0  # column A
CASE_NAME = 2  # column C
PROCEDURE = 16  # column Q
EXPECTED_RESULT = 17  # column R
PASS_FAIL = 13  # column N
OBSERVATION = 14  # column O


def parse_csv():
    """Open and parse CSV data and find test data

    Returns:
        list: List of interesting test data
    """
    print(f"Parsing CSV file: {CSVFILE} for test data...")

    # open csv
    with open(CSVFILE, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        # regex for matching a test suite header
        test_data = inspect_csv_data(csv_reader)

    return test_data


def inspect_csv_data(csv_reader):
    """Inspect each row of CSV data and determine if its interesting

    Args:
        csv_reader (obj): CSV object to iterate through

    Returns:
        list: List of interesting test data
    """

    test_data = []

    for row in csv_reader:
        test_data_entry = []
        # parse csv row for a test case ids
        if "TN" in row[TESTCASE_ID]:
            test_data_entry.append(row[TESTCASE_ID])
            test_data_entry.append(row[CASE_NAME])
            test_data_entry.append(row[PROCEDURE])
            test_data_entry.append(row[EXPECTED_RESULT])
            test_data_entry.append(row[PASS_FAIL])
            test_data_entry.append(row[OBSERVATION])

            # raw data entry for output data
            test_data.append(test_data_entry)
        # parse csv row for header
        elif re.match(TEST_SUITE_HEADER, row[CASE_NAME]):
            test_data_entry.append(row[CASE_NAME])
            test_data.append(test_data_entry)

    return test_data


def write_report(test_data):
    """Write word doc with test data collected from CSV

    Args:
        test_data (list): List of interesting test data
    """
    print(f"Writing report doc: {DOCFILE}")

    # Open doc
    document = docx.Document()
    # Change doc margins
    section = document.sections[0]
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    write_header(document)
    write_results_table(document, test_data)

    doc_text = (
        "\n\n\nPlease note – for more details on test outputs please "
        "reference the test case output appendix docs.\n"
    )
    write_text(document, doc_text)

    # Close doc
    document.save(DOCFILE)


def write_header(document):
    """Write test section header to word doc

    Args:
        document (obj): Test report Word doc
        test_data (list): List of interesting test data
    """

    # Write summary header
    heading = document.add_heading(level=2)
    run = heading.add_run("4	Test Summary Result")
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(204, 0, 0)

    # Header text
    doc_text = (
        "\nTest Cases for Arista BAU Hardware & EOS 4.27.2F Certification. "
        "Please note – for more details on test outputs please reference "
        "the test case output appendix docs.\n\n\n"
    )
    write_text(document, doc_text)


def write_text(document, doc_text, font_pt=10, font="Arial"):
    """Write a paragraph to Word Doc

    Args:
        document (obj): Word doc object
        doc_text (str): Text to write to doc
        pt (int): Word font size
        font (string): Word font style
    """
    para = document.add_paragraph()
    run = para.add_run(doc_text)
    run.font.size = Pt(font_pt)
    run.font.name = font


def write_header_row(table):
    """Write the header row for the result table

    Args:
        table (obj): Word doc table object
    """

    headers = [
        "Test Case",
        "Case Name",
        "Procedure",
        "Expected result",
        "Pass/Fail",
        "Observation",
    ]

    # Write header row in table
    for count, header in enumerate(headers):
        para = table.rows[0].cells[count].paragraphs[0]

        cell = table.cell(0, count)
        run = para.add_run(header)
        run.font.name = "Arial"
        run.font.size = Pt(9)
        run.font.bold = True

        cell = table.cell(0, count)

        shading_blue = parse_xml(
            # pylint: disable-next=consider-using-f-string
            r'<w:shd {} w:fill="00FFFF"/>'.format(nsdecls("w"))
        )
        # pylint: disable-next=protected-access
        cell._tc.get_or_add_tcPr().append(shading_blue)


def write_results_table(document, test_data):
    """Write results table to Word doc

    Args:
        document (obj): Word doc object
        test_data (list): List of interesting test data
    """

    # create table
    table = document.add_table(rows=1, cols=6, style="Table Grid")

    # Set table column widths
    set_col_widths(table)
    # create table rows
    write_header_row(table)
    write_data_row(table, test_data)


def write_data_row(table, test_data):
    """Write a test case result row in table

    Args:
        table (obj): Word doc table object
        test_data (list): List of interesting test data
    """

    # Iterate through test data and write table rows
    for count, test_case_entry in enumerate(test_data):
        count += 1

        # Identify test suite sub-header row
        if re.match(TEST_SUITE_HEADER, test_case_entry[0]):
            row_cells = table.add_row().cells
            row_cells[0].merge(row_cells[5])
            row_cells[0].text = ""
            run = row_cells[0].paragraphs[0].add_run(test_case_entry)
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.bold = True

            cell = table.cell(count, 0)
            shading_blue = parse_xml(
                # pylint: disable-next=consider-using-f-string
                r'<w:shd {} w:fill="CCFFFF"/>'.format(nsdecls("w"))
            )
            # pylint: disable-next=protected-access
            cell._tc.get_or_add_tcPr().append(shading_blue)

        # Identify test case result data row
        elif "TN" in test_case_entry[0]:
            row_cells = table.add_row().cells

            for counter, test_data_entry in enumerate(test_case_entry):
                row_cells[counter].text = ""
                run.font.name = "Arial"
                run.font.size = Pt(9)

                # Test Case Identifier cell
                if counter == 0:
                    test_data_entry = format_test_id(test_data_entry)
                    run = (
                        row_cells[counter]
                        .paragraphs[0]
                        .add_run(test_data_entry)
                    )
                # Test Case Pass/Fail cell
                elif counter == 4:
                    format_pass_fail(row_cells, counter, test_data_entry)
                # Cells not needing special formatting
                else:
                    run = (
                        row_cells[counter]
                        .paragraphs[0]
                        .add_run(test_data_entry)
                    )

                run.font.name = "Arial"
                run.font.size = Pt(9)


def format_test_id(test_data_entry):
    """Format the test case id

    Args:
        test_data_entry (str): Text for table cell

    Returns:
        str: Formatted text for table cell
    """
    if "TN" in test_data_entry:
        test_data_entry = test_data_entry.split("TN")[1]

    return test_data_entry


def format_pass_fail(row_cells, counter, test_data_entry):
    """Format pass fail cell

    Args:
        row_cells (obj): Table cell
        counter (int): Table cell number
        test_data_entry (str): Text for table cell
    """
    run = row_cells[counter].paragraphs[0].add_run(test_data_entry.upper())

    if test_data_entry.upper() == "PASS":
        # pylint: disable-next=no-member
        run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
        run.font.bold = True
    elif test_data_entry.upper() == "FAIL":
        # pylint: disable-next=no-member
        run.font.highlight_color = WD_COLOR_INDEX.RED
        run.font.bold = True
    else:
        # pylint: disable-next=no-member
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        run.font.bold = True


def set_col_widths(table):
    """Set width of Word table columns
        Note: Table column width is presently broken in docx module.
        Word defaults to autofit.

    Args:
        table (obj): Word doc table object
    """
    widths = (
        Inches(0.5),
        Inches(1.17),
        Inches(1.55),
        Inches(1.25),
        Inches(0.85),
        Inches(2.15),
    )
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width


def main():
    """Main Python function"""

    print("Starting...")
    test_data = parse_csv()
    write_report(test_data)
    print("Complete")


if __name__ == "__main__":
    main()
