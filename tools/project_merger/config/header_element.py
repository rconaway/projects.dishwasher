from config.common import *
from typing import NamedTuple
import config.enable_element as enable_element
import config.string_element as string_element
import config.bit_element as bit_element
import config.option_element as option_element


class HeaderElement(NamedTuple):
    name: str
    description: str
    infos: List
    body: List


def parse(i, doc):
    (i, name, description, infos) = parse_element_header(i, doc, "h")
    i, body = _parse_body(i, doc)
    i = parse_blanks(i, doc)
    i, = parse_pattern(i, doc, "// </h>")

    return i, HeaderElement(name, description, infos, body)


def _parse_body(i, doc):
    body = []

    while True:
        elt = \
            optional(lambda: parse(i, doc)) or \
            optional(lambda: enable_element.parse(i, doc)) or \
            optional(lambda: string_element.parse(i, doc)) or \
            optional(lambda: bit_element.parse(i, doc)) or \
            optional(lambda: option_element.parse(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    return i, body
