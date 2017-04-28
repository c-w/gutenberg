"""Module to deal with type validation."""

from __future__ import unicode_literals
import sys

from rdflib.term import bind

from gutenberg._domain_model.exceptions import InvalidEtextIdException


def validate_etextno(etextno):
    """
    Raises:
        InvalidEtextId: If the argument does not represent a valid Project
            Gutenberg text idenfifier.

    """
    if not isinstance(etextno, int) or etextno <= 0:
        raise InvalidEtextIdException
    return etextno


def rdf_bind_to_string(rdf_type):
    """Python2/3 compatibility wrapper around rdflib.term.bind that binds a
    term to the appropriate string type.

    """
    string_type = unicode if sys.version_info < (3,) else str  # noqa
    bind(rdf_type, string_type)
