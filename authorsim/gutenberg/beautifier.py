# -*- coding: utf-8 -*-

from terminators import HEADERS, FOOTERS


def strip_headers(lines):
    """Remove lines that are part of the Project Gutenberg header or footer.

    This is a port of the C++ version by Johannes Krugel
    Link: http://www14.in.tum.de/spp1307/src/strip_headers.cpp

    Args:
        lines (list): the lines of text to filter

    Returns:
        list: the lines of text that don't belong to a header or footer

    """
    out = []
    i = 0
    reset = True
    footer_found = False

    for line in lines:
        if len(line) <= 12:
            continue  # just a shortcut for short lines

        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(header) for header in HEADERS):
                reset = True

            # If it's the end of the header, delete the output produced so far.
            # May be done several times, if multiple lines occur indicating the
            # end of the header
            if reset:
                out = []
                continue

        if i >= 100:
            # Check if the footer begins here
            if any(line.startswith(footer) for footer in FOOTERS):
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        out.append(line)
        i += 1

    return out


if __name__ == '__main__':
    import argparse
    import sys

    doc = 'Removes Project Gutenberg headers and footers.'
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help='gutenberg text to clean-up')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help='cleaned text goes here')
    args = parser.parse_args()

    for line in strip_headers(args.infile):
        args.outfile.write(line)
