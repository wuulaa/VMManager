from __future__ import annotations

import sys
import json

SUCCESS_CODE: int = 0


class APIResponse(object):

    def __init__(self,
                 code: int = SUCCESS_CODE,
                 data: any = None,
                 msg: str = None):
        self.data = data
        self.code = code
        self.msg = msg

    @classmethod
    def success(cls, data: any = None, msg: str = None) -> APIResponse:
        # Display the successfully executed API
        if (msg is None):
            API = sys._getframe(1).f_code.co_name
            msg = f'API \'{API}\' has operated successfully.'
        return cls(code=SUCCESS_CODE, data=data, msg=msg)

    @classmethod
    def error(cls, code: int = None, msg: str = None) -> APIResponse:
        if (code is None):
            raise Exception('error code cannot be None.')
        # Display the failed executed APIs
        if (msg is None):
            API = sys._getframe(1).f_code.co_name
            msg = f'An unexpected error occurred when calling the API \'{API}\'.'
        return cls(code, msg=msg)

    def is_success(self) -> bool:
        return True if (self._code == 0) else False

    def get_code(self) -> int:
        return self.code

    def set_code(self, code: int):
        self.code = code

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_msg(self):
        return self.msg

    def set_msg(self, msg: str = None):
        self.msg = msg

    _code = property(get_code, set_code)
    _data = property(get_data, set_data)
    _msg = property(get_msg, set_msg)

    def to_json_str(self) -> str:
        return json.dumps(self.__dict__, cls=MyEncoder, indent=4)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


# Controller 中使用
def example():
    # 1. 创建空 response，自行补充属性值
    print('------------------------- 创建空 response，自行补充属性值 --------------------------')
    response = APIResponse()
    response.set_msg('Empty APIResponse')
    response.set_code(SUCCESS_CODE)
    print(response.to_json_str())
    print()

    # 2. 创建包含 data 的 response, code 默认为 0
    print('----------------- 创建包含 data 的 response, code 默认为 0 -----------------')
    data_res = APIResponse(
        [1234, 2234, 'aaa', [333333, 2222222, 3333333, 444444]])
    data_res.set_msg('Creating APIResponse with data, code defaults to 0')
    print(data_res.to_json_str())
    print()

    # 3. 创建包含 data 的 successful response
    print('----------------------- 创建包含 data 的 successful response --------------------')
    success_res = APIResponse.success(dict(str='a1',
                                           dict={'bool': True,
                                                 'int': 123,
                                                 'void': None}))
    print(success_res.to_json_str())
    print()

    # 4. 创建包含 msg 的 failed response
    print('---------------------- 创建包含 msg 的 failed response -------------------------')
    error_res = APIResponse.error('invocation: error')
    print(error_res.to_json_str())
    print('----------------------------------------------------------------------------------')


# example()
