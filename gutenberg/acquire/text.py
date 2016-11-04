"""Module to deal with text acquisition."""


from __future__ import absolute_import

import gzip
import os
from contextlib import closing

import requests

from gutenberg._domain_model.exceptions import UnknownDownloadUriException
from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.types import validate_etextno
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove


_TEXT_CACHE = local_path('text')


def _etextno_to_uri_subdirectory(etextno):
    """
    For example, ebook #1 is in subdirectory:
    0/1

    And ebook #19 is in subdirectory:
    1/19

    While ebook #15453 is in this subdirectory:
    1/5/4/5/15453
    """
    str_etextno = str(etextno).zfill(2)
    all_but_last_digit = list(str_etextno[:-1])
    subdir_part = "/".join(all_but_last_digit)
    subdir = "{0}/{1}".format(subdir_part, etextno)  # etextno not zfilled
    return subdir


def _format_download_uri(etextno):
    """Returns the download location on the Project Gutenberg servers for a
    given text.

    Raises:
        UnknownDownloadUri: If no download location can be found for the text.

    """
    uri_root = r'http://www.gutenberg.lib.md.us'
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
    raise UnknownDownloadUriException


def load_etext(etextno, refresh_cache=False):
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
        download_uri = _format_download_uri(etextno)
        response = requests.get(download_uri)
        response.encoding = 'utf-8'
        text = response.text
        with closing(gzip.open(cached, 'w')) as cache:
            cache.write(text.encode('utf-8'))
    else:
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
    args = parser.parse_args()

    try:
        text = load_etext(args.etextno)
        with reopen_encoded(args.outfile, 'w', 'utf8') as outfile:
            outfile.write(text)
    except Error as error:
        parser.error(str(error))


if __name__ == '__main__':
    _main()
