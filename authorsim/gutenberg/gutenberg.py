from beautify import strip_headers
import os
import urllib


def cleanup(inp):
    try:
        text = urllib.urlopen(inp).read()
    except IOError:
        text = inp
    lines = text.split(os.linesep)
    clean = strip_headers(lines)
    return os.linesep.join(clean)
