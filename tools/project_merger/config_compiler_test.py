import unittest
import config_compiler as compiler
import config_parser as parser


def compile(text: str):
    lines = text.splitlines()[1:-1]
    lines = [line[12:] for line in lines]

    parsed = parser.parse(lines)
    return compiler.compile(parsed)

class config_compiler_test(unittest.TestCase):

    def test_compiles_block_comment_and_body(self):
        (comment, body) = compile("""
            /**
             * a test
             */
            #ifndef SDK_CONFIG_H
            #define SDK_CONFIG_H
            // <<< Use Configuration Wizard in Context Menu >>>\n
            #ifdef USE_APP_CONFIG
            #include "app_config.h"
            #endif
            #endif //SDK_CONFIG_H
        """)

        self.assertEqual([" * a test"], comment)
        self.assertEquals(("SDK_CONFIG_H", []), body)

    def xtest_compiles_empty_group_header(self):
        (comment, body) = compile("""
            /**
             * a test
             */
            #ifndef SDK_CONFIG_H
            #define SDK_CONFIG_H
            // <<< Use Configuration Wizard in Context Menu >>>\n
            #ifdef USE_APP_CONFIG
            #include "app_config.h"
            #endif
            // <h> nrf_ble - a test 
            // </h> 
            #endif //SDK_CONFIG_H
        """)

        gh:compiler.GroupHeader = body[0]
        self.assertEqual("nrf_ble", gh.label)
        self.assertEqual("- a test", gh.label)
        self.assertEquals([], gh.content)


