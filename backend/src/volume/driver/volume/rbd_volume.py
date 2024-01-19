from .base_volume import VolumeDriver, SnapshotDriver
from src.storage import storage_api as rbd
from src.utils.response import APIResponse
from src.volume.common import config


CONF = config.CONF
POOL_NAME = CONF['volume']['pool_name']


class RbdVolume(VolumeDriver):
    @staticmethod
    def clone(src_volume_name: str,
              snap_name: str,
              dest_volume_name: str):
        return rbd.clone(POOL_NAME, src_volume_name, snap_name,
                         POOL_NAME, dest_volume_name)

    @staticmethod
    def create(volume_name: str, allocation: int):
        return rbd.create_rbd(POOL_NAME,
                              volume_name,
                              allocation*1024*1024)     # MB to B

    @staticmethod
    def delete(volume_name: str):
        return rbd.delete_rbd(POOL_NAME, volume_name)

    @staticmethod
    def get_volume_info(volume_name: str):
        return APIResponse.success()

    @staticmethod
    def rename(volume_name: str, new_name: str):
        return APIResponse.success()

    @staticmethod
    def resize(volume_name: str, new_size: int):
        return APIResponse.success()


class RbdSnapshot(SnapshotDriver):
    @staticmethod
    def create(volume_name: str, snap_name: str):
        return rbd.create_snap(POOL_NAME, volume_name, snap_name)

    @staticmethod
    def delete(volume_name: str, snap_name: str):
        return rbd.delete_snap(POOL_NAME, volume_name, snap_name)
