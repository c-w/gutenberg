"""Module to remove the noise from Project Gutenberg texts."""


from __future__ import absolute_import
import os

from gutenberg._domain_model.text import TEXT_END_MARKERS as _FOOTERS
from gutenberg._domain_model.text import TEXT_START_MARKERS as _HEADERS


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
    sep = unicode(os.linesep)

    out = []
    i = 0
    reset = True
    footer_found = False

    for line in lines:
        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(header) for header in _HEADERS):
                reset = True

            # If it's the end of the header, delete the output produced so far.
            # May be done several times, if multiple lines occur indicating the
            # end of the header
            if reset:
                out = []
                continue

        if i >= 100:
            # Check if the footer begins here
            if any(line.startswith(footer) for footer in _FOOTERS):
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        out.append(line.rstrip(sep))
        i += 1

    return sep.join(out)
