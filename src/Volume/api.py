from .service.pool import PoolService as pool_svc
from .service.volume import VolumeService as vol_svc


class API(object):

    def create_pool(self, name, allocation, owner):
        return pool_svc.create_pool(name, allocation, owner)

    def delete_pool_by_id(self, id):
        return pool_svc.delete_pool_by_id(id)

    def list_all_pool(self):
        return pool_svc.list_all_pool()

    def create_volume(self, pool_id, volume_name, allocation):
        return vol_svc.create_volume(pool_id, volume_name, allocation)

    def delete_volume_by_id(id):
        return vol_svc.delete_volume_by_id()

    def list_all_volume():
        return vol_svc.list_all_volume()
