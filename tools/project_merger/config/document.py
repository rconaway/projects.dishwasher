from config.common import *
from typing import NamedTuple
import config.header_element as header_element


class Document(NamedTuple):
    comment: str
    guard: str
    body: List


def parse(doc):
    """Parse document
        - sanity check
        >>> with open("sdk_config.h") as f:
        ...     text = [x.rstrip() for x in f]
        ...     x = parse(text)
    """

    i, comment = _parse_header_comment(0, doc)
    i, guard = _parse_prefix(i, doc)
    i, body = _parse_body(i, doc)
    i = _parse_suffix(i, doc)
    i = parse_blanks(i, doc)

    if i < len(doc):
        raise ParseFailure(i, "Unexpected content after end of document")

    return Document(comment, guard, body)


def _parse_header_comment(i, doc):
    """Parse document header comment

    >>> _parse_header_comment(0, [
    ...     "/**",
    ...     "* a line",
    ...     "* another line",
    ...     "*/"
    ... ])
    (4, ['* a line', '* another line'])
    """

    if doc[i].strip() != "/**":
        raise ParseFailure(i, "Expected beginning of block comment")

    e = i + 1
    while e < len(doc) and doc[e].strip() != "*/":
        e += 1

    return e + 1, doc[i + 1: e]


def _parse_prefix(i, doc):
    """Parse guard condition, config header, and app_config

    >>> _parse_prefix(0, [
    ... '',
    ... '#ifndef SDK_CONFIG_H',
    ... '#define SDK_CONFIG_H',
    ... '// <<< Use Configuration Wizard in Context Menu >>>\\n',
    ... '#ifdef USE_APP_CONFIG',
    ... '#include "app_config.h"',
    ... '#endif'
    ... ])
    (7, 'SDK_CONFIG_H')
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    i, guard_macro = parse_pattern(i, doc, "#ifndef (\S+)$")
    i, define_macro = parse_pattern(i, doc, "#define (\S+)$")
    if guard_macro != define_macro:
        raise ParseFailure(i, f"guard macro mismatch: {guard_macro} / {define_macro}")
    i, = parse_pattern(i, doc, "// <<< Use Configuration Wizard in Context Menu >>>")
    i, = parse_pattern(i, doc, "#ifdef USE_APP_CONFIG")
    i, = parse_pattern(i, doc, '#include "app_config.h"')
    i, = parse_pattern(i, doc, "#endif")

    return i, guard_macro


def _parse_body(i, doc):
    body = []

    while True:
        elt = optional(lambda: header_element.parse(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    return i, body


def _parse_suffix(i, doc):
    """Parse end of document

    >>> _parse_suffix(0, [
    ...     "",
    ...     "// <<< end of configuration section >>>",
    ...     "#endif //SDK_CONFIG_H",
    ...     "",
    ... ])
    4
    """

    i = parse_blanks(i, doc)
    if "<<< end of configuration section >>>" in doc[i]:
        i += 1

    i = parse_blanks(i, doc)

    if not doc[i].startswith("#endif "):
        raise ParseFailure(i, "Expected #endif")

    return parse_blanks(i + 1, doc)
