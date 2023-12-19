import importlib
import numpy as np
from src.Utils.singleton import singleton
import src.Volume.db as db
from src.Volume.common import config
from src.Volume.db.models import Pool, Volume
from src.Volume.db.context import DBContext


# 注册配置组和配置项
CONF = config.CONF

# 通过配置信息动态加载 driver
volume_driver_path = CONF[CONF.provider].volume_driver
volume_module_name, volume_driver_name = volume_driver_path.rsplit('.', 1)
volume_module = importlib.import_module(volume_module_name)
volume_driver = getattr(volume_module, volume_driver_name)


@singleton
class VolumeService():

    context = DBContext()

    def create_volume(self, pool_id: str,
                      volume_name: str, allocation: int, vm_uuid: str = None):
        pool = db.select_by_id(self.context, Pool, pool_id)
        if pool is None:
            raise Exception(f'cannot find a pool which UUID={pool_id}')
        response = volume_driver.create(volume_name, allocation)
        if response.is_success is True:
            dev_order = self._get_dev_order(vm_uuid)
            volume = Volume(pool_id, volume_name, allocation, vm_uuid, dev_order)
            db.insert(self.context, volume)
            return volume
        else:
            raise Exception(f'volume {volume_name} create failed')

    def _get_dev_order(self, vm_uuid):
        list = db.condition_select(self.context, Volume, {'vm_id': vm_uuid})
        length = len(list)
        orders = np.zeros(length, dtype=bool)
        for vol in list:
            if (vol.dev_order < length):
                orders[vol.dev_order] = True
        for index, order in enumerate(orders):
            if (order is False):
                return index
        return length

    def delete_volume_by_id(self, pool_id: str, volume_id: str):
        volume = db.select_by_id(self.context, Volume, volume_id)
        if volume is None:
            raise Exception(f'cannot find a volume which id={volume_id}')

        pool = db.select_by_id(self.context, Pool, volume.pool_id)
        response = volume_driver.delete(pool.name, volume.name)
        if response.is_success is True:
            db.delete(volume)

    def delete_volume_by_name(self, pool_id: str, volume_name: str):
        volumes = db.condition_select(self.context, Volume,
                                      {'pool_id': pool_id,
                                       'name': volume_name})
        if len(volumes) == 0:
            raise Exception(f'cannot find a volume named {volume_name}')

        pool = db.select_by_id(self.context, Pool, volumes[0].pool_id)
        response = volume_driver.delete(pool.name, volumes[0].name)
        if response.is_success is True:
            db.delete(self.context, volumes[0])

    def get_volume_by_id(self, id):
        return db.select_by_id(self.context, Volume, id)

    def get_volume_by_name(self, name):
        return db.select_by_name(self.context, Volume, name)

    def list_all_volume(self):
        db.condition_select(self.context, Volume)

    def resize_volume(self, id, new_size):
        volume = db.select_by_id(self.context, Volume, id)
        if volume.usage <= new_size:
            pool = db.select_by_id(self.context, Pool, volume.pool_id)
            response = volume_driver.resize(pool.name,
                                            volume.name,
                                            new_size)
            if response.is_success is True:
                db.condition_update(self.context, Pool, id,
                                    {'allocation': new_size})
        else:
            raise Exception(
                "The new capacity is smaller than the used capacity")
