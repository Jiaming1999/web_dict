import re

from property_cached import cached_property

from .base_provider import BaseProvider
from ..parser import Parser


class _PhraseProvider(Parser):
    to_dict_fields = (
        'phrase',
        'trans',
    )

    @property
    def phrase(self):
        return self.select("span.type-phr > span.orth")

    @property
    def trans(self):
        return self.select("span.cit.type-translation > span.quote")


class _IdiomProvider(Parser):
    to_dict_fields = (
        'orth',
        'trans'
    )

    @property
    def orth(self):
        return self.select('span.orth')

    @property
    def trans(self):
        return self.select("span.cit.type-translation > span")


class _GrammarProvider(Parser):
    to_dict_fields = {
        'content',
        'trans',
    }

    @property
    def content(self):
        content = self.select("span.colloc")
        if content:
            return re.match(r"\[(?P<c>.+)\]", content).group("c")
        return content

    @property
    def trans(self):
        return self.select('span.cit.type-translation')


class _ExampleProvider(Parser):
    to_dict_fields = {
        'sent', 'trans'
    }

    @property
    def sent(self):
        return re.sub(r'\s+', ' ', self.select('span.quote', one=False)[0]).strip()

    @property
    def trans(self):
        try:
            return re.sub(r'\s+', ' ', "; ".join(self.select('span.quote', one=False)[1:])).strip()
        except IndexError:
            return None


class _SenseProvider(Parser):
    to_dict_fields = (
        'exp',
        'examples',
        'syn',
        'grammars',
        'idioms',
        'phrases'
        'senses'
    )

    @property
    def syn(self):
        syn_pattern = re.compile(r"\)?\s*\(=?\s*(?P<c>.+)\)")
        t1 = self.select('span.lbl.type-geo > span.lbl.type-syn', text=False)
        if t1:
            syn = re.match(syn_pattern, t1.text).group("c")
            geo_txt = self.select('span.lbl.type-geo')

            return {
                'syn': syn,
                'geo': re.match(r"\((?P<g>.+)\)\s*\(.+\)", geo_txt).group("g")
            }
        try:
            syn = re.match(syn_pattern, self.select('span.lbl.type-syn')).group("c")
        except:
            syn = ''
        return {'syn': syn, 'geo': None}

    @property
    def exp(self):
        exp = "; ".join(t.text for t in
                        self.bs.find_all('span', class_='cit type-translation', recursive=False, ))

        if not exp:
            exp = self.select("div.def")
        return exp

    @property
    def idioms(self):
        return self.provider_to_list(
            _IdiomProvider, 'div.re.type-idm'
        )

    @property
    def examples(self):
        return self.provider_to_list(_ExampleProvider, "div.cit.type-example")

    @property
    def phrases(self):
        return self.provider_to_list(_PhraseProvider, 'div.type-phr')

    # @property
    # def grammars(self):
    #     return self.provider_to_list(_GrammarProvider, "div.sense")

    def val_senses(self):
        return self.provider_to_list(_SenseProvider, 'div.sense')


class _DefProvider(Parser):
    to_dict_fields = (
        "pos",
        'senses',
        'misc'
    )

    def __init__(self, markup: str):
        super(_DefProvider, self).__init__(markup=markup)

    @property
    def pos(self):
        return self.select('span.pos')

    @property
    def misc(self):
        misc = self.select('span.lbl.type-misc')
        return re.match(r"\((?P<c>.+)\)", misc).group('c') if misc else misc

    @property
    def senses(self):
        return [s for s in self.provider_to_list(_SenseProvider,
                                                 ('div', dict(class_='sense', recursive=False)))
                if any(s.values())]


class CollinsDictionary(BaseProvider):
    to_dict_fields = (
        'head_word',
        'pron',
        'rank',
        'audio',
        'defs'
    )

    @property
    def url(self):
        return f"https://www.collinsdictionary.com/dictionary/{self.seg}/{self.word}"

    def __init__(self, word: str, seg: str = 'spanish-english'):
        super(CollinsDictionary, self).__init__(word)
        self.seg = seg

    @cached_property
    def bs(self):
        bs = super(BaseProvider, self).bs
        return bs.find('div', class_=re.compile(r'cB\scB-def.+'))

    @property
    def pron(self):
        return self.select('span.pron.type-')

    @property
    def rank(self):
        try:
            return int(self.select('span.word-frequency-img', one=True, text=False)['data-band'])
        except Exception as exc:
            return None

    @property
    def head_word(self):
        try:
            return self.select("span.orth")
        except AttributeError:
            return None

    @property
    def audio(self):
        return self.select("a.audio_play_button", text=False)['data-src-mp3']

    @property
    def defs(self):
        return [s for s in self.provider_to_list(_DefProvider, "div.hom")
                if any(s.values())]
