from . import api
import collections
import contextlib
import gzip
import logging
import os
import sqlite3


class SqliteCorpus(api.Corpus):
    def __init__(self, *args, **kwargs):
        api.Corpus.__init__(self, *args, **kwargs)
        self._index = os.path.join(self.basedir, 'index.sqlite3')

    @contextlib.contextmanager
    def _dbcon(self):
        dbcon = sqlite3.connect(self._index)
        try:
            dbcon.row_factory = sqlite3.Row
            yield dbcon
        finally:
            dbcon.close()

    def _build_index(self):
        with self._dbcon() as dbcon:
            dbcon.execute('''
                CREATE TABLE IF NOT EXISTS TextInfo(
                    uid INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    location TEXT
                )''')
            dbcon.executemany('''
                INSERT INTO TextInfo(uid, title, author, location)
                VALUES(?, ?, ?, ?)
            ''', ((text_info.uid, text_info.title, text_info.author,
                   os.path.join(self.basedir, '%s.gz' % text_info.uid))
                  for text_info in iter(self.text_source)))

    def _fulltext(self, text_info, location=None):
        if location is None:
            with self._dbcon() as dbcon:
                result = dbcon.execute('''
                    SELECT location
                    FROM TextInfo
                    WHERE uid = ?
                    LIMIT 1
                ''', (text_info.uid, )).fetchone()
            location = result['location']

        try:
            with gzip.open(location, 'rb') as gzipped:
                fulltext = gzipped.read()
        except IOError:
            fulltext = self.text_source.fulltext(text_info)
            if fulltext:
                with gzip.open(location, 'wb') as gzipped:
                    gzipped.write(fulltext)
        return fulltext

    def texts_for_author(self, author):
        matches = collections.defaultdict(list)
        with self._dbcon() as dbcon:
            for row in dbcon.execute('''
                SELECT uid, author, title, location
                FROM TextInfo
                WHERE author LIKE ?
                ORDER BY author
            ''', ('%' + author + '%', )):
                matches[row['author']].append(row)
        if len(matches) > 1:
            logging.warning(
                '%d authors match the query "%s": %s',
                len(matches), author,
                ', '.join('"%s"' % author for author in matches))

        for matched_author, texts in matches.iteritems():
            for text in texts:
                text_info = api.TextInfo(
                    uid=text['uid'],
                    author=matched_author,
                    title=text['title'])
                yield text_info, self._fulltext(text_info, text['location'])
