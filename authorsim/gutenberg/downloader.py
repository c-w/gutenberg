from user_agents import USER_AGENTS
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
        logging.info('Downloading from offset %s' % offset)
        request = {
            'url': 'http://www.gutenberg.org/robot/harvest',
            'params': {
                'filetypes[]': filetypes,
                'langs[]': langs,
                'offset': offset,
            },
            'headers': {
                'user-agent': random.choice(USER_AGENTS),
            },
        }

        response = requests.get(**request)
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
    makedirs(todir)
    for link in gutenberg_links(filetypes, langs, offset):
        try:
            logging.info('Downloading file %s' % link)
            topath = os.path.join(todir, os.path.basename(link))
            urllib.urlretrieve(link, filename=topath)
        except KeyboardInterrupt:
            pass
        time.sleep(delay)


if __name__ == '__main__':
    import argparse

    doc = 'Downloads the Project Gutenberg corpus.'
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('todir', type=str,
                        help='directory to which to download the corpus')
    parser.add_argument('--filetypes', metavar='F',  type=str, default='txt',
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
