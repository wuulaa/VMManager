import importlib
import numpy as np

from ..common import config
from src.utils.singleton import singleton
import src.volume.db as db
from src.volume.db.models import Pool, Volume
from src.utils.sqlalchemy import enginefacade


CONF = config.CONF

# 通过配置信息动态加载 driver
if (CONF['volume']['provider'].lower() == 'rbd'):
    volume_settings = config.RbdSettings()
else:
    volume_settings = config.LibvirtSettings()
volume_driver_path = volume_settings.volume_driver
volume_module_name, volume_driver_name = volume_driver_path.rsplit('.', 1)
volume_module = importlib.import_module(volume_module_name)
volume_driver = getattr(volume_module, volume_driver_name)


@singleton
class VolumeService():

    @enginefacade.transactional
    def create_volume(self,
                      session,
                      pool_uuid: str,
                      volume_name: str,
                      allocation: int,
                      vm_uuid: str = None):
        pool = db.select_by_uuid(session, Pool, pool_uuid)
        if pool is None:
            raise Exception(f'cannot find a pool which UUID={pool_uuid}')
        elif pool.allocation - pool.usage < allocation:
            raise Exception(f'Pool {pool.name} is not enough storage')
        response = volume_driver.create(volume_name, allocation)
        if response.is_success():
            dev_order = self._get_dev_order(session, vm_uuid)
            volume = Volume(pool_uuid, volume_name,
                            allocation, vm_uuid, dev_order)

            db.insert(session, volume)

            pool.usage += allocation
            return volume
        else:
            raise Exception(f'volume {volume_name} create failed')

    def _get_dev_order(self, session, vm_uuid: str):
        list = db.condition_select(
            session, Volume, values={'vm_uuid': vm_uuid})
        length = len(list)
        orders = np.zeros(length, dtype=bool)
        for vol in list:
            if (vol.dev_order < length):
                orders[vol.dev_order] = True
        for index, order in enumerate(orders):
            if (order is False):
                return index
        return length

    @enginefacade.transactional
    def delete_volume_by_uuid(self, session, volume_uuid: str):
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'cannot find a volume which id={volume_uuid}')

        pool = db.select_by_uuid(session, Pool, volume.pool_uuid)
        response = volume_driver.delete(pool.name, volume.name)
        if response.is_success is True:
            db.delete(session, volume)

    @enginefacade.transactional
    def delete_volume_by_name(self, session, pool_uuid: str, volume_name: str):
        volumes = db.condition_select(session,
                                      Volume,
                                      values={'pool_uuid': pool_uuid,
                                              'name': volume_name})
        if len(volumes) == 0:
            raise Exception(f'cannot find a volume named {volume_name}')

        pool = db.select_by_uuid(session, Pool, volumes[0].pool_uuid)
        response = volume_driver.delete(pool.name, volumes[0].name)
        if response.is_success is True:
            db.delete(volumes[0])

    @enginefacade.transactional
    def get_volume_by_uuid(self, session, uuid):
        return db.select_by_uuid(session, Volume, uuid)

    @enginefacade.transactional
    def get_volume_by_name(self, session, name):
        return db.select_by_name(session, Volume, name)

    def list_all_volume(self, session):
        db.condition_select(session, Volume)

    @enginefacade.transactional
    def resize_volume(self, session, uuid, new_size):
        volume = db.select_by_uuid(session, Volume, uuid)
        if volume.usage <= new_size:
            pool = db.select_by_uuid(session, Pool, volume.pool_uuid)
            response = volume_driver.resize(pool.name,
                                            volume.name,
                                            new_size)
            if response.is_success is True:
                db.condition_update(session, Pool, uuid,
                                    {'allocation': new_size})
        else:
            raise Exception(
                "The new capacity is smaller than the used capacity")


# service = VolumeService()
# service.create_volume('a2d6b10a-8957-4648-8052-8371fb10f4e1',
#                       'py-image7',
#                       20480,
#                       vm_uuid='57a40ef1-1f5b-4555-97b0-835c3c7ceca6')
