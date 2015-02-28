"""Module to deal with type validation."""


def validate_etextno(etextno):
    """Raises a ValueError if the argument does not represent a valid Project
    Gutenberg text idenfifier.

    """
    if not isinstance(etextno, int) or etextno <= 0:
        msg = 'e-text identifiers should be strictly positive integers'
        raise ValueError(msg)
    return etextno
