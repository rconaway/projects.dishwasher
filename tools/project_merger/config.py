from enum import Enum
from typing import List
import re

class ConfigTag(Enum):
    BLOCK_COMMENT = "Block Comment"
    HEADER_GUARD_BEGIN = "Header Guard"
    HEADER_GUARD_END = "Header Guard End"
    CONFIG_SECTION_BEGIN = "Config Section Begin"
    CONFIG_SECTION_END = "Config Section End"
    APP_CONFIG = "App Config"
    STRUCTURE_BEGIN = "Structure Begin"
    STRUCTURE_END = "Structure End"
    NAMED_VALUE = "Named Value"
    MACRO_DEFINITION = "Macro Definition"

def parse(text: List[str]):

    result = []
    while (text):
        parsed = \
            _parse_block_comment(text) or \
            _parse_header_guard(text) or \
            _parse_configuration_begin(text) or \
            _parse_configuration_end(text) or \
            _parse_app_config(text) or \
            _parse_structure_begin(text) or \
            _parse_structure_end(text) or \
            _parse_named_value(text) or \
            _parse_blank_line(text) or \
            _parse_separator_line(text) or \
            _parse_macro_definition(text) or \
            _parse_header_guard_end(text)

        if (parsed):
            (elt, text) = parsed
            if (elt != None):
                result.append(elt)
        else:
            raise RuntimeError(f"Unexpected text while parsing: {text[0]}")

    return result


def _parse_block_comment(text: List[str]):

    if text[0] != "/**":
        return None

    end = text.index(" */")

    return (
        (ConfigTag.BLOCK_COMMENT, text[1:end]),
        text[end+1:]
    )

def _parse_header_guard(text: List[str]):
    if_pattern = re.compile("#ifndef\\s+(\\S+)\\s*$")
    define_pattern = re.compile("#define\\s+(\\S+)\\s*$")

    m = if_pattern.match(text[0])
    if (not m):
        return None

    label = m.group(1)

    m = define_pattern.match(text[1])
    if (not m):
        return None

    if (label != m.group(1)):
        raise RuntimeError(f"labels do not match: {label}, {m.group(1)}")

    return (ConfigTag.HEADER_GUARD_BEGIN, label), text[2:]

def _parse_configuration_begin(text: List[str]):
    p = re.compile("\\s*//\\s+<<< Use Configuration Wizard in Context Menu >>>")
    m = p.match(text[0])
    if (m):
        return (ConfigTag.CONFIG_SECTION_BEGIN,), text[1:]
    else:
        return None

def _parse_configuration_end(text: List[str]):
    p = re.compile("\\s*//\\s+<<< end of configuration section >>>")
    m = p.match(text[0])
    if (m):
        return (ConfigTag.CONFIG_SECTION_END,), text[1:]
    else:
        return None

def _parse_app_config(text: List[str]):
    expected = [
        "#ifdef USE_APP_CONFIG",
        '#include "app_config.h"',
        "#endif"
        ]
    if (text[0:3] == expected):
        return ((ConfigTag.APP_CONFIG,), text[3:])
    else:
        return None

def _parse_structure_begin(text: List[str]):
    p = re.compile("\\s*//\\s+<([heoiqs])>\\s+(\\S+)\\s*(.*)$")
    m = p.match(text[0])
    if (m):
        return (ConfigTag.STRUCTURE_BEGIN, m.group(1), m.group(2), m.group(3)), text[1:]
    else:
        return None

def _parse_structure_end(text: List[str]):
    p = re.compile("\\s*//\\s+</([he])>\\s*$")
    m = p.match(text[0])
    if (m):
        return (ConfigTag.STRUCTURE_END, m.group(1)), text[1:]
    else:
        return None


def _parse_named_value(text: List[str]):
    p = re.compile("\\s*//\\s+<(\\S+)=>\\s+(.+)\\s*$")
    m = p.match(text[0])
    if (m):
        return (ConfigTag.NAMED_VALUE, m.group(2), m.group(1)), text[1:]
    else:
        return None

def _parse_blank_line(text: List[str]):
    if (text[0].strip() == ""):
        return None, text[1:]
    else:
        return None

def _parse_separator_line(text: List[str]):
    p = re.compile("\\s*//\\s*=+\\s*$")
    if p.match(text[0]):
        return None, text[1:]
    else:
        return None

def _parse_macro_definition(text: List[str]):
    p_if = re.compile("#ifndef\\s+(\\S+)")
    p_def = re.compile("#define\\s+(\\S+)\\s+(\\S+)")

    m = p_if.match(text[0])
    if not m:
        return None
    name = m.group(1)

    m = p_def.match(text[1])
    if not m:
        return None
    value = m.group(2)

    if (m.group(1) != name):
        raise RuntimeError(f"mismatched macro names: {name}, {m.group(1)}")

    if text[2] != "#endif":
        return None

    return (ConfigTag.MACRO_DEFINITION, name, value), text[3:]

def _parse_header_guard_end(text: List[str]):
    p = re.compile("#endif\\s+")
    m = p.match(text[0])

    if (m):
        return (ConfigTag.HEADER_GUARD_END,), text[1:]
    else:
        return None
