from functools import wraps
from typing import Optional, List

import oslo_db.exception as DBException
from oslo_db.sqlalchemy import enginefacade
from sqlalchemy.ext.declarative import DeclarativeMeta

from src.volume.common.config import CONF    # 获取配置信息
from src.volume.db.context import DBContext
from src.volume.db.models import Pool, Volume


# 获取事务型 context
main_context_manager = enginefacade.transaction_context()


# ######################### General ###########################

# 暂不使用，之后用来捕获 db 全局异常
def catch_db_exception(func):
    @wraps(func)
    def db_api(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except DBException.DBError as e:
            print('\n***************** DBError',
                  e.inner_exception, '*****************\n')
            return False
        except Exception as e:
            print('\n***************** Exception',
                  e.args[0], '********************\n')
        else:
            return True if res is None else res
    return db_api


@main_context_manager.writer
def batch_insert(context: DBContext, instance_list):
    for instance in instance_list:
        context.session.add(instance=instance)


@main_context_manager.writer
def batch_delete(context: DBContext, instance_list):
    for instance in instance_list:
        context.session.delete(instance=instance)


@main_context_manager.writer
def condition_update(context: DBContext,
                     model: DeclarativeMeta,
                     id: str,
                     values: dict):
    if id is None or len(id.strip()) == 0:
        raise Exception('id is empty')
    pool = context.session.query(model).filter_by(id=id).first()
    if pool:
        pool.update(values)
    else:
        raise Exception(
            f'cannot find id={id} in table \'{model.__tablename__}\'')


@main_context_manager.reader
def condition_select(context: DBContext,
                     model: DeclarativeMeta,
                     values: dict = {}) -> List:
    return context.session.query(model).filter_by(**values).all()


@main_context_manager.writer
def delete(context: DBContext, instance):
    context.session.delete(instance=instance)


@main_context_manager.reader
def select_by_name(context: DBContext, model: DeclarativeMeta, name: str):
    return context.session.query(model).filter_by(name=name).first()


@main_context_manager.reader
def select_by_id(context: DBContext, model: DeclarativeMeta, id: str):
    return context.session.query(model).filter_by(id=id).first()


@main_context_manager.writer
def insert(context: DBContext, instance):
    context.session.add(instance=instance)


@main_context_manager.writer
def soft_delete(context: DBContext, instance):
    return instance.delete(context.session)


# ######################### Dedicated ###########################


@main_context_manager.writer
def condition_update_pool(context: DBContext, id: str, values: dict):
    if id is None:
        raise Exception('id is empty')
    pool = context.session.query(Pool).filter_by(id=id).first()
    if pool:
        for key, value in values.items():
            pool[key] = value
    else:
        raise Exception('cannot find pool')


@main_context_manager.reader
def condition_select_pool(context: DBContext,
                          values: dict) -> List:
    if (values is None):
        raise Exception('dict is None')

    return context.session.query(Pool).filter_by(**values).all()


@main_context_manager.writer
def delete_pool(context: DBContext, pool: Pool):
    context.session.delete(pool)


@main_context_manager.reader
def select_pool_by_id(context: DBContext, id):
    return context.session.query(Pool).filter_by(id=id).first()


@main_context_manager.writer
def insert_pool(context: DBContext, pool: Pool):
    context.session.add(pool)


# ######################### Example ###########################

# import src.Volume.db as db
# from src.Volume.db.context import DBContext
# from src.Volume.db.models import Pool

# # 获取 DB context
# context = DBContext()

# # 创建 entity
# pool = Pool('aaa', 11412, 'ccc')

# db.insert(context, pool)

# '''
# 删除 create_at 这个属性
# python 生成的 datetime 精度较高，精确到毫秒级，
# 而 mysql 默认精确到秒级，过于精确导致查询不到结果
# python - datetime.datetime(2023, 10, 8, 7, 20, 47, 961920)
# mysql - DateTime(2023, 10, 8, 7, 20, 47)
# '''
# del pool.__dict__['created_at']

# pool_list = db.condition_select(context, Pool, pool.to_dict())

# pool_id = pool_list[0].id

# db.condition_update(context,
#                     Pool,
#                     pool_id,
#                     {'name': 'pool_name'})

# pool = db.get_by_id(context, Pool, pool_id)

# db.soft_delete(my_context, pool)

# db.delete(context, pool)
