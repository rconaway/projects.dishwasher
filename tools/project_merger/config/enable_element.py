from config.common import *
from typing import NamedTuple
import config.header_element as header_element
import config.bit_element as bit_element
import config.string_element as string_element
import config.option_element as option_element


class EnableElement(NamedTuple):
    name: str
    description: str
    value: str
    infos: List
    body: List

    def dump(self):
        return dump_infos(self.infos) + \
            ["",
             f"// <e> {self.name} {self.description}",
             "//=========================================================="] + \
            dump_macro_definition(self.name, self.value) + \
            indent(flatten([x.dump() for x in self.body])) + \
            ["// </e>"]


def parse(i, doc):
    i, name, description, infos = parse_element_header(i, doc, "e")
    i, value, minfos = parse_macro_definition(i, doc, name)
    i, body = _parse_body(i, doc)
    i = parse_blanks(i, doc)
    i, = parse_pattern(i, doc, "// </e>")

    return i, EnableElement(name, description, value, infos + minfos, body)


def _parse_body(i, doc):
    body = []

    while True:
        elt = \
            optional(lambda: header_element.parse(i, doc)) or \
            optional(lambda: parse(i, doc)) or \
            optional(lambda: string_element.parse(i, doc)) or \
            optional(lambda: bit_element.parse(i, doc)) or \
            optional(lambda: option_element.parse(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    return i, body
