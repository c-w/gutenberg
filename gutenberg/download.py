import bs4
import errno
import logging
import os
import random
import re
import requests
import time
import urllib
import urlparse


USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',  # pylint: disable=C0301
    'Opera/9.25 (Windows NT 5.1; U; en)',  # pylint: disable=C0301
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',  # pylint: disable=C0301
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',  # pylint: disable=C0301
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',  # pylint: disable=C0301
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',  # pylint: disable=C0301
]


def gutenberg_links(filetypes, langs, offset):
    """Crawls Project Gutenberg for etext download locations.

    Args:
        filetypes (str): generate links for files of these types (eg. "txt")
        langs (str): generate links for etexts in this language (eg. "en")
        offset (int): start downloading from this results page onwards

    Yields:
        str: the download location of the next etext

    """
    has_next = True
    while has_next:
        logging.info('Downloading from offset %s', offset)
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
                offset = request_param('offset', link['href'])
                has_next = True
            else:
                yield link['href']


def request_param(param, url):
    """Extracts the value of a single http request parameter.

    Args:
        param (str): the request parameter whose value to extract
        url (str): the request string from which to extract the paramter value

    Returns:
        str: the value of the parameter or None if the paramter is not
             in the url

    Examples:
        >>> request_param('baz', 'http://www.foo.com/bar?baz=1')
        '1'
        >>> request_param('grob', 'http://www.foo.com/bar?grob=2&baz=1')
        '2'
        >>> request_param('notfound', 'http://www.foo.com/bar?baz=1') is None
        True

    """
    query = urlparse.urlparse(url).query
    match = re.search('%s=([^&]*)&?' % param, query)
    return match.group(1) if match is not None else None


def makedirs(path):
    """Recrusively create all directories on a path.

    This is a wrapper around os.makedirs that doesn't fail if the directories
    already exist.

    Args:
        path (str): the path of directories to create

    Examples:
        >>> makedirs('/tmp/foo/bar')
        >>> os.path.isdir('/tmp/foo/bar')
        True
        >>> makedirs('/tmp/foo/bar')

    """
    try:
        os.makedirs(path)
    except (IOError, OSError) as ex:
        if ex.errno != errno.EEXIST:
            raise


def download_corpus(todir, filetypes, langs, offset, delay=2):
    """Downloads the entire Project Gutenberg corpus to disk. Prefers ISO
    encoded files over ASCII encoded files.

    Args:
        todir (str): directory to which to download the corpus files
        filetypes (str): only download extexts in these formats (eg. "txt")
        langs (str): only download etexts in these languages (eg. "en")
        offset (int): start downloading from this results page onwards
        delay (int): in-between request wait-time (in seconds)

    """
    makedirs(todir)
    seen = set()
    for link in gutenberg_links(filetypes, langs, offset):
        download = False
        filename, ext = os.path.splitext(os.path.basename(link))
        if '-' in filename:
            # prefer iso encoded files over ascii encoded versions
            asciiname, isoname = filename.split('-')[0], filename
            if asciiname in seen:
                download = True
                seen.add(isoname)
                seen.remove(asciiname)
                os.remove(os.path.join(todir, asciiname + ext))
        else:
            # fetch ascii encoded etext if iso encoded version not downloaded
            asciiname, isoname = filename, filename + '-'
            if isoname not in seen:
                download = True
                seen.add(asciiname)

        if download:
            try:
                logging.info('Downloading file %s', link)
                urllib.urlretrieve(link, os.path.join(todir, filename + ext))
                seen.add(filename)
            except KeyboardInterrupt:
                pass
            time.sleep(delay)


if __name__ == '__main__':
    import argparse

    doc = 'Downloads the Project Gutenberg corpus.'
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('todir', type=str,
                        help='directory to which to download the corpus')
    parser.add_argument('--filetypes', metavar='F', type=str, default='txt',
                        help='only download files in these formats')
    parser.add_argument('--langs', metavar='L', type=str, default='en',
                        help='only download files in these languages')
    parser.add_argument('--offset', metavar='O', type=int, default=0,
                        help='start download at this element')
    parser.add_argument('--verbose', dest='log', action='store_const',
                        const=logging.DEBUG, default=logging.WARNING,
                        help='log more detailed messages')
    args = parser.parse_args()

    logging.basicConfig(level=args.log)
    download_corpus(args.todir, args.filetypes, args.langs, args.offset)
