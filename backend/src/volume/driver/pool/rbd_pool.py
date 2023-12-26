from .base_pool import PoolDriver
from src.storage import storage_api as rbd
from src.utils.response import APIResponse


class RbdPool(PoolDriver):

    @staticmethod
    def create(name):
        return APIResponse.success()

    @staticmethod
    def delete(name):
        return APIResponse.success()

    @staticmethod
    def resize(name, size):
        return APIResponse.success()

    @classmethod
    def initialize_connection(cls):
        '''
        return: rados.Ioctx Connection
        '''
        return

    @classmethod
    def terminate_connection(cls):
        return
