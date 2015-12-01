"""Module to handle os-level interactions."""


from __future__ import absolute_import
from io import open
import codecs
import errno
import os
import shutil


def makedirs(*args, **kwargs):
    """Wrapper around os.makedirs that doesn't raise an exception if the
    directory already exists.

    """
    try:
        os.makedirs(*args, **kwargs)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def remove(path):
    """Wrapper that switches between os.remove and shutil.rmtree depending on
    whether the provided path is a file or directory.

    """
    if not os.path.exists(path):
        return

    if os.path.isdir(path):
        return shutil.rmtree(path)

    if os.path.isfile(path):
        return os.remove(path)


def determine_encoding(path, default=None):
    """Determines the encoding of a file based on byte order marks.

    Arguments:
        path (str): The path to the file.
        default (str, optional): The encoding to return if the byte-order-mark
            lookup does not return an answer.

    Returns:
        str: The encoding of the file.

    """
    byte_order_marks = (
        ('utf-8-sig', (codecs.BOM_UTF8, )),
        ('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
        ('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)),
    )

    try:
        with open(path, 'rb') as infile:
            raw = infile.read(4)
    except IOError:
        return default

    for encoding, boms in byte_order_marks:
        if any(raw.startswith(bom) for bom in boms):
            return encoding

    return default


def reopen_encoded(fileobj, mode='r', fallback_encoding=None):
    """Makes sure that a file was opened with some valid encoding.

    Arguments:
        fileobj (file): The file-object.
        mode (str, optional): The mode in which to re-open the file.
        fallback_encoding (str, optional): The encoding in which to re-open
            the file if it does not specify an encoding itself.

    Returns:
        file: The re-opened file.

    """
    encoding = determine_encoding(fileobj.name, fallback_encoding)
    fileobj.close()
    return open(fileobj.name, mode, encoding=encoding)
