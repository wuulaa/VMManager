from typing import List, Optional, Type

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from . import enginefacade


class Base():
    @enginefacade.auto_session
    def batch_insert(self, session, instance_list: List):
        session.add_all(instance_list)

    @enginefacade.auto_session
    def batch_delete(self, session, instance_list):
        for instance in instance_list:
            session.delete(instance=instance)

    @enginefacade.auto_session
    def condition_update(self,
                         session,
                         model_type: Type[DeclarativeBase],
                         uuid: str,
                         values: dict):
        instance = self.select_by_uuid(session, model_type, uuid)
        if instance is not None:
            for key, value in values.items():
                if (key in instance.get_field_list()):
                    setattr(instance, key, value)
        else:
            raise Exception(
                f'cannot find id={id} in table \'{model_type.__tablename__}\'')

    @enginefacade.auto_session
    def condition_select(self,
                         session,
                         model_type: Type[DeclarativeBase],
                         instance: Optional[DeclarativeBase] = None,
                         values: Optional[dict] = {}) -> List[DeclarativeBase]:
        if instance is not None:
            values = instance.to_dict()
        stmt = select(model_type).filter_by(**values)
        return session.scalars(stmt).all()

    @enginefacade.auto_session
    def delete(self, session, instance: DeclarativeBase):
        session.delete(instance=instance)

    @enginefacade.auto_session
    def insert(self, session, instance: DeclarativeBase):
        session.add(instance=instance)

    @enginefacade.auto_session
    def select_by_id(self, session,
                     model_type: Type[DeclarativeBase],
                     id: int):
        stmt = select(model_type).filter_by(id=id)
        return session.scalar(stmt)

    @enginefacade.auto_session
    def select_by_uuid(self, session,
                       model_type: Type[DeclarativeBase],
                       uuid: str):
        stmt = select(model_type).filter_by(uuid=uuid)
        return session.scalar(stmt)

    @enginefacade.auto_session
    def select_by_name(self, session,
                       model_type: Type[DeclarativeBase],
                       name: str):
        stmt = select(model_type).filter_by(name=name)
        return session.scalar(stmt)


# if __name__ == '__main__':
#     from backend.src.volume.db.models import Pool
#     db = Base()
#     with enginefacade.get_session() as session:
#         pool = Pool('py-test2', 20480, 'Sonya')
#         db.insert(session, pool)

#         query_pool = Pool()
#         query_pool.name = 'py-test2'
#         print(query_pool.to_dict())

#         pool_list1 = db.condition_select(session, Pool, instance=query_pool)
#         print(pool_list1[0].name)

#         pool_list2 = db.condition_select(session, Pool, values=query_pool.to_dict())
#         print(pool_list2[0].name)

#         # 判断两种方法查询出来的数据是否一致
#         print(pool_list1[0] is pool_list2[0])

#         db.condition_update(session,
#                             Pool,
#                             pool.uuid,
#                             {'name': 'new_pool1155',
#                              'allocation': 0,
#                              'owner': 'ZYQ123'})

#         selected_pool = db.select_by_uuid(session, Pool, pool.uuid)
#         print(selected_pool.to_dict())

#         db.delete(session, selected_pool)

#         pool1 = Pool('test1', 1234, 'owner1')
#         pool2 = Pool('test2', 12345, 'owner2')
#         pool3 = Pool('test3', 12346, 'owner3')
#         db.batch_insert(session, [pool1, pool2, pool3])
#         session.commit()
