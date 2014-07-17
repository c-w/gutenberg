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


Base = sqlalchemy.ext.declarative.declarative_base()


class GutenbergCorpus(object):
    def __init__(self):
        BASEDIR = 'ProjectGutenbergCorpus'
        self.cfg = configutil.ConfigMapping()
        self.cfg.download = configutil.ConfigMapping.Section()
        self.cfg.download.data_path = os.path.join(BASEDIR, 'rawdata')
        self.cfg.download.offset = 0
        self.cfg.metadata = configutil.ConfigMapping.Section()
        self.cfg.metadata.metadata = os.path.join(BASEDIR, 'metadata.json.gz')
        self.cfg.database = configutil.ConfigMapping.Section()
        self.cfg.database.drivername = 'sqlite'
        self.cfg.database.username = None
        self.cfg.database.password = None
        self.cfg.database.host = None
        self.cfg.database.port = None
        self.cfg.database.database = os.path.join(BASEDIR, 'gutenberg.db3')

    @classmethod
    def using_config(cls, config_path):
        corpus = GutenbergCorpus()
        corpus.cfg.merge(configutil.ConfigMapping.from_config(config_path))
        return corpus

    def write_config(self, path):
        self.cfg.write_config(path)

    @functutil.memoize
    def etext_metadata(self):
        opener = osutil.opener
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

    def download(self, filetypes='txt', langs='en'):
        osutil.makedirs(self.cfg.download.data_path)
        self.cfg.download.offset = download.download_corpus(
            self.cfg.download.data_path, filetypes=filetypes, langs=langs,
            offset=int(self.cfg.download.offset))

    def cleanup(self):
        _cleanup = functutil.ignore(Exception)(beautify.clean_and_compress)
        for path in osutil.listfiles(self.cfg.download.data_path):
            logging.debug('processing %s', path)
            _cleanup(path)

    def _dbsession(self):
        osutil.makedirs(os.path.dirname(self.cfg.database.database))
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
            drivername=self.cfg.database.drivername,
            username=self.cfg.database.username,
            password=self.cfg.database.password,
            host=self.cfg.database.host,
            port=self.cfg.database.port,
            database=osutil.canonical(self.cfg.database.database),
        ))
        Base.metadata.create_all(engine)
        new_session = sqlalchemy.orm.sessionmaker(bind=engine)
        return new_session()

    def persist(self):
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


class EText(Base):
    __tablename__ = 'etexts'

    etextno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.Unicode)
    title = sqlalchemy.Column(sqlalchemy.Unicode)
    path = sqlalchemy.Column(sqlalchemy.String)

    @classmethod
    def from_file(cls, path, etext_metadata):
        ident = metainfo.etextno(osutil.readfile(path, encoding='latin1'))
        metadata = etext_metadata[ident]
        author = metadata.get('author')
        title = metadata.get('title')
        path = beautify.clean_and_compress(path)
        return EText(etextno=ident, author=author, title=title, path=path)

    def __repr__(self):
        return ('{clsname}(author="{author}", title="{title}", path="{path}")'
                .format(
                    clsname=self.__class__.__name__,
                    author=self.author,
                    title=self.title,
                    path=self.path,
                ))


def _main():
    """This function implements the main/script/command-line functionality of
    the module and will be called from the `if __name__ == '__main__':` block.

    """
    import gutenberg.common.cliutil as cliutil

    doc = 'command line utilities to manage the Project Gutenberg corpus'
    parser = cliutil.ArgumentParser(description=doc)
    parser.add_argument('configfile', type=str, nargs='?',
                        help='path to corpus configuration file')
    parser.add_argument('--download', action='store_true',
                        help='download more etexts')
    parser.add_argument('--cleanup', action='store_true',
                        help='cleanup etexts (remove headers etc.)')
    parser.add_argument('--persist', action='store_true',
                        help='persist meta-data of etexts to database')
    args = parser.parse_args()

    corpus = (GutenbergCorpus() if args.configfile is None
              else GutenbergCorpus.using_config(args.configfile))
    if args.download:
        corpus.download()
    if args.cleanup:
        corpus.cleanup()
    if args.persist:
        corpus.persist()


if __name__ == '__main__':
    _main()
