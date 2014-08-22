"""Utility methods to deal with downloads and urls ."""


import hashlib
import os
import requests
import tempfile


def iter_lines(url, decode_unicode=True):
    response = requests.get(url, stream=True)
    if not response.ok:
        return iter([]), False
    return response.iter_lines(decode_unicode=decode_unicode), True


def grab(url, filename=None, cached=True):
    if not filename:
        cachedir = tempfile.gettempdir()
        filename = os.path.join(cachedir, hashlib.sha256(url).hexdigest())

    if cached and os.path.isfile(filename):
        return filename, True

    response = requests.get(url, stream=True)
    if not response.ok:
        return None, False

    with open(filename, 'wb') as downloaded:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                downloaded.write(chunk)
                downloaded.flush()
    return filename, True
