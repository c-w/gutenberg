"""Module to deal with type validation."""

from __future__ import unicode_literals
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
