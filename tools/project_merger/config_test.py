import unittest
import config


class config_test(unittest.TestCase):

    def test_parse_reads_the_initial_block_comment(self):
        c = config.parse([
            "/**",
            " * a line",
            " */",
        ])

        (tag, text) = c[0]
        self.assertEqual(config.ConfigTag.BLOCK_COMMENT, tag)
        self.assertEqual([" * a line"], text)

    def test_parse_reads_the_header_guard_begin(self):
        c = config.parse([
            "#ifndef SDK_CONFIG_H",
            "#define SDK_CONFIG_H",
        ])

        (tag, symbol) = c[0]
        self.assertEqual(config.ConfigTag.HEADER_GUARD_BEGIN, tag)
        self.assertEqual("SDK_CONFIG_H", symbol)

    def test_parse_verifies_that_header_guard_ifndef_and_define_match(self):
        with self.assertRaises(RuntimeError) as context:
            config.parse([
                "#ifndef SDK_CONFIG_H",
                "#define SDK_CONFIG",
            ])

        self.assertEquals("labels do not match: SDK_CONFIG_H, SDK_CONFIG", str(context.exception))

    def test_parse_finds_beginning_of_configuration_section(self):
        c = config.parse([
            "// <<< Use Configuration Wizard in Context Menu >>>"
        ])

        (tag,) = c[0]
        self.assertEquals(config.ConfigTag.CONFIG_SECTION_BEGIN, tag)

    def test_parse_finds_end_of_configuration_section(self):
        c = config.parse([
            "// <<< end of configuration section >>>"
        ])

        (tag,) = c[0]
        self.assertEquals(config.ConfigTag.CONFIG_SECTION_END, tag)

    def test_parse_finds_app_config_inclusion(self):
        c = config.parse([
            "#ifdef USE_APP_CONFIG",
            '#include "app_config.h"',
            "#endif"
        ])

        (tag,) = c[0]
        self.assertEquals(config.ConfigTag.APP_CONFIG, tag)

    def test_parse_finds_structure_element(self):
        c = config.parse([
            "// <h> nRF_Drivers - a comment"
        ])

        (tag, name, label, comment) = c[0]

        self.assertEquals(config.ConfigTag.STRUCTURE_BEGIN, tag)
        self.assertEquals("h", name)
        self.assertEquals("nRF_Drivers", label)
        self.assertEquals("- a comment", comment)

    def test_parse_finds_structure_element_without_comment(self):
        c = config.parse([
            "// <h> nRF_Drivers"
        ])

        (tag, name, label, comment) = c[0]

        self.assertEquals(config.ConfigTag.STRUCTURE_BEGIN, tag)
        self.assertEquals("h", name)
        self.assertEquals("nRF_Drivers", label)
        self.assertEquals("", comment)

    def test_parse_finds_all_defined_structure_elements(self):
        c = config.parse([
            "// <h> nRF_Drivers",
            "// <e> an e",
            "// <o> an o",
            "// <i> an i",
            "// <q> a q",
            "// <s> an s",
        ])

        self.assertEqual("h", c[0][1])
        self.assertEqual("e", c[1][1])
        self.assertEqual("o", c[2][1])
        self.assertEqual("i", c[3][1])
        self.assertEqual("q", c[4][1])
        self.assertEqual("s", c[5][1])

    def test_parse_finds_all_defined_structure_ends(self):
        c = config.parse([
            "// </h>",
            "// </e>"
        ])

        self.assertEqual(config.ConfigTag.STRUCTURE_END, c[0][0])
        self.assertEqual("h", c[0][1])
        self.assertEqual(config.ConfigTag.STRUCTURE_END, c[1][0])
        self.assertEqual("e", c[1][1])

    def test_parse_finds_named_value(self):
        c = config.parse([
            "// <0=> Black"
        ])

        (tag, name, value) = c[0]

        self.assertEqual(config.ConfigTag.NAMED_VALUE, tag)
        self.assertEqual("Black", name)
        self.assertEqual("0", value)

    def test_parse_finds_named_value_with_multi_word_name(self):
        c = config.parse([
            "// <5=> 32 bytes"
        ])

        (tag, name, value) = c[0]

        self.assertEqual(config.ConfigTag.NAMED_VALUE, tag)
        self.assertEqual("32 bytes", name)
        self.assertEqual("5", value)


    def test_parse_ignores_blank_lines(self):
        c = config.parse([
            "    "
        ])

        self.assertListEqual(c, [])

    def test_parse_ignores_separator_lines(self):
        c = config.parse([
            "//============"
        ])

        self.assertListEqual(c, [])

    def test_parse_parses_macro_definition(self):
        c = config.parse([
            "#ifndef FOO",
            "#define FOO 1",
            "#endif"
        ])

        (tag, name, value) = c[0]

        self.assertEqual(config.ConfigTag.MACRO_DEFINITION, tag)
        self.assertEqual("FOO", name)
        self.assertEqual("1", value)

    def test_parse_finds_end_of_header_file(self):
        c = config.parse([
            "#endif //SDK_CONFIG.h"
        ])

        self.assertEqual(config.ConfigTag.HEADER_GUARD_END, c[0][0])

    def test_parses_master_sdk_config(self):
        with open("/Users/rconaway/etc/nRF5_SDK/config/nrf52840/config/sdk_config.h") as f:
            text = [line.rstrip() for line in f]
            config.parse(text)


if __name__ == '__main__':
    unittest.main()