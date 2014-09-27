"""Utility methods to deal with downloads and urls ."""


import hashlib
import os
import requests
import tempfile


def iter_lines(url, decode_unicode=True):
    """Downloads a resource, one line at a time.

    Arguments:
        url (str): The URL of the resource to download
        decode_unicode (bool, optional): Set to False to prevent fetched lines
            to be converted to unicode

    Returns:
        iter, bool: An iterator over the lines in the resource and True/False
            depending on whether the resource could be fetched successfully


    """
    response = requests.get(url, stream=True)
    if not response.ok:
        return iter([]), False
    return response.iter_lines(decode_unicode=decode_unicode), True


def grab(url, filename=None, cached=True):
    """Downloads a resource.

    Arguments:
        url (str): The URL of the resource to download
        filename (str, optional): The path to which to download the resource
        cached (bool, optional): Set to False to disable local caching of files

    Returns:
        str, bool: The path to the downloaded resource and True/False depending
            on whether the resource could be fetched successfully
    """
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
