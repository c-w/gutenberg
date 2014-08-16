"""Module to tag Project Gutenberg etexts with meta-data."""


from __future__ import absolute_import
import gutenberg.common.urlutil as urlutil
import collections
import json
import os
import rdflib
import re
import tarfile


def etextno(lines):
    """Retrieves the id for an etext.

    Args:
        lines (iter): The lines of the etext to search.

    Returns:
        int: The id of the etext.

    Raises:
        ValueError: If no etext id was found.

    Examples:
        >>> etextno(['Release Date: March 17, 2004 [EBook #11609]'])
        11609

        >>> etextno(['Release Date: July, 2003 [Etext# 4263]'])
        4263

        >>> etextno(['Release Date: November 29, 2003 [Eook #10335]'])
        10335

        >>> etextno(['December, 1998  [Etext 1576#]'])
        1576

        >>> etextno(['Some lines', 'without', 'Any [Etext] Number'])
        Traceback (most recent call last):
            ...
        ValueError: no etext-id found

    """

    etext_re = re.compile(r'''
        e(text|b?ook)
        \s*
        (\#\s*(?P<etextid_front>\d+)
         |
        (?P<etextid_back>\d+)\s*\#)
        ''', re.IGNORECASE | re.VERBOSE)
    for line in lines:
        match = etext_re.search(line)
        if match is not None:
            front_match = match.group('etextid_front')
            back_match = match.group('etextid_back')
            if front_match is not None:
                return int(front_match)
            elif back_match is not None:
                return int(back_match)
            else:
                raise ValueError('no regex match (this should never happen')
    raise ValueError('no etext-id found')


def parse_rdf(graph):
    """Extracts etext meta-data from an RDF graph.

    Arguments:
        graph (rdflib.Graph): The RDF graph to parse.

    Returns:
        iter: An iterator over the etext-ids, authors and titles in the graph.

    """

    return ((
        int(os.path.basename(ebook_node.toPython())),
        author_node.toPython(),
        title_node.toPython(),
    ) for (
        ebook_node,
        author_node,
        title_node,
    ) in graph.query("""
        SELECT DISTINCT
            ?ebook
            ?author
            ?title
        WHERE {
            ?ebook a pgterms:ebook.
            ?ebook dcterms:creator [ pgterms:name ?author ].
            ?ebook dcterms:title ?title.
        }
    """))


def metainfo():
    """Retrieves a database of meta-data about Project Gutenberg etexts.  The
    meta-data always contains at least information about the title and author
    of a work. Optional information includes translator, editor, language, etc.

    Returns:
        dict: A mapping from etext-identifier to etext meta-data.

    """
    metadata = collections.defaultdict(dict)
    for graph in raw_metainfo():
        for etext, author, title in parse_rdf(graph):
            metadata[etext]['author'] = author
            metadata[etext]['title'] = title
    return dict(metadata)


def raw_metainfo():
    """Retrieves an RDF version of the Project Gutenberg meta-data catalog.

    Yields:
        rdflib.Graph: An etext meta-data definition.

    """
    index_url = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
    filename, _ = urlutil.urlretrieve(index_url)
    with tarfile.open(filename) as archive:
        for tarinfo in archive:
            graph = rdflib.Graph()
            graph.parse(archive.extractfile(tarinfo))
            yield graph


def _main():
    """This function implements the main/script/command-line functionality of
    the module and will be called from the `if __name__ == '__main__':` block.

    """
    import gutenberg.common.cliutil as cliutil
    import argparse
    import sys

    doc = 'Downloads Project Gutenberg meta-data for all etexts as JSON'
    parser = cliutil.ArgumentParser(description=doc)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help=('the file to which to write the etext meta-data '
                              '(default: stdout)'))

    with parser.parse_args() as args:
        json.dump(metainfo(), args.outfile, sort_keys=True, indent=2)


if __name__ == '__main__':
    _main()
