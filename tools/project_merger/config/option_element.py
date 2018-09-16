from config.common import *
from typing import NamedTuple


class OptionElement(NamedTuple):
    name: str
    description: str
    value: str
    options: List
    infos: List
    option_infos: List
    macro_infos: List


def parse(i, doc):
    """
    >>> parse(0, [
    ...     "// <i> some info",
    ...     "",
    ...     "// <o> FOO the description",
    ...     "// <i> more info",
    ...     "// <0=> zero",
    ...     "// <1=> the one",
    ...     "// <2=> two",
    ...     "// <i> even more",
    ...     "#ifndef FOO",
    ...     "#define FOO 1",
    ...     "#endif",
    ...     ""
    ... ])
    (11, OptionElement(name='FOO', description='the description', value='1', options=[('0', 'zero'), ('1', 'the one'), ('2', 'two')], infos=['some info'], option_infos=['more info'], macro_infos=['even more']))
    """
    assert isinstance(i, int)
    assert isinstance(doc, list)

    i, name, description, infos = parse_element_header(i, doc, "o")
    i, options, option_infos = parse_options(i, doc)
    i, value, macro_infos = parse_macro_definition(i, doc, name)

    return i, OptionElement(name, description, value, options, infos, option_infos, macro_infos)
