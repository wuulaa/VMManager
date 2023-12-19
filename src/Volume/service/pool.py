import importlib
from oslo_config import cfg

from src.Utils.singleton import singleton
import src.Volume.db as db
from src.Volume.common import config
from src.Volume.db.models import Pool
from src.Volume.db.context import DBContext


# 定义配置组
backend_group = cfg.OptGroup(name='backend',
                             title='Backend defaults')
# 定义配置项
backend_opts = [
    cfg.StrOpt('provider', default='rbd',
               help='Specify the backend provider'),
]

# 注册配置组和配置项
CONF = config.CONF
CONF.register_group(backend_group)
CONF.register_opts(backend_opts, group=backend_group)

# 获取所选的后端实现方案
implementation = CONF.backend.implementation

# 定义配置组
backend_impl_group = cfg.OptGroup(name=implementation,
                                  title='Backend Driver Implementation')
# 定义配置项
backend_impl_opts = [
    cfg.StrOpt('pool_driver',
               default='src.Volume.driver.pool.rbd_pool.RbdPool',
               help='Specify the pool driver'),
]
CONF.register_group(backend_impl_group)
CONF.register_opts(backend_impl_opts, group=backend_impl_group)

# 获取实现方案中的 module
pool_impl_module = CONF[implementation].pool_impl_class
# 获取 module 和 class name
pool_module_name, pool_class_name = pool_impl_module.rsplit('.', 1)
# 动态加载实现 module
pool_module = importlib.import_module(pool_module_name)
# 通过反射获取实现类
pool_impl_class = getattr(pool_module, pool_class_name)


@singleton
class PoolService():

    context = DBContext()

    def create_pool(self, name, allocation, owner):
        pool = Pool(name, allocation, owner)
        db.insert(self.context, pool)
        return pool.id

    def delete_pool_by_id(self, id: str = None):
        pool = db.select_by_id(self.context, Pool, id)
        if pool is None:
            raise Exception(f'cannot find a pool which UUID={id}')

        response = pool_impl_class.delete(pool.name)
        if response.is_success is True:
            db.delete(pool)

    def delete_pool_by_condition(self, values: dict):
        pool_list = db.condition_select(self.context, Pool, values)
        if len(pool_list) == 0:
            raise Exception(f'cannot match any pool with {values.__dict__}')

        for pool in pool_list:
            self.delete_pool_by_id(pool.id)

    def get_pool_by_id(self, id):
        return db.select_by_id(self.context, Pool, id)

    def get_pool_by_name(self, name):
        return db.select_by_name(self.context, Pool, name)

    def list_all_pool(self):
        db.condition_select(self.context, Pool)

    def resize_pool(self, id, new_size):
        pool = db.select_by_id(self.context, Pool, id)
        if pool.usage <= new_size:
            db.condition_update(self.context, Pool, id,
                                {'allocation': new_size})
        else:
            raise Exception(
                "The new capacity is smaller than the used capacity")

