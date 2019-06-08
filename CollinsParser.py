import base64
import json
import os
import re
import unicodedata
import warnings
from enum import unique, Enum, auto
from functools import wraps, reduce
from operator import add
from pathlib import Path
from pprint import pprint

import bs4
import requests

WEB_ROOT = 'https://www.collinsdictionary.com/dictionary'


@unique
class WebDictSeg(Enum):
    SpanishEnglish = 1
    English = 2


@unique
class TransLang(Enum):
    Swedish = auto()
    Norwegian = auto()
    Spanish = auto()
    British_English = auto()
    Dutch = auto()
    Chinese = auto()
    Finnish = auto()
    Ukrainian = auto()
    Polish = auto()
    Croatian = auto()
    Korean = auto()
    Brazilian_Portuguese = auto()
    Thai = auto()
    Danish = auto()
    European_Spanish = auto()
    Turkish = auto()
    French = auto()
    Italian = auto()
    Japanese = auto()
    Russian = auto()
    Arabic = auto()
    Czech = auto()
    German = auto()
    Romanian = auto()
    Vietnamese = auto()
    Greek = auto()
    American_English = auto()
    European_Portuguese = auto()


# region Decorators


def _decExtract(prop='text', ignore_warnings=False, convert_to_type=None):
    def wrapper(func):
        @wraps(func)
        def _dec(self):
            _ = func(self)
            try:
                if prop == 'text':
                    return getattr(_, prop).strip()
                rslt = _[prop].strip()
                return convert_to_type(rslt) if convert_to_type else rslt
            except:
                if not ignore_warnings:
                    warnings.warn(f'No property for: {prop} of word "{self._word}"')
                return None

        return _dec

    return wrapper


def _decArchive(k, pk=None):
    def wrapper(func):
        @wraps(func)
        def _dec(self):
            if not self._use_archive:
                _ = func(self)
            if not k:
                self.json = func(self)
                _ = self.json
            else:
                val = self.json.get(k if not pk else pk, {})
                if isinstance(val, dict) and not k in self.json:
                    if k in val:
                        _ = val[k]
                    else:
                        _ = func(self)
                        if isinstance(_, bytes):
                            _ = _.decode()
                        val.update({k: _})
                        if pk:
                            self.json.update({pk: val})
                        else:
                            self.json.update(val)
                else:
                    _ = val
            if self._use_archive:
                json.dump(self.json, self._archive_json.open("w"), indent=True, ensure_ascii=False)
            return base64.decodebytes(_.encode()) if k.endswith('_bytes') and _ else _

        return _dec

    return wrapper


# endregion

class _Parser:
    headers = {
        # 'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8",
        "accept - encoding": "gzip, deflate, br",
        "accept - language": "zh - CN, zh;q = 0.9",
        "cache - control": "max - age = 0"
    }

    @property
    def _segDef(self):
        return {
            1: 'spanish-english',
            2: 'english',
        }[self._seg.value]

    @property
    def RqstUrl(self):
        return WEB_ROOT + f"/{self._segDef}/{self._word}"

    def __init__(self, seg, word, bs=None, use_archive=True,
                 archive_dir='_parser_json', download_audio=True, ):
        """

        :type seg: WebDictSeg
        :type word: str
        """
        self._seg = seg
        self._word = word
        self._bs = bs
        self._use_archive = use_archive
        self._download_audio = download_audio
        self.audio_file = None

        self.archive_dir = Path(archive_dir, seg.name, )
        self.archive_dir.mkdir(exist_ok=True, parents=True)

        self._trans_langs_json_file = None
        self._trans_langs = []
        self.json = {}

        if self._use_archive:
            self._archive_json = Path(self.archive_dir, f'{self._word}.json')
            self._trans_langs_json_file = Path(archive_dir, f'trans_langs.json')
            if self._archive_json.is_file():
                self.json = json.load(self._archive_json.open())
            if not self._trans_langs_json_file.is_file():
                json.dump(self._trans_langs, self._trans_langs_json_file.open('w'))
            else:
                self._trans_langs = json.load(self._trans_langs_json_file.open())

        if self._download_audio:
            self.audio_dir = Path(self.archive_dir, 'audio')
            self.audio_dir.mkdir(exist_ok=True, parents=True)

        else:
            self.audio_dir = None

        self.fo = self._find_class_one

    def __getattribute__(self, item):
        _ = super(_Parser, self).__getattribute__(item)
        if isinstance(_, str) and _.endswith('.mp3') and self._download_audio:
            self.audio_file = Path(self.audio_dir, f'{self._word}{os.path.splitext(Path(_).name)[-1]}')
            if not self.audio_file.is_file():
                self._download_media(_, self.audio_file)
        return _

    def set_trans_lang(self, lang):
        self._trans_langs = set(self._trans_langs)
        self._trans_langs.add(lang)
        if self._trans_langs_json_file and self._trans_langs_json_file.is_file():
            json.dump(list(self._trans_langs), self._trans_langs_json_file.open('w'),
                      indent=True, ensure_ascii=False)

    @property
    def bs(self):
        """

        :rtype: bs4.Tag
        """
        if not self._bs:
            print(f"Requesting {self}: {self.RqstUrl}")
            self._bs = bs4.BeautifulSoup(
                requests.get(self.RqstUrl, headers=_Parser.headers, verify=True).text,
                features='lxml').body
        return self._bs

    def _find_class_all(self, cls_, tag_nm=None, bs_obj=None):
        if not bs_obj:
            bs_obj = self.bs
        _ = bs_obj.find_all(tag_nm, attrs={'class': cls_})
        return _

    def _find_class_one(self, cls_, tag_nm=None, bs_obj=None):
        _ = self._find_class_all(cls_, tag_nm, bs_obj)
        if _:
            return _[0]
        return None

    def _download_media(self, url, dest_file):
        '''

        :param url:
        :type dest_file: Path
        :return:
        '''
        dest_file.write_bytes(requests.get(url, stream=True, verify=True).content)

    @property
    @_decArchive('entry_title')
    @_decExtract()
    def PropEntryTitle(self):
        return self._find_class_one('entry_title', 'h1')

    @property
    @_decArchive('orth')
    @_decExtract()
    def PropOrth(self):
        return self._find_class_one('orth', 'span')

    @property
    @_decArchive('translations')
    def PropTranslations(self):
        trans_data = [
            {
                'lang': self.fo('lang', bs_obj=t).text,
                'orth': self.fo('orth', bs_obj=t).text,
            } for t in
            self._find_class_all('translation', bs_obj=self.fo('content-box content-box-translations', 'div'))
        ]
        _ = {}
        for trans_dict in trans_data:
            lang = trans_dict['lang']
            self.set_trans_lang(lang)
            orth = trans_dict['orth']
            _.setdefault(lang, [])
            _[lang].append(orth)
            _[lang] = list(set(_[lang]))
        return _

    @property
    @_decArchive('name', pk='audio')
    def PropAudioFileName(self):
        return self.audio_file.name if self.audio_file else None

    @property
    @_decArchive('content_bytes', pk='audio')
    def PropAudioFileContent(self):
        if self.audio_file and self.audio_file.is_file():
            _ = base64.encodebytes(self.audio_file.read_bytes()).decode()
            return _


class _SpanishEnglishDef(_Parser):
    def __init__(self, word, bs, use_archive, **json):
        super(_SpanishEnglishDef, self).__init__(WebDictSeg.SpanishEnglish, word, use_archive=use_archive)
        self._bs = bs
        self.json = json

    @property
    def bs(self):
        return self._bs

    @property
    @_decArchive('verb_table_url')
    @_decExtract('href', ignore_warnings=True)
    def PropVertableLink(self):
        return self.fo('link-right verbtable', 'a')

    @property
    @_decArchive('pos')
    @_decExtract()
    def PropPos(self):
        return self.fo('pos')

    @property
    @_decArchive('explains')
    def PropExplains(self):
        _ = []
        for senceTag in list(self.bs.children):
            try:
                if 'sense' not in senceTag['class']:
                    continue
            except:
                continue
            assert isinstance(senceTag, bs4.Tag)
            colloc = ''
            syn = ''
            trans = ''
            subject = ''
            geo, register = ['', ] * 2
            grama_grp_tag = self.fo('gramGrp', bs_obj=senceTag)

            if grama_grp_tag:
                colloc_tag = self.fo('colloc', bs_obj=grama_grp_tag)
                if colloc_tag:
                    colloc = colloc_tag.text
            child_tags = [t for t in list(senceTag.children)
                          if isinstance(t, bs4.Tag)]

            _find_tag_txt = lambda cls_nm, tgs=child_tags: unicodedata.normalize("NFKD",
                                                                                 [t for t in tgs
                                                                                  if cls_nm in t['class']][0].text)
            try:
                trans = _find_tag_txt('type-translation')
            except:
                try:
                    trans_list = []
                    for t in child_tags:
                        try:
                            if 'sense' not in t['class']:
                                continue
                            trans_list.append(
                                _find_tag_txt('type-translation', self._find_class_all('type-translation', bs_obj=t)))
                        except:
                            pass
                    else:
                        if not trans_list:
                            for tt in senceTag.recursiveChildGenerator():
                                if not isinstance(tt, bs4.Tag):
                                    continue
                                if 'type-translation' in tt.get('class') \
                                        and 'type-example' not in tt.parent.get('class'):
                                    trans_list.append(tt.text.strip())

                    trans = ', '.join(trans_list)
                except Exception as exc:
                    trans = ''
            try:
                subject = _find_tag_txt('type-subj')
            except:
                pass
            try:
                syn = _find_tag_txt('type-syn')
                syn = re.match("\((.+)\)", syn).group(1).strip()
            except:
                pass

            # region type-geo
            try:
                type_geo = _find_tag_txt('type-geo')
                type_geo_match = re.match('\((.+\w+)\)?\s\((.+\w+)\)?\s\((.+\w+)\)', type_geo)
                if type_geo_match:
                    geo, register, syn = type_geo_match.groups()
            except:
                pass

            if not trans:
                if syn:
                    trans = syn

            # remove [....]
            m = re.match("(\[.+\])\s+(.+)", trans)
            if m:
                ss_, trans = m.groups()

            # 1. (= xxxx) .......
            m = re.match("\(=\s?([(?u)\w\s?]+)\)\s(.+)", trans)
            if m:
                syn, trans = m.groups()

            # endregion

            examples = []
            for emp_tag in self._find_class_all('type-example', bs_obj=senceTag):
                spanish_sentence = self.fo('quote', bs_obj=emp_tag)
                trans_sentence_tag = self.fo('cit type-translation',
                                             bs_obj=emp_tag).find('span', attrs={'class': 'quote'})

                tag_misc = self.fo('lbl type-misc', bs_obj=senceTag)
                if tag_misc:
                    misc = re.match("\((.+)\)", tag_misc.text).group(1)
                else:
                    misc = ''

                examples.append(
                    {
                        'sentence': unicodedata.normalize("NFKD", spanish_sentence.text),
                        'misc': unicodedata.normalize("NFKD", misc),
                        'trans': trans_sentence_tag.text
                    }
                )
            trans = ", ".join(list(set([t.strip() for t in trans.split(",") if t.strip()])))
            # if trans:
            _.append(
                {
                    'colloc': colloc,
                    'geo': geo,
                    'register': register,
                    'syn': syn,
                    'subj': subject,
                    'trans': unicodedata.normalize("NFKD", trans.split("\n")[0].strip()),
                    'examples': examples
                }
            )
        return _

    def to_dict(self):
        return {
            'verb_table_url': self.PropVertableLink,
            'pos': self.PropPos,
            'explains': self.PropExplains,
        }


class SpanishEnglish(_Parser):
    def __init__(self, word: str, use_archive: bool = True, download_audio: bool = True):
        self._suggest_url = f'https://www.collinsdictionary.com/search/?dictCode=spanish-english&q={word}'
        self._request_url = ''
        super(SpanishEnglish, self).__init__(WebDictSeg.SpanishEnglish, word, download_audio=download_audio,
                                             use_archive=use_archive)
        self.get = lambda: self.to_dict
        self.get()

    @property
    def RqstUrl(self):
        if not self._request_url:
            rsp = requests.get(self._suggest_url, verify=True)
            self._request_url = rsp.url
        return self._request_url

    @property
    @_decArchive('url', pk='audio')
    def WordSoundUrl(self):
        try:
            return self.fo("hwd_sound sound audio_play_button icon-volume-up ptr")['data-src-mp3']
        except:
            pass

    @property
    def defs_objs(self):
        return [_SpanishEnglishDef(f"{self._word}_{i}", w, use_archive=False) for i, w in
                enumerate(self.bs.find_all('div', attrs={'class': 'hom'}))]

    @property
    @_decArchive('defs')
    def defs(self):
        return list(map(lambda o: o.to_dict(), self.defs_objs))

    @property
    @_decArchive('title', pk='frequency')
    @_decExtract('title')
    def PropFrequencyTitle(self):
        return self.fo('word-frequency-img', 'span')

    @property
    @_decArchive('score', pk='frequency')
    @_decExtract('data-band', convert_to_type=int)
    def PropFrequencyScore(self):
        return self.fo('word-frequency-img', 'span')

    @property
    @_decArchive('rank', 'frequency')
    def FrequencyRank(self):
        try:
            return int((re.search("(\d+)", self.PropFrequencyTitle).group(1)))
        except:
            pass

    def __getitem__(self, item):
        """

        :param item:
        :rtype: _SpanishEnglishDef
        """
        return _SpanishEnglishDef('', None, **self.to_dict['defs'][item])

    @property
    def joined_english_explains(self):
        return "; ".join([
            re.sub(
                '(,\s){2,}',
                '',
                f"{d['pos'] + ': ' if d['pos'] and all(d['explains']) else d['pos']}{', '.join(d['explains'])}"
            ).strip(', ').replace(": , ", ": ") for i, d in enumerate(self.english_explains)
        ]
        )

    @property
    def english_explains(self):
        _ = [dict(
            explains=[
                re.sub("\s+", " ",
                       re.sub(
                           '\(\s?\)',
                           "",
                           f"{e['colloc']} ({e['geo']})({e['register']}) {e['trans']}"
                       )).strip() for e in
                d['explains']],
            pos=d['pos'],
            syns=[e['syn'] for e in
                  d['explains']]
        ) for d in self.defs]

        return _

    def get_langs_trans(self, lang):
        """

        :param lang: TransLang member or reg pattern string
        :type lang: TransLang or str
        :return:
        """
        if isinstance(lang, str):
            _ = []
            for name, member in TransLang.__members__.items():
                if re.match(lang, name):
                    _.append(member)

        else:
            _ = [lang, ]
        r_data = ", ".join(list(
            set(reduce(add, [self.PropTranslations.get(lg.name.replace("_", " "), []) for lg in _]))
        ))

        if 'english' in ';'.join([l.name.lower() for l in _]) and not r_data:
            r_data = self.joined_english_explains
        return r_data

    @property
    def to_dict(self):
        return {
            'frequency': {
                'title': self.PropFrequencyTitle,
                'rank': self.FrequencyRank,
                'score': self.PropFrequencyScore
            },

            'translations': self.PropTranslations,
            'entry_title': self.PropEntryTitle,
            'orth': self.PropOrth,
            "word": self._word,
            'defs': self.defs,
        }

    @property
    def audio_info(self):
        return {'url': self.WordSoundUrl,
                'name': self.PropAudioFileName,
                # 'content': base64.encodebytes(
                #     self.PropAudioFileContent).decode() if self.PropAudioFileContent else ''
                }


if __name__ == '__main__':
    for w in ['hagan', ]:
        p = SpanishEnglish(w, use_archive=True, download_audio=False)
        pprint(
            p.to_dict['defs'][1]
        )
