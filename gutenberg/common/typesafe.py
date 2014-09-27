"""Utility functions to deal with type-safety."""


import types


def namedtuple(clsname, field_info):  # pylint: disable=R0912
    """Factory that creates a type with a given name and fields.
    This is essentially a version of collections.namedtuple that enforces the
    types of its arguments.

    Arguments:
        clsname (str): The name of the type to create.
        field_info (list): A list of field-name and field-type pairs.

    Returns:
        TypesafeNamedTuple: A type-safe version of collections.namedtuple.

    Examples:
        >>> Point = namedtuple('Point', (('x', int), ('y', int)))
        >>> p1 = Point(1, 2)
        >>> p1.x, p1.y
        (1, 2)

        >>> p2 = Point(x=1, y=2)
        >>> p2 == p1
        True

        >>> Point(1)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: too few arguments to initialize...

        >>> Point('1', '2')  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        TypeError: bad argument...

        >>> del Point(1, y=2).x  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        TypeError: unable to delete attribute...

        >>> Point(1, 2).x = 4  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        TypeError: unable to set attribute...

    """
    def create_initvals(*args, **kwargs):
        """Concatenates args and kwargs.

        """
        initvals = dict(kwargs)
        arg_names = (name for name, _ in field_info if name not in initvals)
        for arg, arg_name in zip(args, arg_names):
            initvals[arg_name] = arg
        return initvals

    def validate_nargs(initvals):
        """Makes sure that there are enough arguments available for the closure
        constructor.

        Raises:
            ValueError: If there are not enough arguments to the namedtuple.

        """
        if len(initvals) != len(field_info):
            raise ValueError(
                'too few arguments to initalize {clsname} '
                '(need {num_required}, have {num_available})'
                .format(
                    clsname=clsname,
                    num_required=len(field_info),
                    num_available=len(initvals)))

    def validate_types(initvals):
        """Makes sure that the arguments to the closure constructor all are of
        the requisite types.

        Raises:
            TypeError: If one of the arguments has a type inconsistent with the
                       type signature of the namedtuple.

        """
        for field_name, field_type in field_info:
            field_value = initvals[field_name]
            if not isinstance(field_value, (field_type, types.NoneType)):
                raise TypeError(
                    'bad argument "{field_value}": field {field_name} can '
                    'only store values of type {type_required}  '
                    '(have {type_available})'
                    .format(
                        field_value=field_value,
                        field_name=field_name,
                        type_required=field_type,
                        type_available=type(field_value)))

    class TypesafeNamedTuple(object):  # pylint: disable=R0903
        """Closure.

        """
        def __init__(self, *args, **kwargs):
            _fields = [field_name for field_name, _ in field_info]
            _types = [field_type for _, field_type in field_info]
            object.__setattr__(self, '_fields', _fields)
            object.__setattr__(self, '_types', _types)

            initvals = create_initvals(*args, **kwargs)
            validate_nargs(initvals)
            validate_types(initvals)
            for field_name, field_value in initvals.iteritems():
                object.__setattr__(self, field_name, field_value)

        def __repr__(self):
            return '{clsname}({fields})'.format(
                clsname=clsname,
                fields=', '.join('%s=%s' % (attr, getattr(self, attr))
                                 for attr, _ in field_info))

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return all(getattr(self, field_name) == getattr(other, field_name)
                       for field_name, _ in field_info)

        def __delattr__(self, *args):
            """Immutable class - disabled.

            """
            raise TypeError(
                'unable to delete attribute: {clsname} is immutable'
                .format(clsname=clsname))

        def __setattr__(self, *args):
            """Immutable class - disabled.

            """
            raise TypeError(
                'unable to set attribute: {clsname} is immutable'
                .format(clsname=clsname))

    return TypesafeNamedTuple
