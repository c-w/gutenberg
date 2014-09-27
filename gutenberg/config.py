"""Module providing implementations of the api.Corpus.Config interface."""


from . import api
import json


class JsonConfig(api.Corpus.Config):
    """Implementation of api.Corpus.Config backed by a JSON file.

    """
    def __init__(self, path):
        with open(path, 'rb') as serialized:
            self._config = json.load(serialized)

    @property
    def text_source(self):
        return api.TextSource.load(self._config['text-source'])

    @property
    def basedir(self):
        return self._config['basedir']
