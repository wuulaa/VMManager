import importlib
import datetime
import numpy as np
from typing import List

from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.volume import db
from src.volume.common import config
from src.volume.db.models import Pool, Volume, Snapshot
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder

CONF = config.CONF

# 通过配置信息动态加载对应的类
if (CONF['volume']['provider'].lower() == 'rbd'):
    volume_settings = config.RbdSettings()
else:
    volume_settings = config.LibvirtSettings()

# 根据配置文件导入对应的 volume driver
volume_driver_path = volume_settings.volume_driver
volume_module_name, volume_driver_name = volume_driver_path.rsplit('.', 1)
volume_module = importlib.import_module(volume_module_name)
volume_driver = getattr(volume_module, volume_driver_name)
# 根据配置文件导入对应的 snapshot driver
snap_driver_path = volume_settings.snap_driver
snap_module_name, snap_driver_name = snap_driver_path.rsplit('.', 1)
snap_module = importlib.import_module(snap_module_name)
snap_driver = getattr(snap_module, snap_driver_name)


@singleton
class StorageService():

    def _get_dev_order(self, session, guest_uuid: str):
        list = db.condition_select(session, Volume, values={
                                   'guest_uuid': guest_uuid})
        length = len(list)
        orders = np.zeros(length, dtype=bool)
        for vol in list:
            if (vol.dev_order < length):
                orders[vol.dev_order] = True
        for index, order in enumerate(orders):
            if (order is False):
                return index
        return length

    def _is_pool_enough_space(self, pool: Pool, allocation: int):
        return True if (allocation < pool.allocation - pool.usage) else False

    @enginefacade.transactional
    def attach_volume_to_guest(self, session,
                               guest_uuid: str,
                               volume_uuid: str,
                               pool_uuid: str,
                               volume_name: str,
                               allocation: int):
        if volume_uuid:
            # attach existed volume
            volume = db.select_by_uuid(session, Volume, volume_uuid)
            if volume is None:
                raise Exception(f'Cannot find a volume '
                                f'which UUID is {volume_uuid}')
            elif volume.guest_uuid is not None:
                raise Exception(f'this volume is used by {volume.guest_uuid}')
        else:
            # attach new volume
            volume = self.create_volume(session, pool_uuid, volume_name, allocation)

        dev_order = self._get_dev_order(session, guest_uuid)
        volume.dev_order = dev_order
        volume.guest_uuid = guest_uuid
        return volume

    @enginefacade.transactional
    def remove_volume_from_guest(self, session, volume_uuid: str):
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {volume_uuid}')
        volume.guest_uuid = None
        volume.dev_order = None

    @enginefacade.transactional
    def create_volume(self,
                      session,
                      pool_uuid: str,
                      volume_name: str,
                      allocation: int,
                      guest_uuid: str = None) -> Volume:
        pool = db.select_by_uuid(session, Pool, pool_uuid)
        if pool is None:
            raise Exception(f'Cannot find a pool which UUID is {pool_uuid}')
        elif not self._is_pool_enough_space(pool, allocation):
            raise Exception(f'Pool {pool.name} is not enough space')

        response = volume_driver.create(volume_name, allocation)

        if response.is_success():
            dev_order = None
            if guest_uuid is not None:
                dev_order = self._get_dev_order(session, guest_uuid)

            volume = Volume(pool_uuid, volume_name, allocation,
                            guest_uuid=guest_uuid,
                            dev_order=dev_order)

            db.insert(session, volume)

            pool.usage += allocation
            return volume
        else:
            raise Exception(f'volume {volume_name} creation failed: '
                            f'{response.get_msg()}')

    @enginefacade.transactional
    def clone_volume(self,
                     session,
                     src_volume_uuid: str,
                     dest_pool_uuid: str = None,
                     dest_volume_name: str = None,
                     guest_uuid: str = None) -> Volume:
        # 1. 验证参数对象是否存在
        src_volume = db.select_by_uuid(session, Volume, src_volume_uuid)
        if dest_pool_uuid is None:
            dest_pool_uuid = src_volume.pool.uuid
        dest_pool = db.select_by_uuid(session, Pool, dest_pool_uuid)

        if src_volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {src_volume_uuid}')
        elif dest_pool is None:
            raise Exception(f'Cannot find a pool '
                            f'which UUID is {dest_pool_uuid}')
        elif not self._is_pool_enough_space(dest_pool, src_volume.allocation):
            raise Exception(f'Pool {dest_pool.name} is not enough space')

        # 2. 创建 snapshot
        snap_name = f'{src_volume.name}_{str(datetime.datetime.now().timestamp())}'

        self.create_snapshot(session, src_volume_uuid, snap_name, is_temp=True)

        # 3. clone volume
        clone_response = volume_driver.clone(src_volume.name,
                                             snap_name,
                                             dest_volume_name)
        if clone_response.is_success():
            dev_order = None
            if guest_uuid is not None:
                dev_order = self._get_dev_order(session, guest_uuid)

            dest_volume = Volume(dest_pool_uuid,
                                 dest_volume_name,
                                 src_volume.allocation,
                                 parent_uuid=src_volume.uuid,
                                 guest_uuid=guest_uuid,
                                 dev_order=dev_order)

            db.insert(session, dest_volume)

            dest_pool.usage += src_volume.allocation
            return dest_volume
        else:
            raise Exception(f'volume {dest_volume_name} clone failed: '
                            f'{clone_response.get_msg()}')

    @enginefacade.transactional
    def create_from_snapshot(self,
                             session,
                             snap_uuid: str,
                             volume_name: str,
                             guest_uuid: str = None) -> Volume:
        snapshot = db.select_by_uuid(session, Snapshot, snap_uuid)
        if snapshot is None:
            raise Exception(f'Cannot find a snapshot '
                            f'which UUID is {snap_uuid}')

        response = volume_driver.clone(src_volume_name=snapshot.volume.name,
                                       snap_name=snapshot.name,
                                       dest_volume_name=volume_name)
        if response.is_success():
            dev_order = None
            if guest_uuid is not None:
                dev_order = self._get_dev_order(session, guest_uuid)

            src_volume = snapshot.volume
            cloned_volume = Volume(src_volume.pool_uuid,
                                   volume_name,
                                   src_volume.allocation,
                                   parent_uuid=src_volume.uuid,
                                   guest_uuid=guest_uuid,
                                   dev_order=dev_order)
            db.insert(session, cloned_volume)
            return cloned_volume
        else:
            raise Exception(f'Volume {volume_name} creation failed: '
                            f'{response.get_msg()}')

    @enginefacade.transactional
    def delete_volume_by_uuid(self, session, volume_uuid: str):
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {volume_uuid}')
        elif volume.guest_uuid is not None:
            raise Exception(f'The Volume is being used by the Guest '
                            f'with UUID {volume.guest_uuid}')

        response = volume_driver.delete(volume.name)
        if response.is_success():
            volume.pool.usage -= volume.allocation
            db.delete_volume_with_snapshots(volume_uuid=volume_uuid)
        else:
            raise Exception(f'volume {volume.name} deletion failed: '
                            f'{response.get_msg()}')

    @enginefacade.transactional
    def delete_volume_by_name(self, session, pool_uuid: str, volume_name: str):
        pool = db.select_by_uuid(session, Pool, pool_uuid)
        if pool is None:
            raise Exception(f'Cannot find a pool which UUID is {pool_uuid}')

        volume = db.select_volumes(session,
                                   pool_uuid=pool_uuid,
                                   name=volume_name)
        if volume is None:
            raise Exception(f'Cannot find a volume named {volume_name} '
                            f'in Pool {pool.name}')

        response = volume_driver.delete(volume.name)
        if response.is_success():
            pool.usage -= volume.allocation
            db.delete_volume_with_snapshots(volume_uuid=volume.uuid)
        else:
            raise Exception(f'volume {volume.name} deletion failed: '
                            f'{response.get_msg()}')

    @enginefacade.transactional
    def get_volume_by_uuid(self, session, uuid: str) -> Volume:
        return db.select_by_uuid(session, Volume, uuid)

    @enginefacade.transactional
    def get_volume_by_name(self, session, pool_uuid: str, name: str) -> Volume:
        volume_list = db.select_volumes(session,
                                        pool_uuid=pool_uuid,
                                        name=name)
        if len(volume_list) > 0:
            return volume_list[0]

    @enginefacade.transactional
    def get_volume_xml(self, session, volume_uuid: str) -> str:
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume.guest_uuid is None:
            raise Exception(f'Volume {volume.name} hasn\'t '
                            f'distribution to any guest')
        disk = RbdVolumeXMLBuilder().construct(volume.name, volume.dev_order)
        return disk.get_xml_string()

    @enginefacade.transactional
    def get_all_volumes(self, session, **kwargs):
        return db.select_volumes(session, **kwargs)

    @enginefacade.transactional
    def fetch_backup_list(self, session, parent_uuid: str) -> List[Volume]:
        return db.select_volumes(session, parent_uuid=parent_uuid)

    @enginefacade.transactional
    def resize_volume(self, session, uuid: str, new_size: int):
        volume = db.select_by_uuid(session, Volume, uuid)
        if volume.usage <= new_size:
            response = volume_driver.resize(volume.name, new_size)
            if response.is_success():
                db.condition_update(session, Pool, uuid, {
                                    'allocation': new_size})
        else:
            raise Exception('The new capacity is smaller '
                            'than the used capacity')

    @enginefacade.transactional
    def rollback_to_snapshot(self, session,
                             volume_uuid: str,
                             snap_uuid: str):
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {volume_uuid}')
        snapshot = db.select_by_uuid(session, Snapshot, snap_uuid)
        if snapshot is None:
            raise Exception(f'Cannot find a snapshot '
                            f'which UUID is {snap_uuid}')

        response = volume_driver.rollback(volume.name, snapshot.name)
        if not response.is_success():
            raise Exception(f'Volume {volume.name} rollback failed')

    @enginefacade.transactional
    def create_snapshot(self,
                        session,
                        volume_uuid: str,
                        snap_name: str,
                        is_temp: bool = False) -> Snapshot:
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {volume_uuid}')

        response = snap_driver.create(volume.name, snap_name)

        if response.is_success():
            snapshot = Snapshot(volume_uuid, snap_name, is_temp=is_temp)
            db.insert(session, snapshot)
            return snapshot
        else:
            raise Exception(f'snapshot {snap_name} creation failed: '
                            f'{response.get_msg()}')

    @enginefacade.transactional
    def delete_snapshot_by_uuid(self, session, snap_uuid: str):
        snapshot = db.select_by_uuid(session, Snapshot, snap_uuid)
        if snapshot is None:
            raise Exception(f'Cannot find a snapshot '
                            f'which UUID is {snap_uuid}')
        response = snap_driver.delete(snapshot.volume.name, snapshot.name)

        if response.is_success():
            db.delete(session, snapshot)
        else:
            raise Exception(f'snapshot {snapshot.name} deletion failed: '
                            f'{response.get_msg()}')

    # @enginefacade.transactional
    # def fetch_volume_snapshots

    @enginefacade.transactional
    def get_snapshots(self, session, volume_uuid: str = None) -> List[Snapshot]:
        volume = db.select_by_uuid(session, Volume, volume_uuid)
        if volume is None:
            raise Exception(f'Cannot find a volume '
                            f'which UUID is {volume_uuid}')
        return volume.snapshots()

    @enginefacade.transactional
    def get_snap_info(self, session, snap_uuid: str):
        snapshot = db.select_by_uuid(session, Snapshot, snap_uuid)
        if snapshot is None:
            raise Exception(f'Cannot find a snapshot '
                            f'which UUID is {snap_uuid}')
        response = snap_driver.get_snap_info(snapshot.volume.name,
                                             snapshot.name)
        if response.is_success():
            return response.get_data()
        else:
            raise Exception(f'Fail to get snapshot {snapshot.name} infomation')

# service = StorageService()

# POOL_UUID = 'd38681d3-07fd-41c7-b457-1667ef9354c7'
# volume_service = VolumeService()
# snap_service = SnapshotService()
# with enginefacade.get_session() as session:
#     volume1 = volume_service.create_volume(session,
#                                            pool_uuid=POOL_UUID,
#                                            volume_name='python-image',
#                                            allocation=20*1024,
#                                            guest_uuid='guest_uuid')
#     select_volume1 = volume_service.get_volume_by_name(
#         session, POOL_UUID, 'python-image')
#     print(select_volume1.to_dict())

#     volume2 = volume_service.create_volume(session,
#                                            POOL_UUID,
#                                            'python-image2',
#                                            20*1024)
#     select_volume2 = volume_service.get_volume_by_uuid(session, volume2.uuid)

#     snap1 = snap_service.create_snapshot(session, volume1.uuid, 'snap1')

#     snap_volume = volume_service.create_from_snap(session,
#                                                   snap_uuid=snap1.uuid,
#                                                   volume_name="snap-image")

#     cloned_volume = volume_service.clone_volume(session,
#                                                 src_volume_uuid=volume2.uuid,
#                                                 dest_pool_uuid=POOL_UUID,
#                                                 dest_volume_name="clone-image")

#     volume_list = volume_service.list_volumes(session)
#     print(f'\n\n\n\nvolume_list have {str(len(volume_list))} volumes\n\n')
#     for volume in volume_list:
#         print(volume.to_dict())

#     import pdb

#     snapshot_list = snap_service.list_snapshots(session)
#     print(f'snapshot_list have {str(len(snapshot_list))} volumes\n\n\n\n')
#     for snapshot in snapshot_list:
#         print(snapshot.to_dict())

#     pdb.set_trace()
#     volume_service.delete_volume_by_name(session,
#                                          cloned_volume.pool_uuid,
#                                          cloned_volume.name)
#     volume_service.delete_volume_by_uuid(session, snap_volume.uuid)

#     snap_service.delete_snapshot_by_uuid(session, snap1.uuid)

#     volume_list = volume_service.list_volumes(session)
#     print(f'\n\n\n\nvolume_list have {str(len(volume_list))} volumes\n\n\n\n')
#     for volume in volume_list:
#         print(volume.to_dict())

#     session.commit()
