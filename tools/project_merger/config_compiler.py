
from typing import List
from typing import NamedTuple
import re

def parse(doc):
    """Parse
        - sanity check
        >>> with open("sdk_config.h") as f:
        ...     text = [line.rstrip() for line in f]
        ...     x = parse(text)
        ...
    """
    (i, comment) = _parse_header_comment(0, doc)
    (i, guard) = _parse_prefix(i, doc)

    body = []

    while True:
        elt = _optional(lambda: _parse_header_block(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    i = _parse_suffix(i, doc)
    _parse_blanks(i, doc)

    if (i < len(doc)):
        raise ParseFailure(i, "Unexpected content after end of document")

    return comment, guard, body


class HeaderBlock(NamedTuple):
    name: str
    description: str
    infos: List
    body: List

def _parse_header_block(i, doc):
    (i, name, description, infos) = _parse_element_header(i, doc, "h")
    body = []

    while True:
        elt = \
            _optional(lambda: _parse_header_block(i, doc)) or \
            _optional(lambda: _parse_enable_block(i, doc)) or \
            _optional(lambda: _parse_string_element(i, doc)) or \
            _optional(lambda: _parse_bit_element(i, doc)) or \
            _optional(lambda: _parse_option_element(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    i = _parse_blanks(i, doc)
    if (doc[i] != "// </h>"):
        raise ParseFailure(i, "expected // </h>")
    i += 1

    return i, HeaderBlock(name, description, infos, body)


class EnableBlock(NamedTuple):
    name: str
    description: str
    value: str
    infos: List
    body: List

def _parse_enable_block(i, doc):
    (i, name, description, infos) = _parse_element_header(i, doc, "e")
    (i, value, minfos) = _parse_macro_definition(i, doc, name)

    body = []

    while True:
        elt = \
            _optional(lambda: _parse_header_block(i, doc)) or \
            _optional(lambda: _parse_enable_block(i, doc)) or \
            _optional(lambda: _parse_string_element(i, doc)) or \
            _optional(lambda: _parse_bit_element(i, doc)) or \
            _optional(lambda: _parse_option_element(i, doc))

        if elt:
            body.append(elt[1])
            i = elt[0]
        else:
            break

    i = _parse_blanks(i, doc)
    if (doc[i] != "// </e>"):
        raise ParseFailure(i, "expected // </e>")

    i+= 1

    return i, EnableBlock(name, description, value, infos + minfos, body)


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
    while (e < len(doc) and doc[e].strip() != "*/"):
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

    i = _parse_blanks(i, doc)

    p = re.compile("#ifndef (\S+)$")
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, "Expected #ifndef guard")
    guard_macro = m.group(1)
    i = _parse_blanks(i + 1, doc)

    p = re.compile("#define (\S+)$")
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, "Expected #define guard")
    if guard_macro != m.group(1):
        raise ParseFailure(i, f"guard macro mismatch: {guard_macro} / {m.group(1)}")
    i = _parse_blanks(i + 1, doc)

    if not "<<< Use Configuration Wizard in Context Menu >>>" in doc[i]:
        raise ParseFailure(i, "Expected <<< Use Configuration Wizard in Context Menu >>>")
    i = _parse_blanks(i + 1, doc)

    if doc[i] != "#ifdef USE_APP_CONFIG":
        raise ParseFailure(i, "Expected #ifdef USE_APP_CONFIG")
    i = _parse_blanks(i + 1, doc)

    if doc[i] != '#include "app_config.h"':
        raise ParseFailure(i, 'Expected #include "app_config.h"')
    i = _parse_blanks(i + 1, doc)

    if doc[i] != "#endif":
        raise ParseFailure(i, "Expected #endif")
    i = _parse_blanks(i + 1, doc)

    return i, guard_macro


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

    i = _parse_blanks(i, doc)
    if "<<< end of configuration section >>>" in doc[i]:
        i += 1

    i = _parse_blanks(i, doc)

    if not doc[i].startswith("#endif "):
        raise ParseFailure(i, "Expected #endif")

    return _parse_blanks(i + 1, doc)


class StringElement(NamedTuple):
    name: str
    description: str
    value: str
    infos: List

def _parse_string_element(i, doc):
    """
    >>> _parse_string_element(0, [
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

    i, name, description, infos = _parse_element_header(i, doc, "s")
    i, value, minfos = _parse_macro_definition(i, doc, name)
    infos += minfos

    return i, StringElement(name, description, value, infos)


class BitElement(NamedTuple):
    name: str
    description: str
    value: str
    infos: List

def _parse_bit_element(i, doc):
    """
    >>> _parse_bit_element(0, [
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

    i, name, description, infos = _parse_element_header(i, doc, "q")
    i, value, minfos = _parse_macro_definition(i, doc, name)
    infos += minfos

    return i, BitElement(name, description, value, infos)


class OptionElement(NamedTuple):
    name: str
    description: str
    value: str
    options: List
    infos: List
    option_infos: List
    macro_infos: List

def _parse_option_element(i, doc):
    """
    >>> _parse_option_element(0, [
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

    i, name, description, infos = _parse_element_header(i, doc, "o")
    i, options, option_infos = _parse_options(i, doc)
    i, value, macro_infos = _parse_macro_definition(i, doc, name)

    return i, OptionElement(name, description, value, options, infos, option_infos, macro_infos)



def _parse_macro_definition(i, doc, name):
    """Parse #ifndef ... #define macro definition, absorbing info lines

    >>> _parse_macro_definition(0, [
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

    p = re.compile("#ifndef (\S+)$")
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, "Expected #ifndef")
    if (name != m.group(1)):
        raise ParseFailure(i, "Macro name does not match element")

    p = re.compile("#define (\S+) (.+)$")
    m = p.match(doc[i+1])
    if not m:
        raise ParseFailure(i, "Expected #define")
    if (name != m.group(1)):
        raise ParseFailure(i, "#ifndef and #define have different macro names")
    value = m.group(2)

    if doc[i+2] != "#endif":
        raise ParseFailure(i, "Expected #endif")

    return i + 3, value, infos


def _parse_element_header(i, doc, tag):
    """Parse element header, absorbing info lines before the header

    - Minimal
    >>> _parse_element_header(0, [
    ...     "// <x> the_name the description",
    ... ], "x")
    (1, 'the_name', 'the description', [])

    - Fully loaded
    >>> _parse_element_header(0, [
    ...     "",                             # ignores leading blank lines
    ...     "// <i> Some info",             # absorbs infos
    ...     "",                             # ignores blanks
    ...     "// <x> the_name the description",  # first word is name, rest is description
    ...     "",                             # stops after header
    ... ], "x")
    (4, 'the_name', 'the description', ['Some info'])

    - No description
    >>> _parse_element_header(0, [
    ...     "// <x> the_name",
    ... ], "x")
    (1, 'the_name', '', [])

    - Fail
    >>> try:
    ...     _parse_element_header(0, [
    ...         "// <i> Some info",
    ...         "// <x>",
    ...     ], "x")
    ... except ParseFailure as e:
    ...     e
    ParseFailure(1, 'Not an element header')
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    i = _parse_blanks(i, doc)
    i, infos = parse_info(i, doc)

    p = re.compile("// <(\S)> (\S+)\s*(.*)$")
    m = p.match(doc[i])
    if not m:
        raise ParseFailure(i, "Not an element header")
    if tag != m.group(1):
        raise ParseFailure(i, f"Expected <{tag}> element")

    (name, description) = (m.group(2), m.group(3))
    return i + 1, name, description, infos


def _parse_options(i, doc):
    """parse a list of option values, absorbing info lines.  Return empty list if none.

    >>> _parse_options(0, [
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

    i = _parse_blanks(i, doc)
    i, infos = parse_info(i, doc)

    options = []
    p = re.compile("// <(\S+)=>\s+(.+)$")

    while True:
        m = p.match(doc[i])
        if not m:
            return i, options, infos

        options.append((m.group(1), m.group(2)))
        i += 1


def _parse_blanks(i, doc):
    """Advance index past empty lines and separator lines

    - Blanks
    >>> _parse_blanks(0, ["", "", "foo"])
    2

    - No op if no blanks
    >>> _parse_blanks(0, ["foo"])
    0

    - Skip to end of file
    >>> _parse_blanks(0, [""])
    1
    """
    assert isinstance(i, int)
    assert isinstance(doc, List)

    while i < len(doc) and (doc[i].strip() == "" or doc[i].startswith("//=")):
        i += 1

    return i


def parse_info(i, doc):
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
        i = _parse_blanks(i, doc)
        if i == len(doc):
            return i, text

        m = p.match(doc[i])
        if not m:
            return i, text

        text.append(m.group(1))
        i += 1



def _optional(action):
    try:
        return action()
    except ParseFailure as e:
        return None


class ParseFailure(Exception):

    def __init__(self, index, message):
        self.index = index
        self.message = message

