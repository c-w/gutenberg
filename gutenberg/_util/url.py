"""Module to provide easy backwards compatibility with urllib."""


try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
try:
    from urllib import pathname2url
except ImportError:
    from urllib.request import pathname2url
