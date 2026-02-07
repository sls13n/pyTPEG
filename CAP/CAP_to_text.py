#!/usr/bin/env python3
#
# Copyright 2022 TISA ASBL
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#   Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   Neither the name of the copyright holder nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; # OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Read in CAP message and create textual output

import xml, optparse
from xml.etree.ElementTree import ElementTree, Element, ParseError
from CAP.CAP_alert_component import CAP_alert_component


def read_and_parse_file(fname: str) -> Element:
    """
    Reads a CAP message file and parses it as XML.

    Args:
        fname (str): The name of the file to read.

    Returns:
        Element: The root element of the parsed XML tree, or None if an error occurs.

    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If an I/O error occurs while reading the file.
        ParseError: If there is an error parsing the XML.
    """
    try:
        with open(fname, 'r') as f:
            file_string: str = f.read()

        print(f"\n\n\nLength of file {fname} = {len(file_string)}")

        if len(file_string) == 0:
            print(f'File {fname} is empty! Skipping.')
            return None

        # Parse the XML content
        root: Element = xml.etree.ElementTree.fromstring(file_string)
        return root

    except FileNotFoundError:
        print(f"Error: File {fname} not found.")
    except IOError as e:
        print(f"Error reading file {fname}: {e}")
    except ParseError as e:
        print(f"Error parsing XML in file {fname}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred while processing file {fname}: {e}")

    return None


def process_file(fname: str) -> None:
    """
    Processes a single CAP message file: reads, parses, and generates output.

    Args:
        fname (str): The name of the file to process.
    """
    root: Element = read_and_parse_file(fname)

    if root is None:
        # Skip further processing if there was an error or the file is empty
        return

    try:
        # Determine the CAP version in use, defaulting to version 1.2
        CAPversion: str = "1.2"
        backup_capns: str = "{urn:oasis:names:tc:emergency:cap:1.1}"

        # Check if the file is using CAP version 1.1
        if root.tag == backup_capns + "alert":
            CAPversion = "1.1"

        # Parse the CAP message root element
        CAPalert: CAP_alert_component = CAP_alert_component(1, CAPversion=CAPversion)
        CAPalert.parse(root)

        # Generate and print textual output for the CAP alert
        txt: str = CAPalert.out(num_only=["WKT", "SHN", "warnVerwaltungsbereiche"])
        print(txt)

    except AttributeError as e:
        print(f"Error processing CAP alert component in file {fname}: {e}")
    except Exception as e:
        print(f"Unexpected error during CAP alert processing in file {fname}: {e}")


def main() -> None:
    """
    Main function to read CAP (Common Alerting Protocol) message files,
    parse them using the CAP_alert_component class, and output a textual
    representation of the CAP message.
    """

    # Set up command-line argument parsing
    usage: str = "usage: %prog [options]"
    parser: optparse.OptionParser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()

    # Check if any files are provided
    if not args:
        print("No CAP message files provided. Exiting.")
        exit(1)

    # Iterate over each file provided in the arguments
    for fname in args:
        process_file(fname)


if __name__ == '__main__':
    main()
