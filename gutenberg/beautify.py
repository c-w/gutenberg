# -*- coding: utf-8 -*-


# Markers that indicate the Project Gutenberg headers
HEADERS = [
    "*END*THE SMALL PRINT",
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
    "This etext was prepared by",
    "E-text prepared by",
    "Produced by",
    "Distributed Proofreading Team",
    "*END THE SMALL PRINT",
    "***START OF THE PROJECT GUTENBERG",
    "This etext was produced by",
    "*** START OF THE COPYRIGHTED",
    "The Project Gutenberg",
    "http://gutenberg.spiegel.de/ erreichbar.",
    "Project Runeberg publishes",
    "Beginning of this Project Gutenberg",
    "Project Gutenberg Online Distributed",
    "Gutenberg Online Distributed",
    "the Project Gutenberg Online Distributed",
    "Project Gutenberg TEI",
    "This eBook was prepared by",
    "http://gutenberg2000.de erreichbar.",
    "This Etext was prepared by",
    "Gutenberg Distributed Proofreaders",
    "the Project Gutenberg Online Distributed Proofreading Team",
    "**The Project Gutenberg",
    "*SMALL PRINT!",
    "More information about this book is at the top of this file.",
    "tells you about restrictions in how the file may be used.",
    "l'authorization à les utilizer pour preparer ce texte.",
    "of the etext through OCR.",
    "*****These eBooks Were Prepared By Thousands of Volunteers!*****",
    "SERVICE THAT CHARGES FOR DOWNLOAD",
    "We need your donations more than ever!",
    " *** START OF THIS PROJECT GUTENBERG",
    "****     SMALL PRINT!",
]

# Markers that indicate the Project Gutenberg footers
FOOTERS = [
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
    "***END OF THE PROJECT GUTENBERG",
    "End of the Project Gutenberg",
    "End of The Project Gutenberg",
    "Ende dieses Project Gutenberg",
    "by Project Gutenberg",
    "End of Project Gutenberg",
    "End of this Project Gutenberg",
    "Ende dieses Projekt Gutenberg",
    "        ***END OF THE PROJECT GUTENBERG",
    "*** END OF THE COPYRIGHTED",
    "End of this is COPYRIGHTED",
    "Ende dieses Etextes ",
    "Ende dieses Project Gutenber",
    "Ende diese Project Gutenberg",
    "**This is a COPYRIGHTED Project Gutenberg Etext, Details Above**",
    "Fin de Project Gutenberg",
    "The Project Gutenberg Etext of ",
    "Ce document fut presente en lecture",
    "Ce document fut présenté en lecture",
    "More information about this book is at the top of this file.",
    "We need your donations more than ever!",
    "<<THIS ELECTRONIC VERSION OF",
    "END OF PROJECT GUTENBERG",
    " End of the Project Gutenberg",
    " *** END OF THIS PROJECT GUTENBERG",
]


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

        out.append(line.strip())
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
