#!/usr/bin/env python2
"""Script to download texts of a certain author from Project Gutenberg."""


from __future__ import absolute_import
from __future__ import print_function
from gutenberg.textsource import GutenbergEbooks
from gutenberg.corpus import SqliteCorpus
import logging
import re
import shutil
import sys
import tempfile


def download_texts(author):
    """This function demonstrates how the gutenberg library can be used to
    download some texts to the current directory.

    """
    corpus = SqliteCorpus(GutenbergEbooks(), tempfile.mkdtemp())

    text_generator = corpus.texts_for_author(author)
    filename = lambda text_info: re.sub(r'\W', '-', text_info.title) + '.txt'

    for text_info, fulltext in text_generator:
        with open(filename(text_info), 'w') as outfile:
            outfile.write(fulltext)
            print('downloaded %s' % outfile.name, file=sys.stderr)

    shutil.rmtree(corpus.basedir)


def _main():
    """This function implements the main/script/command-line functionality of
    the module and will be called from the `if __name__ == '__main__':` block.

    """
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--author', help='download works by this author')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase logging verbosity')
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING - 10 * args.verbose)

    download_texts(author=args.author)


if __name__ == '__main__':
    _main()
