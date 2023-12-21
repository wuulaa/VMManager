from __future__ import annotations
import abc
from typing import List
from src.utils.secret import Secret


class SecretXMLBuilder(object, metaclass=abc.ABCMeta):
    _secret: Secret = None

    @property
    def KEY_WORD(self) -> List:
        raise NotImplementedError

    @abc.abstractmethod
    def _build_secret(self, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _build_usage(self, **kwargs):
        raise NotImplementedError

    def _valid_keywords(self, **kwargs):
        for key in self.KEY_WORD:
            if (key not in kwargs):
                raise ValueError(key, 'must be contained when init volume')
            value = kwargs.get(key)
            if (value is None or len(value.strip()) == 0):
                raise ValueError(key, 'cannot be None or empty')

    def construct(self, **kwargs) -> Secret:
        self._valid_keywords(**kwargs)
        self._build_secret(**kwargs)
        self._build_usage(**kwargs)
        return self._secret
