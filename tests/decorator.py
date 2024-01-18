from functools import wraps
import inspect


def NOT_NULL(dict: dict):
    def check(func):
        sig = inspect.signature(func)
        parameters = sig.parameters  #参数列表的有序字典
        @wraps(func)
        def decorator(*args, **kwargs):
            flag =False
            str = ""
            for key in dict:
                if not key in parameters or parameters[key] is None:
                    flag = True
                    str = str + str(key)
            if flag:
                return "These params are None. " + str
            return func(*args, **kwargs)
        return decorator
    return check


# @NOT_NULL({"a"})
def test(a , b, c , d):
    return "aaa"


test(b=2, c=3 ,d=4)