"""Module to deal with text acquisition."""


from __future__ import absolute_import, unicode_literals

import gzip
import os
from contextlib import closing

import requests

from gutenberg._domain_model.exceptions import UnknownDownloadUriException
from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.types import validate_etextno
from gutenberg._util.decorators import execute_only_once
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove

_TEXT_CACHE = local_path('text')
_GUTENBERG_MIRROR = 'http://aleph.gutenberg.org'


def _etextno_to_uri_subdirectory(etextno):
    """
    Returns the subdirectory that an etextno will be found in a gutenberg mirror. Generally, one
    finds the subdirectory by separating out each digit of the etext number, and uses it for
    a directory. The exception here is for etext numbers less than 10, which are prepended with a
    0 for the directory traversal.
    
    >>> _etextno_to_uri_subdirectory(1)
    '0/1'
    >>> _etextno_to_uri_subdirectory(19)
    '1/19'
    >>> _etextno_to_uri_subdirectory(15453)
    '1/5/4/5/15453'
    """
    str_etextno = str(etextno).zfill(2)
    all_but_last_digit = list(str_etextno[:-1])
    subdir_part = "/".join(all_but_last_digit)
    subdir = "{0}/{1}".format(subdir_part, etextno)  # etextno not zfilled
    return subdir


@execute_only_once
def _check_mirror_exists(mirror):
    response = requests.head(mirror)
    if not response.ok:
        error = "Could not reach Gutenberg mirror '{0:s}'. Try setting a different mirror " \
                "(https://www.gutenberg.org/MIRRORS.ALL) for --mirror flag or " \
                "GUTENBERG_MIRROR environment variable.".format(mirror)
        raise UnknownDownloadUriException(error)


def _format_download_uri(etextno, mirror=None):
    """Returns the download location on the Project Gutenberg servers for a
    given text.

    Raises:
        UnknownDownloadUri: If no download location can be found for the text.
    """
    uri_root = mirror or _GUTENBERG_MIRROR
    uri_root = uri_root.strip().rstrip('/')
    _check_mirror_exists(uri_root)

    extensions = ('.txt', '-8.txt', '-0.txt')
    for extension in extensions:
        path = _etextno_to_uri_subdirectory(etextno)
        uri = '{root}/{path}/{etextno}{extension}'.format(
            root=uri_root,
            path=path,
            etextno=etextno,
            extension=extension)
        response = requests.head(uri)
        if response.ok:
            return uri
    raise UnknownDownloadUriException('Failed to find {0} on {1}.'.format(etextno, uri_root))


def load_etext(etextno, refresh_cache=False, mirror=None):
    """Returns a unicode representation of the full body of a Project Gutenberg
    text. After making an initial remote call to Project Gutenberg's servers,
    the text is persisted locally.

    """
    etextno = validate_etextno(etextno)
    cached = os.path.join(_TEXT_CACHE, '{0}.txt.gz'.format(etextno))

    if refresh_cache:
        remove(cached)
    if not os.path.exists(cached):
        makedirs(os.path.dirname(cached))
        download_uri = _format_download_uri(etextno, mirror)
        response = requests.get(download_uri)
        text = response.text
        with closing(gzip.open(cached, 'w')) as cache:
            cache.write(text.encode('utf-8'))

    with closing(gzip.open(cached, 'r')) as cache:
        text = cache.read().decode('utf-8')
    return text


def _main():
    """Command line interface to the module.

    """
    from argparse import ArgumentParser, FileType
    from gutenberg import Error
    from gutenberg._util.os import reopen_encoded

    parser = ArgumentParser(description='Download a Project Gutenberg text')
    parser.add_argument('etextno', type=int)
    parser.add_argument('outfile', type=FileType('w'))
    parser.add_argument('--mirror', '-m', type=str)
    args = parser.parse_args()

    mirror = args.mirror or os.environ.get('GUTENBERG_MIRROR')

    try:
        text = load_etext(args.etextno, mirror=mirror)
        with reopen_encoded(args.outfile, 'w', 'utf8') as outfile:
            outfile.write(text)
    except Error as error:
        parser.error(str(error))


if __name__ == '__main__':
    _main()
