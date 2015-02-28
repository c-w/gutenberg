"""Package to deal with handling meta-data about Project Gutenberg works."""


from gutenberg.query.api import get_metadata  # noqa
from gutenberg.query.api import get_etexts  # noqa

from gutenberg.query.extractors import AuthorExtractor  # noqa
from gutenberg.query.extractors import TitleExtractor  # noqa
