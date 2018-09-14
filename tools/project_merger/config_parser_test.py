import unittest
import config_parser as parser


class config_parser_test(unittest.TestCase):

    def test_reads_the_initial_block_comment(self):
        elt = parser.parse([
            "/**",
            " * a line",
            " */",
        ])[0]

        self.assertEqual(parser.BlockComment([" * a line"]), elt)

    def test_reads_the_header_guard_begin(self):
        elt = parser.parse([
            "#ifndef SDK_CONFIG_H",
            "#define SDK_CONFIG_H",
        ])[0]

        self.assertEqual(parser.HeaderGuardBegin("SDK_CONFIG_H"), elt)

    def test_verifies_that_header_guard_ifndef_and_define_match(self):
        with self.assertRaises(RuntimeError) as context:
            parser.parse([
                "#ifndef SDK_CONFIG_H",
                "#define SDK_CONFIG",
            ])

        self.assertEquals("labels do not match: SDK_CONFIG_H, SDK_CONFIG", str(context.exception))

    def test_finds_beginning_of_configuration_section(self):
        elt = parser.parse([
            "// <<< Use Configuration Wizard in Context Menu >>>"
        ])[0]

        self.assertEquals(parser.ConfigSectionBegin(), elt)

    def test_finds_end_of_configuration_section(self):
        elt = parser.parse([
            "// <<< end of configuration section >>>"
        ])[0]

        self.assertEquals(parser.ConfigSectionEnd(), elt)

    def test_finds_app_config_inclusion(self):
        elt = parser.parse([
            "#ifdef USE_APP_CONFIG",
            '#include "app_config.h"',
            "#endif"
        ])[0]

        self.assertEqual(parser.AppConfig, elt)

    def test_finds_structure_element(self):
        elt = parser.parse([
            "// <h> nRF_Drivers - a comment"
        ])[0]

        self.assertEquals(parser.StructureBegin("h","nRF_Drivers", "- a comment"), elt)

    def test_finds_structure_element_without_comment(self):
        elt = parser.parse([
            "// <h> nRF_Drivers"
        ])[0]

        self.assertEquals(parser.StructureBegin("h","nRF_Drivers", ""), elt)


    def test_finds_all_defined_structure_elements(self):
        c = parser.parse([
            "// <h> nRF_Drivers",
            "// <e> an e",
            "// <o> an o",
            "// <i> an i",
            "// <q> a q",
            "// <s> an s",
        ])
        elts = [elt.tag for elt in c]

        self.assertEqual(["h", "e", "o", "i", "q", "s"], elts)

    def test_finds_all_defined_structure_ends(self):
        (h, e) = parser.parse([
            "// </h>",
            "// </e>"
        ])[0:2]

        self.assertEqual(parser.StructureEnd("h"), h)
        self.assertEqual(parser.StructureEnd("e"), e)

    def test_finds_named_value(self):
        elt = parser.parse([
            "// <0=> Black"
        ])[0]

        self.assertEqual(parser.NamedValue("Black", "0"), elt)

    def test_finds_named_value_with_multi_word_name(self):
        elt = parser.parse([
            "// <5=> 32 bytes"
        ])[0]

        self.assertEqual(parser.NamedValue("32 bytes", "5"), elt)

    def test_ignores_blank_lines(self):
        c = parser.parse([
            "    "
        ])

        self.assertListEqual(c, [])

    def test_ignores_separator_lines(self):
        c = parser.parse([
            "//============"
        ])

        self.assertListEqual(c, [])

    def test_parses_macro_definition(self):
        elt = parser.parse([
            "#ifndef FOO",
            "#define FOO 1",
            "#endif"
        ])[0]

        self.assertEqual(parser.MacroDefinition("FOO", "1"), elt)

    def test_finds_end_of_header_file(self):
        elt = parser.parse([
            "#endif //SDK_CONFIG.h"
        ])[0]

        self.assertEqual(parser.HeaderGuardEnd(), elt)

    def test_parses_master_sdk_config(self):
        with open("sdk_config.h") as f:
            text = [line.rstrip() for line in f]
            parser.parse(text)


if __name__ == '__main__':
    unittest.main()