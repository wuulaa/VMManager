from src.utils.response import APIResponse
from .service.pool import PoolService
from .service.volume import VolumeService, SnapshotService

pool_service = PoolService()
volume_service = VolumeService()
snap_service = SnapshotService()


class PoolAPI(object):

    def create_pool(self, name: str, allocation: int, user_id: str):
        try:
            pool = pool_service.create_pool(name, allocation, user_id)
            return APIResponse.success(pool)
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_pool_by_uuid(self, uuid):
        try:
            pool_service.delete_pool_by_uuid(uuid)
            return APIResponse.success(msg='Pool deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_pool_by_uuid(self, uuid):
        try:
            pool = pool_service.get_pool_by_uuid(uuid)
            return APIResponse.success(pool)
        except Exception as e:
            return APIResponse.error(400, e)

    def get_pool_by_name(self, name):
        try:
            pool = pool_service.get_pool_by_name(name)
            return APIResponse.success(pool)
        except Exception as e:
            return APIResponse.error(400, e)

    def list_pools(self):
        try:
            pool_list = pool_service.list_pools()
            return APIResponse.success(pool_list)
        except Exception as e:
            return APIResponse.error(400, e)


class VolumeAPI(object):

    def add_volume_to_guest(self, volume_uuid: str,
                            guest_uuid: str,
                            return_xml: bool = False):
        try:
            response = APIResponse.success('The volume is successfully'
                                           'added to the client.')
            volume = volume_service.add_volume_to_guest(volume_uuid, guest_uuid)
            if return_xml:
                response.set_data(volume.get_xml_string())
            else:
                response.set_data(volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def remove_volume_from_guest(self, volume_uuid: str):
        try:
            volume_service.remove_volume_from_guest(volume_uuid)
            return APIResponse.success('The volume has been removed')
        except Exception as e:
            return APIResponse.error(400, e)

    def create_volume(self,
                      pool_uuid: str,
                      volume_name: str,
                      allocation: int,
                      guest_uuid: str,
                      return_xml: bool = False):
        try:
            response = APIResponse.success()
            volume = volume_service.create_volume(pool_uuid, volume_name,
                                                  allocation, guest_uuid)
            if return_xml:
                response.set_data(volume.get_xml_string())
            else:
                response.set_data(volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def create_from_snap(self,
                         snap_uuid: str,
                         volume_name: str,
                         return_xml: bool = False):
        try:
            response = APIResponse.success()
            volume = volume_service.create_from_snap(snap_uuid, volume_name)
            if return_xml:
                response.set_data(volume.get_xml_string())
            else:
                response.set_data(volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def clone_volume(self,
                     src_volume_uuid: str,
                     dest_pool_uuid: str,
                     dest_volume_name: str,
                     return_xml: bool = False):
        try:
            response = APIResponse.success()
            dest_volume = volume_service.clone_volume(src_volume_uuid,
                                                      dest_pool_uuid,
                                                      dest_volume_name)
            if return_xml:
                response.set_data(dest_volume.get_xml_string())
            else:
                response.set_data(dest_volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_volume_by_uuid(self, uuid: str):
        try:
            volume_service.delete_volume_by_uuid(uuid)
            return APIResponse.success(msg='Volume deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_volume_by_name(self, pool_uuid: str, volume_name: str):
        try:
            volume_service.delete_volume_by_name(pool_uuid, volume_name)
            return APIResponse.success(msg='Volume deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_volume_by_uuid(self, uuid: str, return_xml: bool = False):
        try:
            response = APIResponse.success()
            volume = volume_service.get_volume_by_uuid(uuid)
            if return_xml:
                response.set_data(volume.get_xml_string())
            else:
                response.set_data(volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def get_volume_by_name(self, pool_uuid: str,
                           volume_name: str,
                           return_xml: bool = False):
        try:
            response = APIResponse.success()
            volume = volume_service.get_volume_by_name(pool_uuid, volume_name)
            if return_xml:
                response.set_data(volume.get_xml_string())
            else:
                response.set_data(volume)
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def list_volumes(self, pool_uuid: str):
        try:
            volume_list = volume_service.list_volumes(pool_uuid)
            return APIResponse.success(volume_list)
        except Exception as e:
            return APIResponse.error(400, e)


class SnapshotAPI(object):

    def create_snapshot(self, volume_uuid: str, snap_name: str):
        try:
            snapshot = snap_service.create_snapshot(volume_uuid, snap_name)
            return APIResponse.success(snapshot)
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_snapshot_by_uuid(self, uuid: str):
        try:
            snap_service.delete_snapshot_by_uuid(uuid)
            return APIResponse.success(msg='Snapshot deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def list_snapshots(self, volume_uuid: str = None):
        try:
            snap_list = snap_service.list_snapshots(volume_uuid)
            return APIResponse.success(snap_list)
        except Exception as e:
            return APIResponse.error(400, e)
