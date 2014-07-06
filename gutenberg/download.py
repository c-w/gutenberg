"""Module to download raw etexts from Project Gutenberg."""


from __future__ import absolute_import
import bs4
import gutenberg.common.functutil as functutil
import gutenberg.common.osutil as osutil
import gutenberg.common.stringutil as stringutil
import logging
import os
import random
import requests
import time
import urllib


USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',  # noqa  # pylint: disable=C0301
    'Opera/9.25 (Windows NT 5.1; U; en)',  # noqa  # pylint: disable=C0301
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',  # noqa  # pylint: disable=C0301
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',  # noqa  # pylint: disable=C0301
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',  # noqa  # pylint: disable=C0301
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',  # noqa  # pylint: disable=C0301
]


def gutenberg_links(filetypes, langs, offset):
    """Crawls Project Gutenberg for etext download locations.

    Args:
        filetypes (str): generate links for files of these types (eg. "txt")
        langs (str): generate links for etexts in this language (eg. "en")
        offset (int): start downloading from this results page onwards

    Yields:
        str, int: the download location of the next etext and its offset

    """
    has_next = True
    while has_next:
        logging.info('downloading starting at offset %s', offset)
        response = requests.get(
            url='http://www.gutenberg.org/robot/harvest',
            params={
                'filetypes[]': filetypes,
                'langs[]': langs,
                'offset': offset,
            },
            headers={
                'user-agent': random.choice(USER_AGENTS),
            },
        )
        soup = bs4.BeautifulSoup(response.text)
        has_next = False
        for link in soup.find_all('a', href=True):
            if link.text.lower() == 'next page':
                offset = stringutil.request_param('offset', link['href'])
                has_next = True
            else:
                yield link['href'], int(offset)


def canonicalize(path):
    """Project Gutenberg paths consist of a resource identifier and an
    optinal suffix specifying an encoding. For example, ``14639.zip'' is an
    ascii-encoded file and ``14639-8.zip'' is a utf-8 encoded file. This
    function splits a path into uri and encoding.

    Args:
        path (str): the path to canonicalize

    Returns:
        str, str: the resource identifier associated with the path and its
                  encoding (or None if the file is ascii-encoded)

    Examples:
        >>> canonicalize('http://www.gutenberg.lib.md.us/14639.zip')
        ('14639', None)

        >>> canonicalize('http://www.gutenberg.lib.md.us/14641-8.zip')
        ('14641', '8')

        >>> canonicalize('http://www.gutenberg.lib.md.us/14674-0.zip')
        ('14674', '0')

    """
    uri, _ = os.path.splitext(os.path.basename(path))
    uri, encoding = uri.split('-') if '-' in uri else (uri, None)
    return uri, encoding


def download_link(link, todir, seen=None):
    """Download a single Project Gutenberg etext. Prefers URF-8 encoded files
    over ASCII encoded files.

    Args:
        link (str): the link to the etext to download
        todir (str): the directory to which to download the etext
        seen (dict, optional): a pointer to the already downloaded etexts

    Returns:
        bool: True if the file was downloaded and False if it was skipped

    """
    osutil.makedirs(todir)
    seen = seen if seen is not None else set()
    download = False
    uri, cur_encoding = canonicalize(link)

    if uri not in seen:
        # totally new ebook
        download = True
    else:
        # seen this ebook before - only download if it's a better version
        prev_location = seen[uri]
        prev_encoding = canonicalize(prev_location)[1]
        if cur_encoding > prev_encoding:
            download = True
            functutil.nointerrupt(os.remove)(prev_location)

    if download:
        logging.info('downloading file %s', link)
        downloadloc = os.path.join(todir, os.path.basename(link))
        functutil.nointerrupt(urllib.urlretrieve)(link, downloadloc)
        seen[uri] = downloadloc
    else:
        logging.debug('skipping file %s', link)

    return download


def download_corpus(todir, filetypes, langs, offset, delay=2):
    """Downloads the entire Project Gutenberg corpus to disk.

    Args:
        todir (str): directory to which to download the corpus files
        filetypes (str): only download extexts in these formats (eg. "txt")
        langs (str): only download etexts in these languages (eg. "en")
        offset (int): start downloading from this results page onwards
        delay (int): in-between request wait-time (in seconds)

    Returns:
        int: the last offset location from which etexts were downloaded

    """
    todir = osutil.canonical(todir)
    osutil.makedirs(todir)
    seen = dict((canonicalize(path)[0], path)
                for path in osutil.listfiles(todir))

    download = functutil.nointerrupt(download_link)
    for link, offset in gutenberg_links(filetypes, langs, offset):
        try:
            download_success = download(link, todir, seen=seen)
        except KeyboardInterrupt:
            pass
        except Exception as ex:  # pylint: disable=W0703
            logging.error('skipping %s, [%s] %s',
                          link, type(ex).__name__, ex.message)
        else:
            if download_success:
                time.sleep(delay)
    return offset


if __name__ == '__main__':
    import gutenberg.common.cliutil as cliutil

    doc = 'Downloads the Project Gutenberg corpus.'
    parser = cliutil.ArgumentParser(description=doc)
    parser.add_argument('todir', type=str,
                        help='directory to which to download the corpus')
    parser.add_argument('--filetypes', metavar='F', type=str, default='txt',
                        help='only download files in these formats')
    parser.add_argument('--langs', metavar='L', type=str, default='en',
                        help='only download files in these languages')
    parser.add_argument('--offset', metavar='O', type=int, default=0,
                        help='start download at this element')
    args = parser.parse_args()

    download_corpus(args.todir, args.filetypes, args.langs, args.offset)
