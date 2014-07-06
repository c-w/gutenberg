from __future__ import absolute_import
import gutenberg.beautify as beautify
import gutenberg.common.configutil as configutil
import gutenberg.common.functutil as functutil
import gutenberg.common.osutil as osutil
import gutenberg.download as download
import gutenberg.metainfo as metainfo
import itertools
import json
import logging
import os
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()


class Gutenberg(configutil.ConfigMapping):
    def __init__(self):
        BASEDIR = 'ProjectGutenbergCorpus'
        self.download = configutil.ConfigMapping.Section()
        self.download.data_path = os.path.join(BASEDIR, 'rawdata')
        self.download.offset = 0
        self.metadata = configutil.ConfigMapping.Section()
        self.metadata.metadata = os.path.join(BASEDIR, 'metadata.json.gz')
        self.database = configutil.ConfigMapping.Section()
        self.database.drivername = 'sqlite'
        self.database.username = None
        self.database.password = None
        self.database.host = None
        self.database.port = None
        self.database.database = os.path.join(BASEDIR, 'gutenberg.db3')

    @functutil.memoize
    def etext_metadata(self):
        opener = osutil.opener(self.metadata.metadata)
        try:
            with opener(self.metadata.metadata, 'rb') as metadata_file:
                json_items = json.load(metadata_file).iteritems()
                metadata = dict((int(key), val) for (key, val) in json_items)
        except IOError:
            metadata = metainfo.metainfo()
            osutil.makedirs(os.path.dirname(self.metadata.metadata))
            with opener(self.metadata.metadata, 'wb') as metadata_file:
                json.dump(metadata, metadata_file, sort_keys=True, indent=2)
        return metadata

    def download_corpus(self, filetypes='txt', langs='en'):
        osutil.makedirs(self.download.data_path)
        self.download.offset = download.download_corpus(
            self.download.data_path, filetypes=filetypes, langs=langs,
            offset=int(self.download.offset))

    def _dbsession(self):
        osutil.makedirs(os.path.dirname(self.database.database))
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
            drivername=self.database.drivername,
            username=self.database.username,
            password=self.database.password,
            host=self.database.host,
            port=self.database.port,
            database=osutil.canonical(self.database.database),
        ))
        Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        return Session()

    def update_database(self):
        session = self._dbsession()
        existing = set(etext.etextno for etext in session.query(EText).all())
        for path in osutil.listfiles(self.download.data_path):
            try:
                etext = EText.from_file(path, self.etext_metadata())
            except NotImplementedError as ex:
                logging.error('%s while processing etext at %s: %s',
                              type(ex).__name__, path, ex.message)
            else:
                if etext.etextno not in existing:
                    session.add(etext)
                    existing.add(etext.etextno)
        session.commit()


class EText(Base):
    __tablename__ = 'etexts'

    etextno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.Unicode)
    title = sqlalchemy.Column(sqlalchemy.Unicode)
    fulltext = sqlalchemy.Column(sqlalchemy.UnicodeText)

    @classmethod
    def from_file(cls, fobj, etext_metadata):
        lines = fobj if isinstance(fobj, file) else osutil.readfile(fobj)
        lines = (unicode(line, 'latin1') for line in lines)
        metaiter, fulltextiter = itertools.tee(lines, 2)
        ident = metainfo.etextno(metaiter)
        text = u'\n'.join(beautify.strip_headers(fulltextiter))
        metadata = etext_metadata[ident]
        author = metadata.get('author')
        title = metadata.get('title')
        if author is None:
            logging.warning('No author for etextno %s', ident)
        if title is None:
            logging.warning('No title for etextno %s', ident)
        return EText(etextno=ident, author=author, title=title, fulltext=text)

    def __repr__(self):
        return ('{clsname}(author="{author}", title="{title}", text="{text}")'
                .format(
                    clsname=self.__class__.__name__,
                    author=self.author,
                    title=self.title,
                    text=self.fulltext[:15] + '...'))
