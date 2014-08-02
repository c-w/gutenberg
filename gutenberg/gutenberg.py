"""Module to interface with the Project Gutenberg corpus."""


from __future__ import absolute_import
import gutenberg.beautify as beautify
import gutenberg.common.configutil as configutil
import gutenberg.common.functutil as functutil
import gutenberg.common.osutil as osutil
import gutenberg.download as download
import gutenberg.metainfo as metainfo
import json
import logging
import os
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


ORM_BASE = sqlalchemy.ext.declarative.declarative_base()


class GutenbergCorpus(object):
    """Object representing the Project Gutenberg corpus. The object offers a
    simple interface to functionality such as downloading the corpus, removing
    headers, persisting meta-data to a database, etc.

    """
    def __init__(self):
        basedir = 'ProjectGutenbergCorpus'
        self.cfg = configutil.ConfigMapping()
        self.cfg.download = configutil.ConfigMapping.Section()
        self.cfg.download.data_path = os.path.join(basedir, 'rawdata')
        self.cfg.download.offset = 0
        self.cfg.metadata = configutil.ConfigMapping.Section()
        self.cfg.metadata.metadata = os.path.join(basedir, 'metadata.json.gz')
        self.cfg.database = configutil.ConfigMapping.Section()
        self.cfg.database.drivername = 'sqlite'
        self.cfg.database.username = None
        self.cfg.database.password = None
        self.cfg.database.host = None
        self.cfg.database.port = None
        self.cfg.database.database = os.path.join(basedir, 'gutenberg.db3')

    @classmethod
    def using_config(cls, config_path):
        """Initialize a corpus using the settings specified in a configuration
        file. Any non-specified settings are set to the default values.

        Args:
            config_path (str): the path to the .cfg file

        Returns:
            GutenbergCorpus: a corpus respecting the settings in the
                             configuration file

        """
        corpus = cls()
        corpus.cfg.merge(configutil.ConfigMapping.from_config(config_path))
        return corpus

    def write_config(self, path):
        """Dump the configuration options of the corpus to a file for later
        restoring.

        Args:
            path (str): the path to which to write the configuration file

        """
        self.cfg.write_config(path)

    def _dbsession(self):
        """Creates a database session respecting the configuration settings of
        the corpus.

        Returns:
            sqlalchemy.orm.Session: a database session

        """
        osutil.makedirs(os.path.dirname(self.cfg.database.database))
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
            drivername=self.cfg.database.drivername,
            username=self.cfg.database.username,
            password=self.cfg.database.password,
            host=self.cfg.database.host,
            port=self.cfg.database.port,
            database=osutil.canonical(self.cfg.database.database),
        ))
        ORM_BASE.metadata.create_all(engine)
        new_session = sqlalchemy.orm.sessionmaker(bind=engine)
        return new_session()

    @functutil.memoize
    def etext_metadata(self):
        """Reads a database of etext metadata from disk (or creates the
        database if it does not exist). The metadata contains information such
        as title, author, etc.

        Returns:
            dict: a mapping from etext-identifier to etext-metadata

        """
        opener = lambda path, mode: osutil.opener(path, mode, encoding='utf-8')
        try:
            with opener(self.cfg.metadata.metadata, 'rb') as metadata_file:
                json_items = json.load(metadata_file).iteritems()
                metadata = dict((int(key), val) for (key, val) in json_items)
        except IOError:
            metadata = metainfo.metainfo()
            osutil.makedirs(os.path.dirname(self.cfg.metadata.metadata))
            with opener(self.cfg.metadata.metadata, 'wb') as metadata_file:
                json.dump(metadata, metadata_file, sort_keys=True, indent=2)
        return metadata

    def download(self, filetypes='txt', langs='en', limit=None):
        """Downloads the Gutenberg corpus to disk.

        Args:
            filetypes (str, optional): the etext formats to download
            langs (str, optional): the etext languages to download
            limit (int, optional): number of bytes of etexts to download

        """
        osutil.makedirs(self.cfg.download.data_path)
        self.cfg.download.offset = download.download_corpus(
            self.cfg.download.data_path,
            download.CorpusDownloadContext(
                filetypes=filetypes,
                langs=langs,
                offset=int(self.cfg.download.offset)),
            limit=limit)

    def persist(self):
        """Picks up any new files in the corpus download directory, extracts
        the raw etexts and tags the etext with metadata in the corpus database.

        """
        session = self._dbsession()
        existing = set(etext.etextno for etext in session.query(EText).all())
        files = osutil.listfiles(self.cfg.download.data_path, absolute=False)
        num_added = 0
        _new_etext = functutil.ignore(Exception)(EText.from_file)
        for path in files:
            logging.debug('processing %s', path)
            etext = _new_etext(path, self.etext_metadata())
            if etext and etext.etextno not in existing:
                session.add(etext)
                existing.add(etext.etextno)
                num_added += 1
                if num_added % 100 == 0:
                    logging.debug('committing')
                    session.commit()
        session.commit()

    def __len__(self):
        return self._dbsession().query(EText.author).distinct().count()

    def __repr__(self):
        return ('{clsname}(num_authors={num_authors})'
                .format(
                    clsname=self.__class__.__name__,
                    num_authors=len(self),
                ))


class EText(ORM_BASE):
    """Bag-of-properties representing a Project Gutenberg etext. The class also
    provides ORM with the on-disk database for the corpus.

    """
    __tablename__ = 'etexts'

    etextno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.Unicode)
    title = sqlalchemy.Column(sqlalchemy.Unicode)
    path = sqlalchemy.Column(sqlalchemy.String)

    @classmethod
    def from_file(cls, path, etext_metadata):
        """Creates an etext from a file on disk. Consults a metadata database
        to tag the etext with author and title information.

        Args:
            path (str): the path to the etext file to load
            etext_metadata (dict): the metadata database to consult

        Returns:
            EText: an object representation of the etext file

        """
        ident = metainfo.etextno(osutil.readfile(path, encoding='latin1'))
        metadata = etext_metadata[ident]
        author = metadata.get('author')
        title = metadata.get('title')
        path = beautify.clean_and_compress(path)
        return cls(etextno=ident, author=author, title=title, path=path)

    def __repr__(self):
        return ('{clsname}(author="{author}", title="{title}", path="{path}")'
                .format(
                    clsname=self.__class__.__name__,
                    author=self.author,
                    title=self.title,
                    path=self.path,
                ))
