"""Module defining the public Gutenberg Query API"""
# pylint: disable=R0921


from __future__ import absolute_import, unicode_literals
import abc
import os

from six import with_metaclass
from rdflib.term import URIRef

from gutenberg._domain_model.exceptions import InvalidEtextIdException
from gutenberg._domain_model.exceptions import UnsupportedFeatureException
from gutenberg._domain_model.types import validate_etextno
from gutenberg._util.abc import abstractclassmethod
from gutenberg._util.objects import all_subclasses
from gutenberg.acquire.metadata import load_metadata


def get_metadata(feature_name, etextno):
    """Looks up the value of a meta-data feature for a given text.

    Arguments:
        feature_name (str): The name of the meta-data to look up.
        etextno (int): The identifier of the Gutenberg text for which to look
            up the meta-data.

    Returns:
        frozenset: The values of the meta-data for the text or an empty set if
            the text does not have meta-data associated with the feature.

    Raises:
        UnsupportedFeature: If there is no MetadataExtractor registered that
            can extract meta-data for the given feature name.

    """
    metadata_values = MetadataExtractor.get(feature_name).get_metadata(etextno)
    return frozenset(metadata_values)


def get_etexts(feature_name, value):
    """Looks up all the texts that have meta-data matching some criterion.

    Arguments:
        feature_name (str): The meta-data on which to select the texts.
        value (str): The value of the meta-data on which to filter the texts.

    Returns:
        frozenset: The set of all the Project Gutenberg text identifiers that
            match the provided query.

    Raises:
        UnsupportedFeature: If there is no MetadataExtractor registered that
            can extract meta-data for the given feature name.

    """
    matching_etexts = MetadataExtractor.get(feature_name).get_etexts(value)
    return frozenset(matching_etexts)


def list_supported_metadatas():
    """Looks up the names of all the supported meta-data that can be looked up
    via `get_metadata`.

    Returns:
        tuple: The names of all queryable meta-datas.

    """
    # noinspection PyProtectedMember
    return tuple(sorted(MetadataExtractor._implementations().keys()))


class MetadataExtractor(with_metaclass(abc.ABCMeta, object)):
    """This class represents the interface by which the public functions in
    this API can be extended to provide access to Project Gutenberg meta-data.
    For each meta-data feature X that we want to be able to extract via the
    get_metadata and get_etexts functions, we should create a matching
    MetadataExtractor implementation that returns X for its feature_name call.

    """
    __implementations = None

    @abstractclassmethod
    def feature_name(cls):
        """The keyword that will cause the top-level API methods get_metadata
        and get_etexts to delegate work to this MetadatExtractor. If
        feature_name returns a value X, the API calls get_metadata(X, ...) and
        get_etexts(X, ...) will delegate work to this MetadataExtractor.

        """
        raise NotImplementedError  # pragma: no cover

    @abstractclassmethod
    def get_metadata(cls, etextno):
        """Look up and return the meta-data value for this MetadataExtractor's
        feature-name for the given text.

        """
        raise NotImplementedError  # pragma: no cover

    @abstractclassmethod
    def get_etexts(cls, value):
        """Look up and return the text identifiers whose meta-data about this
        MetadataExtractor's feature name match the provided query.

        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _metadata(cls):
        """Returns a RDF graph representing the meta-data in the Project
        Gutenberg catalog.

        """
        return load_metadata()

    @classmethod
    def _etext_to_uri(cls, etextno):
        """Converts a Gutenberg text identifier to the representation used to
        identify the text in the meta-data RDF graph.

        """
        uri = r'http://www.gutenberg.org/ebooks/{0}'.format(etextno)
        return URIRef(uri)

    @classmethod
    def _uri_to_etext(cls, uri_ref):
        """Converts the representation used to identify a text in the
        meta-data RDF graph to a human-friendly integer text identifier.

        """
        try:
            return validate_etextno(int(os.path.basename(uri_ref.toPython())))
        except InvalidEtextIdException:
            return None

    @classmethod
    def _implementations(cls):
        """Returns all the concrete subclasses of MetadataExtractor.

        """
        if cls.__implementations:
            return cls.__implementations

        cls.__implementations = {}
        for implementation in all_subclasses(MetadataExtractor):
            try:
                feature_name = implementation.feature_name()
                cls.__implementations[feature_name] = implementation
            except NotImplementedError:
                pass
        return cls.__implementations

    @staticmethod
    def get(feature_name):
        """Returns the MetadataExtractor that can extract information about the
        provided feature name.

        Raises:
            UnsupportedFeature: If no extractor exists for the feature name.

        """
        implementations = MetadataExtractor._implementations()
        try:
            return implementations[feature_name]
        except KeyError:
            raise UnsupportedFeatureException(
                'no MetadataExtractor registered for feature "{feature_name}" '
                '(try any of the following: {supported_features})'
                .format(feature_name=feature_name,
                        supported_features=', '.join(sorted(implementations))))
