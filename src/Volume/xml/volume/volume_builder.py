from __future__ import annotations
import abc
from typing import List

from src.DomainXML.Device.disk import DeviceDisk


class VolumeXMLBuilder(object, metaclass=abc.ABCMeta):
    _disk: DeviceDisk = None

    @property
    def KEY_WORD(self) -> List:
        raise NotImplementedError

    @abc.abstractmethod
    def _build_auth(self, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def _build_disk(self, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def _build_source(self, **kwargs):
        raise NotImplementedError()

    def _valid_keywords(self, **kwargs):
        for key in self.KEY_WORD:
            if (key not in kwargs):
                raise ValueError(key, 'must be contained when init volume')
            value = kwargs.get(key)
            if (value is None or
                    isinstance(value, str) and len(value.strip()) == 0):
                raise ValueError(key, 'cannot be None or empty')

    def construct(self, **kwargs) -> DeviceDisk:
        self._valid_keywords(**kwargs)
        self._build_disk(**kwargs)
        self._build_auth(**kwargs)
        self._build_source(**kwargs)
        return self._disk
