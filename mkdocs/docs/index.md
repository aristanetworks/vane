# VANE: Network Certification Tool



## Description


Vane ( **VA** lidation **NE** twork) <div style='text-align: justify;'> is an open source, network validation tool designed to conduct tests on Arista's networking devices. It operates by establishing connections with the devices on a specified network, executing commands, and conducting tests against the generated output. By automating these tasks, Vane significantly streamlines the network validation process, sparing users from the time-consuming burden of repetitive testing that could otherwise span months.

Vane prioritizes user-friendliness, aiming to reduce the necessity for system operators to manually edit source code. It achieves this goal by dynamically conveying information to its test cases through YAML files, which serve as containers for parameters passed to specific test cases.

A significant aspect of the tool is its versatility in reporting test case output across multiple formats such as JSON, HTML, Word documents, or Excel spreadsheets. This diverse range of output formats enhances the clarity of test case results and provides structured data, facilitating easier analysis of the test output.

</div>

## Technologies in Vane 
Vane,<div style='text-align: justify;'> is fundamentally a Python project, employing Python classes for tasks such as parsing command line arguments, configuring and executing tests, and reporting test output. Leveraging the versatility of Python, developers proficient in the language can effortlessly create or extend test cases within the Vane framework.

For reporting purposes, Vane integrates PyTest, capitalizing on its seamless execution of test cases and compatibility with existing functionality. All Vane test cases adhere to PyTest syntax. In essence, Vane serves as an enriched wrapper around PyTest, augmenting its capabilities. The ongoing focus of Arista's development efforts is geared towards enhancing user experience and simplifying the process of crafting test cases, and Vane aims to serve this.
</div>

## Contributing

<div style='text-align: justify;'>
Contributing pull requests are gladly welcomed for this repository.
Please note that all contributions that modify the library behavior
require corresponding test cases otherwise the pull request will be
rejected.
</div>
## License

<div style='text-align: justify;'>
Copyright (c) 2023, Arista Networks EOS+
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

</div>
* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the Arista nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.


!!! quote "Important"

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
