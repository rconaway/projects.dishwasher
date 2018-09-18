from config.common import *
from typing import NamedTuple


class BitElement(NamedTuple):
    name: str
    description: str
    value: str
    infos: List[str]

    def dump(self):
        return [""] + dump_infos(self.infos) + \
               [f"// <q> {self.name} {self.description}"] + \
               dump_macro_definition(self.name, self.value)

    def key_values(self):
        return {self.name: self.value}


def parse(i: int, doc: List[str]):
    """
    >>> parse(0, [
    ...     "// <i> some info",
    ...     "",
    ...     "// <q> FOO the description",
    ...     "// <i> more info",
    ...     "#ifndef FOO",
    ...     "#define FOO 1",
    ...     "#endif",
    ... ])
    (7, BitElement(name='FOO', description='the description', value='1', infos=['some info', 'more info']))
    """

    i, name, description, infos = parse_element_header(i, doc, "q")
    i, value, minfos = parse_macro_definition(i, doc, name)

    return i, BitElement(name, description, value, infos + minfos)

