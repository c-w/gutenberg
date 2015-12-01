"""Module to remove the noise from Project Gutenberg texts."""


from __future__ import absolute_import
from builtins import str
import os

from gutenberg._domain_model.text import TEXT_END_MARKERS
from gutenberg._domain_model.text import TEXT_START_MARKERS
from gutenberg._domain_model.text import LEGALESE_END_MARKERS
from gutenberg._domain_model.text import LEGALESE_START_MARKERS


def strip_headers(text):
    """Remove lines that are part of the Project Gutenberg header or footer.
    Note: this function is a port of the C++ utility by Johannes Krugel. The
    original version of the code can be found at:
    http://www14.in.tum.de/spp1307/src/strip_headers.cpp

    Args:
        text (unicode): The body of the text to clean up.

    Returns:
        unicode: The text with any non-text content removed.

    """
    lines = text.splitlines()
    sep = str(os.linesep)

    out = []
    i = 0
    reset = True
    footer_found = False
    ignore_section = False

    for line in lines:
        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(token) for token in TEXT_START_MARKERS):
                reset = True

            # If it's the end of the header, delete the output produced so far.
            # May be done several times, if multiple lines occur indicating the
            # end of the header
            if reset:
                out = []
                continue

        if i >= 100:
            # Check if the footer begins here
            if any(line.startswith(token) for token in TEXT_END_MARKERS):
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        if any(line.startswith(token) for token in LEGALESE_START_MARKERS):
            ignore_section = True
            continue
        elif any(line.startswith(token) for token in LEGALESE_END_MARKERS):
            ignore_section = False
            continue

        if not ignore_section:
            out.append(line.rstrip(sep))
            i += 1

    return sep.join(out)


def _main():
    """Command line interface to the module.

    """
    from argparse import ArgumentParser, FileType
    from gutenberg._util.os import reopen_encoded

    parser = ArgumentParser(description='Remove headers and footers from a '
                                        'Project Gutenberg text')
    parser.add_argument('infile', type=FileType('r'))
    parser.add_argument('outfile', type=FileType('w'))
    args = parser.parse_args()

    with reopen_encoded(args.infile, 'r', 'utf8') as infile:
        text = infile.read()
        clean_text = strip_headers(text)

    with reopen_encoded(args.outfile, 'w', 'utf8') as outfile:
        outfile.write(clean_text)


if __name__ == '__main__':
    _main()
