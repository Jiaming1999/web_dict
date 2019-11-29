import json
import unittest

from core.prviders.collinsdictionary import CollinsDictionary


class CollinsTest(unittest.TestCase):

    def test_spanish_1(self):
        c = CollinsDictionary('hacer')
        #self._p(c)

    def test_spanish_2(self):
        c = CollinsDictionary('cómo')
        self._p(c)

    def test_english_1(self):
        c = CollinsDictionary('INTRANSITIVE', 'english')
        #self._p(c)

    def _p(self, c):
        print(json.dumps(c.to_dict(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
