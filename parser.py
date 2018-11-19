import base64
import json
import os
import re
import unicodedata
import warnings
from enum import unique, Enum
from functools import wraps
from pathlib import Path
from pprint import pprint

import bs4
import requests

WEB_ROOT = 'https://www.collinsdictionary.com/dictionary'


@unique
class WebDictSeg(Enum):
    SpanishEnglish = 1


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
        return {1: 'spanish-english'}[self._seg.value]

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

        if self._use_archive:
            self._archive_json = Path(self.archive_dir, f'{self._word}.json')
            if self._archive_json.is_file():
                self.json = json.load(self._archive_json.open())
            else:
                self.json = {}
        else:
            self.json = {}

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

    @property
    def bs(self):
        """

        :rtype: bs4.Tag
        """
        if not self._bs:
            print(f"Requesting {self}: {self.RqstUrl}")
            self._bs = bs4.BeautifulSoup(
                requests.get(self.RqstUrl, headers=_Parser.headers).text,
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
        dest_file.write_bytes(requests.get(url, stream=True).content)

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
            _ = base64.encodebytes(self.audio_file.read_bytes())
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
            if 'sense' not in senceTag['class']:
                continue
            assert isinstance(senceTag, bs4.Tag)
            colloc = ''
            syn = ''
            subject = ''
            grama_grp_tag = self.fo('gramGrp', bs_obj=senceTag)
            if grama_grp_tag:
                colloc_tag = self.fo('colloc', bs_obj=grama_grp_tag)
                colloc = colloc_tag.text
            cite_trans_tag = self.fo('type-translation', bs_obj=senceTag)
            if cite_trans_tag and 'type-example' not in cite_trans_tag.parent['class']:
                if 'sense' in cite_trans_tag.parent['class']:
                    trans = unicodedata.normalize("NFKD", cite_trans_tag.parent.text)
                    try:
                        subj_tag = [t for t in list(cite_trans_tag.parent.children)
                                    if isinstance(t, bs4.Tag) and 'type-subj' in t['class']][0]
                        subject = re.match("\((.+)\)", subj_tag.text.strip()).group(1)
                    except:
                        pass
                else:
                    trans = unicodedata.normalize("NFKD", cite_trans_tag.text)
                trans = trans.replace('⧫', "/")

                # remove index
                m = re.match("(\d+)\.\s+(.+)", trans)
                explain_index, trans = m.groups() if m else [''] * 2

                # 1. (= xxxx) .......
                m = re.match("\(=\s?(.+)\)\s+(.+)", trans)
                if m:
                    syn, trans = m.groups()

            else:
                trans = ''

            # region type-geo
            tag_type_geo = self.fo('type-geo', bs_obj=senceTag)
            if tag_type_geo:
                type_geo = unicodedata.normalize("NFKD", tag_type_geo.text)
                type_geo_match = re.match('\((.+\w+)\)?\s\((.+\w+)\)?\s\((.+\w+)\)', type_geo)
                if type_geo_match:
                    geo, register, syn = type_geo_match.groups()
                else:
                    geo, register = ['', ] * 2
            else:
                type_geo = ''
                geo, register = ['', ] * 2

            if not trans:
                if syn:
                    trans = syn
                else:
                    trans = type_geo

            # endregion

            tag_misc = self.fo('lbl type-misc', bs_obj=senceTag)
            if tag_misc:
                misc = tag_misc.text
            else:
                misc = ''

            examples = []
            for emp_tag in self._find_class_all('type-example', bs_obj=senceTag):
                spanish_sentence = self.fo('quote', bs_obj=emp_tag)
                trans_sentence_tag = self.fo('cit type-translation',
                                             bs_obj=emp_tag).find('span', attrs={'class': 'quote'})
                examples.append(
                    {
                        'sentence': unicodedata.normalize("NFKD", spanish_sentence.text),
                        'trans': trans_sentence_tag.text
                    }
                )

            _.append(
                {
                    'colloc': colloc,
                    'misc': misc,
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
    def __init__(self, word, ):
        super(SpanishEnglish, self).__init__(WebDictSeg.SpanishEnglish, word, download_audio=True)
        self.get = lambda: self.to_dict
        self.get()

    @property
    @_decArchive('audio', pk='url')
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
            'audio': {'url': self.WordSoundUrl,
                      'name': self.PropAudioFileName,
                      # 'content': self.PropAudioFileContent
                      },
            'defs': self.defs,
        }

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


if __name__ == '__main__':
    for w in ['proyecto']:
        p = SpanishEnglish(w)
        pprint(p.to_dict)
