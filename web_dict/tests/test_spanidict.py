import json
import unittest

from web_dict.core.factory import SpanishDictDictionary


class VocabularyTest(unittest.TestCase):

    def setUp(self) -> None:
        self.c = SpanishDictDictionary(word='hacer')

    def test_basic(self):
        self.assertIsNotNone(self.c.do_search(), )
        self._p(self.c.do_search())

    def _p(self, c):
        print(json.dumps(c, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
