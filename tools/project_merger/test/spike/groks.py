import unittest


class groks(unittest.TestCase):

    def test_read_text_stream(self):
        stream = '''
        This is line one
        This is line two'''

        source = stream.split("\r?\n")

        for line in source:
            print(line)

if __name__ == '__main__':
    unittest.main()