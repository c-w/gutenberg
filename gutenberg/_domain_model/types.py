"""Module to deal with type validation."""


from gutenberg._domain_model.exceptions import InvalidEtextIdException


def validate_etextno(etextno):
    """
    Raises:
        InvalidEtextId: If the argument does not represent a valid Project
            Gutenberg text identifier.

    """
    if not isinstance(etextno, int) or etextno <= 0:
        raise InvalidEtextIdException
    return etextno
