import pdb
import inspect
import json
from typing import List


class JsonSerializable:

    @staticmethod
    def is_normal_prop(obj, key):
        is_prop = isinstance(getattr(type(obj), key, None), property)
        is_func_attr = callable(getattr(obj, key))
        is_private_attr = key.startswith('__')
        return not (is_prop or is_func_attr or is_private_attr)

    @staticmethod
    def is_basic_type(value):
        return value is None or type(value) in [int, float, str, bool, list, dict]

    def _serialize_prop(self, name):
        return getattr(self, name)

    def _as_dict(self, keys: list = None):
        ''' Recursive serialization

        '''
        props = {}
        if keys is None:
            keys = self.__dict__
        for key in keys:
            if not self.is_normal_prop(self, key):
                continue
            value = self._serialize_prop(key)
            if not (self.is_basic_type(value) or isinstance(value, JsonSerializable)):
                raise Exception(f'Object of type {type(key)} is not JSON '
                                f'serializable: {key=}, {value=}')
            props[key] = value if self.is_basic_type(value) else value._as_dict()
        return props

    def serialize(self):
        return json.dumps(self._as_dict())

    def _deserialize_prop(self, name, deserialized):
        setattr(self, name, deserialized)

    @staticmethod
    def deserialize(json_encoded):
        if json_encoded is None:
            return None

        dict = json.loads(json_encoded) if type(
            json_encoded) is str else json_encoded
        return dict
