"""Module to provide easy backwards compatibility with urllib."""


try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
try:
    import urllib
except ImportError:
    import urllib.request as urllib


urlopen = urllib2.urlopen
pathname2url = urllib.pathname2url
