from typing import List, Optional, Type

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from . import enginefacade


@enginefacade.auto_session
def batch_insert(session, instance_list: List):
    session.add_all(instance_list)


@enginefacade.auto_session
def batch_delete(session, instance_list):
    for instance in instance_list:
        session.delete(instance=instance)


@enginefacade.auto_session
def condition_update(session,
                     model_type: Type[DeclarativeBase],
                     uuid: str,
                     values: dict):
    instance = select_by_uuid(session, model_type, uuid)
    if instance is not None:
        for key, value in values.items():
            if (key in instance.get_field_list()):
                setattr(instance, key, value)
    else:
        raise Exception(
            f'cannot find id={id} in table \'{model_type.__tablename__}\'')


@enginefacade.auto_session
def condition_select(session,
                     model_type: Type[DeclarativeBase],
                     instance: Optional[DeclarativeBase] = None,
                     values: Optional[dict] = {}) -> List[DeclarativeBase]:
    if instance is not None:
        values = instance.to_dict()
    stmt = select(model_type).filter_by(**values)
    return session.scalars(stmt).all()


@enginefacade.auto_session
def delete(session, instance: DeclarativeBase):
    session.delete(instance=instance)


@enginefacade.auto_session
def insert(session, instance: DeclarativeBase):
    session.add(instance=instance)


@enginefacade.auto_session
def select_by_id(session,
                 model_type: Type[DeclarativeBase],
                 id: int):
    stmt = select(model_type).filter_by(id=id)
    return session.scalar(stmt)


@enginefacade.auto_session
def select_by_uuid(session,
                   model_type: Type[DeclarativeBase],
                   uuid: str):
    stmt = select(model_type).filter_by(uuid=uuid)
    return session.scalar(stmt)


@enginefacade.auto_session
def select_by_name(session,
                   model_type: Type[DeclarativeBase],
                   name: str):
    stmt = select(model_type).filter_by(name=name)
    return session.scalar(stmt)


# if __name__ == '__main__':
#     from src.volume.db.models import Pool
#     with enginefacade.get_session() as session:
#         pool = Pool('py-test2', 20480, 'Sonya')
#         insert(session, pool)

#         query_pool = Pool()
#         query_pool.name = 'py-test2'
#         print(query_pool.to_dict())

#         pool_list1 = condition_select(session, Pool, instance=query_pool)
#         print(pool_list1[0].name)

#         pool_list2 = condition_select(
#             session, Pool, values=query_pool.to_dict())
#         print(pool_list2[0].name)

#         # 判断两种方法查询出来的数据是否一致
#         print(pool_list1[0] is pool_list2[0])

#         condition_update(session,
#                          Pool,
#                          pool.uuid,
#                          {'name': 'new_pool1155',
#                              'allocation': 0,
#                              'owner': 'ZYQ123'})

#         selected_pool = select_by_uuid(session, Pool, pool.uuid)
#         print(selected_pool.to_dict())

#         delete(session, selected_pool)

#         pool1 = Pool('test11', 1234, 'owner11')
#         pool2 = Pool('test21', 12345, 'owner21')
#         pool3 = Pool('test31', 123456, 'owner31')
#         batch_insert(session, [pool1, pool2, pool3])
#         session.commit()
