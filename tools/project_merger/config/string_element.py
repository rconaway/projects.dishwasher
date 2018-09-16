from config.common import *
from typing import NamedTuple


class StringElement(NamedTuple):
    name: str
    description: str
    value: str
    infos: List


def parse(i, doc):
    """
    >>> parse(0, [
    ...     "// <i> some info",
    ...     "",
    ...     "// <s> FOO the description",
    ...     "// <i> more info",
    ...     "#ifndef FOO",
    ...     "#define FOO BAZOO",
    ...     "#endif",
    ... ])
    (7, StringElement(name='FOO', description='the description', value='BAZOO', infos=['some info', 'more info']))
    """

    i, name, description, infos = parse_element_header(i, doc, "s")
    i, value, minfos = parse_macro_definition(i, doc, name)
    infos += minfos

    return i, StringElement(name, description, value, infos)
