import abc

from ..parser import WebParser


class BaseProvider(WebParser):
    to_dict_fields = ('head_word',)

    def __init__(self, word: str, ):
        super(BaseProvider, self).__init__(word, )

    @property
    @abc.abstractmethod
    def head_word(self):
        ...
