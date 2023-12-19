from __future__ import annotations

import sys
import json


class APIResponse(object):

    def __init__(self, result: any = None,
                 success: bool = True, desc: str = None):
        self.result = result
        self.is_success = success
        self.description = desc

    @classmethod
    def success(cls, result: any = None, desc: str = None) -> APIResponse:
        # Display the successfully executed API
        if (desc is None):
            API = sys._getframe(1).f_code.co_name
            desc = f'API \'{API}\' has operated successfully.'
        return cls(result, desc=desc)

    @classmethod
    def error(cls, result: any = None, desc: str = None) -> APIResponse:
        # Display the failed executed APIs
        if (desc is None):
            API = sys._getframe(1).f_code.co_name
            desc = f'An unexpected error occurred within the API \'{API}\'.'
        return cls(result, success=False, desc=desc)

    def get_description(self):
        return self.description

    def set_description(self, desc: str = None):
        self.description = desc

    _description = property(get_description, set_description)

    def get_success(self):
        return self.is_success

    def set_success(self, success: bool):
        self.is_success = success

    _success = property(get_success, set_success)

    def json(self) -> str:
        return json.dumps(self.__dict__, cls=MyEncoder, indent=4)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


# Controller 中使用
def example():
    # 1. 创建空 Response，自行补充属性值
    print('------------------------- 创建空 Response，自行补充属性值 --------------------------')
    response = APIResponse()
    response.description = 'Empty APIResponse'
    response.set_success(True)
    print(response.json())
    print()

    # 2. 创建包含 result 的 Response，success 默认为 True
    print('----------------- 创建包含 result 的 Response，success 默认为 True -----------------')
    result = APIResponse([1234, 2234, 'aaa', [333333, 2222222, 3333333, 444444]])
    result.description = 'Creating APIResponse with result,' \
                         ' is_success defaults to True'
    print(result.json())
    print()

    # 3. 创建包含 result 的 successful response
    print('----------------------- 创建包含 result 的 successful response --------------------')
    success_res = APIResponse.success(dict(str='a1',
                                           dict={'bool': True,
                                                 'int': 123,
                                                 'void': None}))
    print(success_res.json())
    print()

    # 4. 创建包含 result 的 failed response
    print('---------------------- 创建包含 result 的 failed response -------------------------')
    error_res = APIResponse.error('invocation: error')
    print(error_res.json())
    print('----------------------------------------------------------------------------------')


# example()
