from .base_volume import VolumeDriver
from src.Storage import storage_api as rbd
from src.Utils.response import APIResponse
from src.Volume.common import config


CONF = config.CONF
POOL_NAME = CONF.rbd.pool_name


class RbdVolume(VolumeDriver):
    @staticmethod
    def clone(src_pool, src_volume, dest_pool, dest_name):
        return APIResponse.success()

    @staticmethod
    def close_volume(volume_name):
        return APIResponse.success()

    @staticmethod
    def create(volume_name, allocation):
        return rbd.create_rbd(POOL_NAME,
                              volume_name,
                              allocation*1024*1024)     # MB to B

    @staticmethod
    def delete(volume_name):
        return rbd.delete_rbd(POOL_NAME, volume_name)

    @staticmethod
    def get_volume_info(volume_name):
        return APIResponse.success()

    @staticmethod
    def rename(volume_name, new_name):
        return APIResponse.success()

    @staticmethod
    def resize(volume_name, new_size):
        return APIResponse.success()
