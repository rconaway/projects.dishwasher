from typing import List
from typing import Tuple
from typing import Callable
from typing import Any

import re


def parse_pattern(i: int, doc: List[str], pattern: str) -> Tuple:
    i = parse_blanks(i, doc)

    p = re.compile(pattern)
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, f"Expected {pattern}")

    return (i + 1, ) + tuple(m.groups())


def parse_macro_definition(i: int, doc: List[str], name: str) -> Tuple:
    """Parse #ifndef ... #define macro definition, absorbing info lines

    >>> parse_macro_definition(0, [
    ...     "",                     # ignores blank lines
    ...     "// <i> some info",     # absorbs info lines
    ...     "#ifndef FOO",
    ...     "#define FOO 1",
    ...     "#endif",
    ...     ""
    ... ], "FOO")
    (5, '1', ['some info'])
    """

    i, infos = parse_info(i, doc)

    i, mname = parse_pattern(i, doc, "#ifndef (\S+)$")
    if name != mname:
        raise ParseFailure(i, "Macro check does not match element")

    i, mname, value = parse_pattern(i, doc, "#define (\S+) (.+)$")
    if name != mname:
        raise ParseFailure(i, "Macro define does not match element")

    i, = parse_pattern(i, doc, "#endif")

    return i, value, infos


def dump_macro_definition(name, value):
    return [
        f"#ifndef {name}",
        f"#define {name} {value}",
        f"#endif"
    ]


def parse_element_header(i: int, doc: List[str], tag: str) -> Tuple:
    """Parse element header, absorbing info lines before the header

    - Minimal
    >>> parse_element_header(0, [
    ...     "// <x> the_name the description",
    ... ], "x")
    (1, 'the_name', 'the description', [])

    - Fully loaded
    >>> parse_element_header(0, [
    ...     "",                             # ignores leading blank lines
    ...     "// <i> Some info",             # absorbs infos
    ...     "",                             # ignores blanks
    ...     "// <x> the_name the description",  # first word is name, rest is description
    ...     "",                             # stops after header
    ... ], "x")
    (4, 'the_name', 'the description', ['Some info'])

    - No description
    >>> parse_element_header(0, [
    ...     "// <x> the_name",
    ... ], "x")
    (1, 'the_name', '', [])

    - Fail
    >>> try:
    ...     parse_element_header(0, [
    ...         "// <i> Some info",
    ...         "// <x>",
    ...     ], "x")
    ... except ParseFailure as e:
    ...     e
    ParseFailure(1, 'Not an element header')
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    i = parse_blanks(i, doc)
    i, infos = parse_info(i, doc)

    p = re.compile(f"// <{tag}> (\S+)(\s(.*))?$")
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, "Not an element header")

    (name, description) = (m.group(1), m.group(3) if m.group(3) else '')
    return i + 1, name, description, infos


def parse_options(i: int, doc: List[str]) -> Tuple:
    """parse a list of option values, absorbing info lines.  Return empty list if none.

    >>> parse_options(0, [
    ...     "",                         # skips blanks at beginning
    ...     "// <i> some info",         # absorbs info lines
    ...     "// <0=> option zero",
    ...     "// <1=> optionOne",
    ...     "// <2=> option two",
    ...     ""                          # stops after last option
    ... ])
    (5, [('0', 'option zero'), ('1', 'optionOne'), ('2', 'option two')], ['some info'])
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    i = parse_blanks(i, doc)
    i, infos = parse_info(i, doc)

    options = []
    p = re.compile("// <(\S+)=>\s+(.+)$")

    while True:
        m = p.match(doc[i])
        if not m:
            return i, options, infos

        options.append((m.group(1), m.group(2)))
        i += 1


def parse_blanks(i: int, doc: List[str]) -> int:
    """Advance index past empty lines and separator lines

    - Blanks
    >>> parse_blanks(0, ["", "", "foo"])
    2

    - No op if no blanks
    >>> parse_blanks(0, ["foo"])
    0

    - Skip to end of file
    >>> parse_blanks(0, [""])
    1
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    while i < len(doc) and (doc[i].strip() == "" or doc[i].startswith("//=")):
        i += 1

    return i


def parse_info(i: int, doc: List[str]) -> Tuple:
    """Parse zero or more <i> elements, ignoring any blank lines

    - Happy path
    >>> parse_info(0, [
    ...     "",
    ...     "// <i> some information",
    ...     "// <i> some more",
    ...     "",
    ...     "// <i> even more",
    ...     "",
    ...     "// <s> name description"
    ... ])
    (6, ['some information', 'some more', 'even more'])

    - No info returns empty list
    >>> parse_info(0, [
    ...     "// <s> name description"
    ... ])
    (0, [])

    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    p = re.compile("// <i>\\s+(.+)")

    text = []

    while True:
        i = parse_blanks(i, doc)
        if i == len(doc):
            return i, text

        m = p.match(doc[i])
        if not m:
            return i, text

        text.append(m.group(1))
        i += 1


def dump_infos(infos):
    return [f"// <i> {x}" for x in infos]


def optional(action: Callable) -> Any:
    try:
        return action()
    except ParseFailure:
        return None


def indent(block):
    """
    >>> indent(["alpha", "beta"])
    ['    alpha', '    beta']
    """

    return ["    " + x for x in block]


def flatten(x):
    """
    >>> flatten(["alpha", "beta"])
    ['alpha', 'beta']

    >>> flatten([["alpha", "beta"], ["gamma"]])
    ['alpha', 'beta', 'gamma']
    """

    if isinstance(x, str):
        return [x]

    flattened = []
    for e in x:
        flattened += flatten(e)

    return flattened


class ParseFailure(Exception):

    def __init__(self, index, message):
        self.index = index
        self.message = message

