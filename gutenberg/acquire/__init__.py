"""Package to deal with interfacing with the Project Gutenberg servers:
download texts, download meta-data, etc."""


from . text import load_etext  # noqa
from . metadata import load_metadata  # noqa
from . metadata import get_metadata_cache  # noqa
from . metadata import set_metadata_cache  # noqa
