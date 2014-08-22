# -*- coding: utf-8 -*-
"""Module to process raw Project Gutenberg ETexts into a more usable format."""


import logging


# Markers that indicate the Project Gutenberg headers
HEADERS = [
    ur"*END*THE SMALL PRINT",
    ur"*** START OF THE PROJECT GUTENBERG",
    ur"*** START OF THIS PROJECT GUTENBERG",
    ur"This etext was prepared by",
    ur"E-text prepared by",
    ur"Produced by",
    ur"Distributed Proofreading Team",
    ur"*END THE SMALL PRINT",
    ur"***START OF THE PROJECT GUTENBERG",
    ur"This etext was produced by",
    ur"*** START OF THE COPYRIGHTED",
    ur"The Project Gutenberg",
    ur"http://gutenberg.spiegel.de/ erreichbar.",
    ur"Project Runeberg publishes",
    ur"Beginning of this Project Gutenberg",
    ur"Project Gutenberg Online Distributed",
    ur"Gutenberg Online Distributed",
    ur"the Project Gutenberg Online Distributed",
    ur"Project Gutenberg TEI",
    ur"This eBook was prepared by",
    ur"http://gutenberg2000.de erreichbar.",
    ur"This Etext was prepared by",
    ur"Gutenberg Distributed Proofreaders",
    ur"the Project Gutenberg Online Distributed Proofreading Team",
    ur"**The Project Gutenberg",
    ur"*SMALL PRINT!",
    ur"More information about this book is at the top of this file.",
    ur"tells you about restrictions in how the file may be used.",
    ur"l'authorization à les utilizer pour preparer ce texte.",
    ur"of the etext through OCR.",
    ur"*****These eBooks Were Prepared By Thousands of Volunteers!*****",
    ur"SERVICE THAT CHARGES FOR DOWNLOAD",
    ur"We need your donations more than ever!",
    ur" *** START OF THIS PROJECT GUTENBERG",
    ur"****     SMALL PRINT!",
]

# Markers that indicate the Project Gutenberg footers
FOOTERS = [
    ur"*** END OF THE PROJECT GUTENBERG",
    ur"*** END OF THIS PROJECT GUTENBERG",
    ur"***END OF THE PROJECT GUTENBERG",
    ur"End of the Project Gutenberg",
    ur"End of The Project Gutenberg",
    ur"Ende dieses Project Gutenberg",
    ur"by Project Gutenberg",
    ur"End of Project Gutenberg",
    ur"End of this Project Gutenberg",
    ur"Ende dieses Projekt Gutenberg",
    ur"        ***END OF THE PROJECT GUTENBERG",
    ur"*** END OF THE COPYRIGHTED",
    ur"End of this is COPYRIGHTED",
    ur"Ende dieses Etextes ",
    ur"Ende dieses Project Gutenber",
    ur"Ende diese Project Gutenberg",
    ur"**This is a COPYRIGHTED Project Gutenberg Etext, Details Above**",
    ur"Fin de Project Gutenberg",
    ur"The Project Gutenberg Etext of ",
    ur"Ce document fut presente en lecture",
    ur"Ce document fut présenté en lecture",
    ur"More information about this book is at the top of this file.",
    ur"We need your donations more than ever!",
    ur"<<THIS ELECTRONIC VERSION OF",
    ur"END OF PROJECT GUTENBERG",
    ur" End of the Project Gutenberg",
    ur" *** END OF THIS PROJECT GUTENBERG",
]


def strip_headers(lines):
    """Remove lines that are part of the Project Gutenberg header or footer.

    This is a port of the C++ version by Johannes Krugel (link:
    http://www14.in.tum.de/spp1307/src/strip_headers.cpp)

    Args:
        lines (list): The lines of text to filter.

    Returns:
        list: The lines of text that don't belong to a header or footer.

    """
    out = []
    i = 0
    reset = True
    footer_found = False

    for lineno, line in enumerate(lines, start=1):
        if len(line) <= 12:
            continue  # just a shortcut for short lines

        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(header) for header in HEADERS):
                logging.debug('found end of header on line %s', lineno)
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
                logging.debug('found start of footer on line %s', lineno)
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        out.append(line.strip())
        i += 1

    return out
