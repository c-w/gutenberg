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


class GutenbergCorpusConfigMapping(configutil.ConfigMapping):
    """Project Gutenberg configuation options.

    """
    class DownloadSection(configutil.ConfigMapping.Section):
        """Corpus downloading configuration options.

        Attributes:
            data_path (str): The path to which to dump the downloaded data.
            offset (int): The page from which to start downloading.

        """
        def __init__(self, basedir):
            configutil.ConfigMapping.Section.__init__(self)
            self.data_path = os.path.join(basedir, 'rawdata')
            self.offset = 0

    class MetadataSection(configutil.ConfigMapping.Section):
        """Corpus metadata configuration options.

        Attributes:
            metadata (str): The path to the corpus metadata file.

        """
        def __init__(self, basedir):
            configutil.ConfigMapping.Section.__init__(self)
            self.metadata = os.path.join(basedir, 'metadata.json.gz')

    class DatabaseSection(configutil.ConfigMapping.Section):
        """Corpus database configuration options.

        Attributes:
            drivername (str): The type of database backend that should be used.
            username (str): The user that should connect to the database.
            password (str): The database password.
            host (str): The database host.
            port (int): The database port.
            database (str): The path to the database.

        """
        def __init__(self, basedir):
            configutil.ConfigMapping.Section.__init__(self)
            self.drivername = 'sqlite'
            self.username = None
            self.password = None
            self.host = None
            self.port = None
            self.database = os.path.join(basedir, 'gutenberg.db3')

    def __init__(self, basedir='corpus'):
        configutil.ConfigMapping.__init__(self)
        self.download = GutenbergCorpusConfigMapping.DownloadSection(basedir)
        self.metadata = GutenbergCorpusConfigMapping.MetadataSection(basedir)
        self.database = GutenbergCorpusConfigMapping.DatabaseSection(basedir)


class GutenbergCorpus(object):
    """Object representing the Project Gutenberg corpus. The object offers a
    simple interface to functionality such as downloading the corpus, removing
    headers, persisting meta-data to a database, etc.

    Attributes:
        cfg (GutenbergCorpusConfigMapping): Corpus configuration options.

    """
    def __init__(self):
        self.cfg = GutenbergCorpusConfigMapping()

    @classmethod
    def using_config(cls, config_path):
        """Initialize a corpus using the settings specified in a configuration
        file. Any non-specified settings are set to the default values.

        Args:
            config_path (str): The path to the .cfg file.

        Returns:
            GutenbergCorpus: A corpus respecting the settings in the
                configuration file.

        """
        corpus = cls()
        corpus.cfg.merge(GutenbergCorpusConfigMapping.from_config(config_path))
        return corpus

    def write_config(self, path):
        """Dump the configuration options of the corpus to a file for later
        restoring.

        Args:
            path (str): The path to which to write the configuration file.

        """
        self.cfg.write_config(path)

    def _dbsession(self):
        """Creates a database session respecting the configuration settings of
        the corpus.

        Returns:
            sqlalchemy.orm.Session: A database session.

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
    def _etext_metadata(self):
        """Reads a database of etext metadata from disk (or creates the
        database if it does not exist). The metadata contains information such
        as title, author, etc.

        Returns:
            dict: A mapping from etext-identifier to etext-metadata.

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
            filetypes (str, optional): The etext formats to download.
            langs (str, optional): The etext languages to download.
            limit (int, optional): Number of bytes of etexts to download.

        """
        osutil.makedirs(self.cfg.download.data_path)
        self.cfg.download.offset = download.download_corpus(
            self.cfg.download.data_path,
            download.CorpusDownloadContext(
                filetypes=filetypes,
                langs=langs,
                offset=int(self.cfg.download.offset)),
            limit=limit)
        self._persist()

    def _persist(self):
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
            etext = _new_etext(path, self._etext_metadata())
            if etext and etext.etextno not in existing:
                session.add(etext)
                existing.add(etext.etextno)
                num_added += 1
                if num_added % 100 == 0:
                    logging.debug('committing')
                    session.commit()
        session.commit()

    def __len__(self):
        """Counts the number of authors in the corpus.

        """
        return self._dbsession().query(EText.author).distinct().count()

    def __repr__(self):
        return ('{clsname}(num_authors={num_authors})'
                .format(
                    clsname=self.__class__.__name__,
                    num_authors=len(self),
                ))

    def __getitem__(self, author):
        """Retrieves an object representation of a particular author.

        """
        return GutenbergAuthor(author, self._dbsession().query(EText))

    def author_names(self):
        """Iterates over the names of the authors in the corpus.

        """
        return iter(etext.author for etext in self._dbsession()
                    .query(EText.author)
                    .distinct()
                    .order_by(EText.author))

    def authors(self):
        """Iterates over the object representations of the corpus' authors.

        """
        for author_name in self.author_names():
            yield self[author_name]


class GutenbergAuthor(object):
    """Object representing an author in the Project Gutenberg corpus. An author
    is characterized by his collected works.

    Attributes:
        name (str): The name of the author.
        _dbview (sqlalchemy.orm.query.Query): A database query that can be
            extended for further refinement but will only consider this
            particular author.

    """
    def __init__(self, name, dbview):
        self.name = name
        self._dbview = dbview.from_self(EText).filter(EText.author == name)

    def __len__(self):
        """Counts the number of works of the author.

        """
        return self._dbview.from_self(EText.title).distinct().count()

    def __repr__(self):
        return ('{clsname}(name="{name}", num_works={num_works})'
                .format(
                    clsname=self.__class__.__name__,
                    name=self.name,
                    num_works=len(self),
                ))

    def __getitem__(self, title):
        """Retrieves an object representation of a particular text of the
        author.

        """
        return GutenbergText(title, self._dbview)

    def work_names(self):
        """Iterates over the names of the works of the author.

        """
        return iter(etext.title for etext in self._dbview
                    .distinct()
                    .order_by(EText.title))

    def works(self):
        """Iterates over the object representations of the authors' titles.

        """
        for title in self.work_names():
            yield self[title]


class GutenbergText(object):
    """Object representing a work in the Project Gutenberg corpus.

    Attributes:
        title (str): The title of the work.
        _dbview (sqlalchemy.orm.query.Query): A database query that can be
            extended for further refinement but will only consider this
            particular work.

    """
    def __init__(self, title, dbview):
        self.title = title
        self._dbview = dbview.from_self(EText).filter(EText.title == title)

    def __repr__(self):
        return ('{clsname}(title="{title}")'
                .format(
                    clsname=self.__class__.__name__,
                    title=self.title,
                ))

    def lines(self):
        """Iterates over the lines in the work.

        """
        return osutil.readfile(self._dbview.first().path, encoding='latin1')

    @property
    @functutil.memoize
    def fulltext(self):
        """Unicode representation of the work.

        """
        return u'\n'.join(self.lines())


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
            path (str): The path to the etext file to load.
            etext_metadata (dict): The metadata database to consult.

        Returns:
            EText: An object representation of the etext file.

        """
        ident = metainfo.etextno(osutil.readfile(path, encoding='latin1'))
        metadata = etext_metadata[ident]
        author = metadata.get('author')
        title = metadata.get('title')
        if author is None:
            logging.warning('no author meta-data found for etext %s', ident)
        if title is None:
            logging.warning('no title meta-data found for etext %s', ident)
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
