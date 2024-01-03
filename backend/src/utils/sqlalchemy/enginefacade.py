import copy
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


_engine = None


def get_engine():
    global _engine
    if (_engine is None):
        _engine = create_engine(
            'mysql+pymysql://vm_manager:kunpeng920@localhost/vm_db', echo=True)
    return _engine


def get_session():
    return Session(get_engine())


def transactional(func):
    ''' 事务管理
    为了保证业务数据的一致性，可以在拥有多个数据库操作的功能上添加事务。

    如果调用者尚未开启事务， 则会创建新的 session 并管理其中的事务
    如果调用者已经开启事务 ，则会自动加入调用者的事务，并由调用者管理事务

    使用该装饰器后，可以确保中的所有数据库操作要么全部提交，要么全部回滚，
    以确保业务数据的正确性。

    param: session: the channel communicate with database
    type: session: sqlalchemy.orm.session.Session
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            _is_new_session = True
            if (len(args) > 1 and isinstance(args[1], Session)):
                _is_new_session = False
                res = func(*args, **kwargs)
                args[1].flush()  # session.flush()
            else:
                session = get_session()
                session.begin()
                res = copy.deepcopy(func(args[0], session, *args[1:], **kwargs))
                session.commit()
            return res
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
        finally:
            if _is_new_session:
                session.close()
    return wrapper


def auto_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            _is_new_session = True
            if (len(args) > 0 and isinstance(args[0], Session)):
                _is_new_session = False
                res = func(*args, **kwargs)
                args[0].flush()  # session.flush()
            else:
                session = get_session()
                session.begin()
                res = copy.deepcopy(func(session, *args, **kwargs))
                session.commit()
            return res
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
        finally:
            if _is_new_session:
                session.close()
    return wrapper
