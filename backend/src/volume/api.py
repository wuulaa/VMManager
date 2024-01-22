from typing import Optional
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

    def add_disk_to_guest(self,
                          volume_uuid: str,
                          guest_uuid: str,
                          rt_flag: Optional[int] = 0):
        try:
            response = APIResponse.success('The disk is successfully'
                                           'added to the client.')
            volume = volume_service.add_volume_to_guest(volume_uuid, guest_uuid)
            if rt_flag == 0:
                response.set_data(volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': volume.uuid,
                        'disk': volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(volume.get_xml_string())
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def remove_disk_from_guest(self, volume_uuid: str):
        try:
            volume_service.remove_volume_from_guest(volume_uuid)
            return APIResponse.success('The volume has been removed')
        except Exception as e:
            return APIResponse.error(400, e)

    def create_disk(self,
                    pool_uuid: str,
                    volume_name: str,
                    allocation: int,
                    guest_uuid: Optional[str] = None,
                    rt_flag: Optional[int] = 0):
        try:
            import pdb
            pdb.set_trace()
            response = APIResponse.success()
            volume = volume_service.create_volume(pool_uuid, volume_name,
                                                  allocation, guest_uuid)
            if rt_flag == 0:
                response.set_data(volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': volume.uuid,
                        'disk': volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(volume.get_xml_string())
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def create_disk_from_snap(self,
                              snap_uuid: str,
                              volume_name: str,
                              guest_uuid: Optional[str] = None,
                              rt_flag: Optional[int] = 0):
        try:
            response = APIResponse.success()
            volume = volume_service.create_from_snap(snap_uuid,
                                                     volume_name,
                                                     guest_uuid=guest_uuid)
            if rt_flag == 0:
                response.set_data(volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': volume.uuid,
                        'disk': volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(volume.get_xml_string())
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def clone_disk(self,
                   src_volume_uuid: str,
                   dest_pool_uuid: str,
                   dest_volume_name: str,
                   guest_uuid: Optional[str] = None,
                   rt_flag: Optional[int] = 0):
        try:
            response = APIResponse.success()
            dest_volume = volume_service.clone_volume(src_volume_uuid,
                                                      dest_pool_uuid,
                                                      dest_volume_name,
                                                      guest_uuid=guest_uuid)
            if rt_flag == 0:
                response.set_data(dest_volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': dest_volume.uuid,
                        'disk': dest_volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(dest_volume.get_xml_string())
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_disk_by_uuid(self, uuid: str):
        try:
            volume_service.delete_volume_by_uuid(uuid)
            return APIResponse.success(msg='Volume deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_disk_by_name(self, pool_uuid: str, volume_name: str):
        try:
            volume_service.delete_volume_by_name(pool_uuid, volume_name)
            return APIResponse.success(msg='Volume deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_disk_by_uuid(self, uuid: str, rt_flag: Optional[int] = 0):
        try:
            response = APIResponse.success()
            volume = volume_service.get_volume_by_uuid(uuid)
            if rt_flag == 0:
                response.set_data(volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': volume.uuid,
                        'disk': volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(volume.get_xml_string())
            return response
        except Exception as e:
            return APIResponse.error(400, e)

    def get_disk_by_name(self,
                         pool_uuid: str,
                         volume_name: str,
                         rt_flag: Optional[int] = 0):
        try:
            response = APIResponse.success()
            volume = volume_service.get_volume_by_name(pool_uuid, volume_name)
            if rt_flag == 0:
                response.set_data(volume)
            elif rt_flag == 1:
                # disk
                data = {'volume_uuid': volume.uuid,
                        'disk': volume.get_device()}
                response.set_data(data)
            elif rt_flag == 2:
                response.set_data(volume.get_xml_string())
        except Exception as e:
            return APIResponse.error(400, e)

    def get_disk_xml(self, volume_uuid: str):
        try:
            xml = volume_service.get_volume_xml(volume_uuid)
            return APIResponse.success(xml)
        except Exception as e:
            return APIResponse.error(400, e)

    def list_volumes(self, pool_uuid: str):
        try:
            volume_list = volume_service.list_volumes(pool_uuid)
            return APIResponse.success(volume_list)
        except Exception as e:
            return APIResponse.error(400, e)

    def rollback_to_snap(self, volume_uuid: str, snap_uuid: str):
        try:
            volume_service.rollback_to_snap(volume_uuid, snap_uuid)
            return APIResponse.success('Rollback successfully')
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

    def get_snaptshot_info(self, snap_uuid: str = None):
        try:
            info = snap_service.get_snap_info(snap_uuid)
            return APIResponse.success(data=info)
        except Exception as e:
            return APIResponse.error(400, e)

    def list_snapshots(self, volume_uuid: str = None):
        try:
            snap_list = snap_service.list_snapshots(volume_uuid)
            return APIResponse.success(snap_list)
        except Exception as e:
            return APIResponse.error(400, e)


# POOL_UUID = 'd38681d3-07fd-41c7-b457-1667ef9354c7'
# volume_api = VolumeAPI()
# res = volume_api.rollback_to_snap(
#     volume_uuid='8388ad7f-e58b-4d94-bf41-6e95b23d0d4a',
#     snap_uuid='b59344fd-6051-43ea-9249-9d7910bf9fb6'
# )
# print(res.is_success())
# print(res.get_msg())

# print(res.is_success())
# data = res.get_data()
# print(str(res.data))
# print(res.data['volume_uuid'])
# print(res.data['disk'])
# print(res.get_msg())
# response = volume_api.clone_disk(src_volume_uuid='8388ad7f-e58b-4d94-bf41-6e95b23d0d4a',
#                                  dest_pool_uuid=POOL_UUID,
#                                  dest_volume_name='test',
#                                  rt_flag=False)
# print(response.is_success())
# print(response.get_data())
# print(response.get_msg())
