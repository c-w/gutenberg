from . import api
import gzip
import sqlite3
import os


class SqliteCorpus(api.Corpus):
    def __init__(self, *args, **kwargs):
        api.Corpus.__init__(self, *args, **kwargs)
        self._index = os.path.join(self.basedir, 'index.sqlite3')

    def _build_index(self):
        with sqlite3.connect(self._index) as dbcon:
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
            with sqlite3.connect(self._index) as dbcon:
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
        with sqlite3.connect(self._index) as dbcon:
            results = dbcon.execute('''
                SELECT uid, author, title, location
                FROM TextInfo
                WHERE author LIKE ?
                ORDER BY author
            ''', ('%' + author + '%', ))

        for result in results:
            text_info = api.TextInfo(
                uid=result['uid'],
                author=result['author'],
                title=result['title'])
            yield text_info, self._fulltext(text_info, result['location'])
