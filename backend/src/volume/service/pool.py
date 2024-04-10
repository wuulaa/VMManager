import importlib

from src.utils.jwt import check_user
from src.utils.response import APIResponse
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.volume import db
from src.volume.common import config
from src.volume.db.models import Pool
from src.user.api import UserAPI
from src.user.db.models import User

user_api = UserAPI()

# 加载配置信息
CONF = config.CONF

# 通过配置信息动态加载对应的类
if (CONF['volume']['provider'].lower() == 'rbd'):
    pool_settings = config.RbdSettings()
else:
    pool_settings = config.LibvirtSettings()


pool_driver_path = pool_settings.pool_driver
pool_module_name, pool_driver_name = pool_driver_path.rsplit('.', 1)
pool_module = importlib.import_module(pool_module_name)
pool_driver = getattr(pool_module, pool_driver_name)


@singleton
class PoolService():

    @enginefacade.transactional
    def create_pool(self, session, pool_name: str, allocation: int, owner: str):
        pool = Pool(pool_name, allocation, owner)
        db.insert(session, pool)
        return pool

    @enginefacade.transactional
    def delete_pool_by_uuid(self, session, uuid: str = None):
        pool = db.select_by_uuid(session, Pool, uuid)
        if pool is None:
            raise Exception(f'cannot find a pool which UUID is {uuid}')
        db.delete(session, pool)

    @enginefacade.transactional
    def delete_pool_by_condition(self, session, values: dict):
        pool_list = db.condition_select(session, Pool, values=values)
        if len(pool_list) == 0:
            raise Exception(f'cannot match any pool with {values.__dict__}')
        db.batch_delete(session, pool_list)

    @enginefacade.transactional
    def get_pool_by_uuid(self, session, uuid: str):
        return db.select_by_uuid(session, Pool, uuid)

    @enginefacade.transactional
    def get_pool_by_name(self, session, name: str):
        return db.select_by_name(session, Pool, name)

    @enginefacade.transactional
    def list_pools(self, session, user_name=None):
        if not check_user(user_name, User):
            return []
        if user_name is None:
            pool_list = db.condition_select(session, Pool)
            return pool_list
        else:
            user_uuid = user_api.get_user_uuid_by_name(user_name).get_data()
            pool_list = db.condition_select(session, Pool, values={"owner": user_uuid})
            return pool_list

    
    @enginefacade.transactional
    def get_pool_user_uuid(self, session, uuid):
        return db.select_by_uuid(session, Pool, uuid).owner
    
    @enginefacade.transactional
    def get_pool_by_user_uuid(self, session, user_uuid):
        return db.condition_select(session, Pool, values={"owner": user_uuid}).uuid

    def resize_pool(self, session, uuid: str, new_size: int):
        pool = db.select_by_uuid(session, Pool, uuid)
        if pool.usage <= new_size:
            db.condition_update(session, Pool, uuid,
                                {'allocation': new_size})
        else:
            raise Exception("The new capacity is"
                            "smaller than the used capacity")


# with enginefacade.get_session() as session:
#     service = PoolService()
#     pool1 = service.create_pool(session,
#                                 pool_name="libvirt_pool",
#                                 allocation=20*1024*1024,
#                                 owner="ZYQ")
#     print(pool1.to_dict())

#     libvirt_pool = service.get_pool_by_name(session, "libvirt_pool")
#     print(libvirt_pool.to_dict())


#     pool2 = service.create_pool(session,
#                                 pool_name='pool2',
#                                 allocation=20*1024*1024,
#                                 owner='XXX')
#     selected_pool = service.get_pool_by_uuid(session, pool2.uuid)

#     pool_list = service.list_pools(session)
#     print(f'pool_list have {str(len(pool_list))} pools:')
#     for pool in pool_list:
#         print(pool.to_dict())

#     service.delete_pool_by_condition(session, libvirt_pool.to_dict())

#     service.delete_pool_by_uuid(session, pool2.uuid)

#     print('After delete...')

#     pool_list = service.list_pools(session)
#     print(f'pool_list have {str(len(pool_list))} pools:')
#     for pool in pool_list:
#         print(pool.to_dict())

    # session.commit()
