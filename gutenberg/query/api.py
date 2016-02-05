"""Module defining the public Gutenberg Query API"""
# pylint: disable=R0921


from __future__ import absolute_import
import abc
import os

from six import with_metaclass
from rdflib.term import URIRef

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
        feature_name (str): The the meta-data on which to select the texts.
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


class MetadataExtractor(with_metaclass(abc.ABCMeta, object)):
    """This class represents the interface by which the public functions in
    this API can be extended to provide access to Project Gutenberg meta-data.
    For each meta-data feature X that we want to be able to extract via the
    get_metadata and get_etexts functions, we should create a matching
    MetadataExtractor implementation that returns X for its feature_name call.

    """
    @abstractclassmethod
    def feature_name(cls):
        """The keyword that will cause the top-level API methods get_metadata
        and get_etexts to delegate work to this MetadatExtractor. If
        feature_name returns a value X, the API calls get_metadata(X, ...) and
        get_etexts(X, ...) will delegate work to this MetadataExtractor.

        """
        raise NotImplementedError

    @abstractclassmethod
    def get_metadata(cls, etextno):
        """Look up and return the meta-data value for this MetadataExtractor's
        feature-name for the given text.

        """
        raise NotImplementedError

    @abstractclassmethod
    def get_etexts(cls, value):
        """Look up and return the text identifiers whose meta-data about this
        MetadataExtractor's feature name match the provided query.

        """
        raise NotImplementedError

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
        """Converts the the representation used to identify a text in the
        meta-data RDF graph to a human-friendly integer text identifier.

        """
        return validate_etextno(int(os.path.basename(uri_ref.toPython())))

    @staticmethod
    def __find_implementations():
        """Returns all the concrete subclasses of MetadataExtractor.

        """
        implementations = {}
        for implementation in all_subclasses(MetadataExtractor):
            try:
                implementations[implementation.feature_name()] = implementation
            except NotImplementedError:
                pass
        return implementations

    @staticmethod
    def get(feature_name):
        """Returns the MetadataExtractor that can extract information about the
        provided feature name.

        Raises:
            UnsupportedFeature: If no extractor exists for the feature name.

        """
        implementations = MetadataExtractor.__find_implementations()
        try:
            return implementations[feature_name]
        except KeyError:
            raise UnsupportedFeatureException(
                'no MetadataExtractor registered for feature "{feature_name}" '
                '(try any of the following: {supported_features})'
                .format(feature_name=feature_name,
                        supported_features=', '.join(sorted(implementations))))
