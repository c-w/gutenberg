from . import api
import json


class JsonConfig(api.Corpus.Config):
    def __init__(self, path):
        with open(path, 'rb') as serialized:
            self._config = json.load(serialized)

    @property
    def text_source(self):
        return api.TextSource.load(self._config['text-source'])

    @property
    def basedir(self):
        return self._config['basedir']
