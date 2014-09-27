"""Utility methods to deal with serialization."""


import gzip
try:
    import cPickle as pickle
except ImportError:
    import pickle


class SerializableObject(object):
    """An object that can be dumped to and loaded from disk.

    """
    @classmethod
    def load(cls, path):
        """Deserialize an instance from disk.

        Arguments:
            path (str): The location of the serialized instance.

        Returns:
            SerializableObject: The deserialized instance.

        """
        with gzip.open(path, 'rb') as serialized:
            obj = pickle.load(serialized)
        return obj

    def dump(self, path):
        """Serializes an instance to disk.

        Arguments:
            path (str): The location to which to serialize the instance.

        """
        with gzip.open(path, 'wb') as serialized:
            pickle.dump(self, serialized)
