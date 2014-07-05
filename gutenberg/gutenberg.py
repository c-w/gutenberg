from __future__ import absolute_import
import gutenberg.beautify as beautify
import gutenberg.common.configutil as configutil
import gutenberg.common.osutil as osutil
import gutenberg.download as download
import gutenberg.metainfo as metainfo
import itertools
import logging
import os
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()


class Gutenberg(configutil.ConfigMapping):
    def __init__(self):
        self.download = configutil.ConfigMapping.Section()
        self.download.data_path = 'ProjectGutenberg/rawdata'
        self.download.offset = 0
        self.database = configutil.ConfigMapping.Section()
        self.database.drivername = 'sqlite'
        self.database.username = None
        self.database.password = None
        self.database.host = None
        self.database.port = None
        self.database.database = 'ProjectGutenberg/gutenberg.db3'

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
        for path in osutil.listfiles(self.download.data_path):
            print path
            session.add(EText.from_file(path))


class EText(Base):
    __tablename__ = 'etexts'

    etextno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    fulltext = sqlalchemy.Column(sqlalchemy.Text)

    @classmethod
    def from_file(cls, fobj):
        lines = fobj if isinstance(fobj, file) else osutil.readfile(fobj)
        metaiter, fulltextiter = itertools.tee(lines, 2)
        ident = metainfo.etextno(metaiter)
        text = '\n'.join(beautify.strip_headers(fulltextiter))
        metadata = metainfo.metainfo()[ident]
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
