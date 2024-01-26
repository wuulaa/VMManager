from typing import Optional
from src.utils.response import APIResponse
from .common.config import CONF
from .service.pool import PoolService
from .service.volume import StorageService

storage_service = StorageService()


class StorageAPI(object):

    def create_pool(self, name: str, allocation: int, user_id: str) -> APIResponse:
        try:
            pool = storage_service.create_pool(name, allocation, user_id)
            return APIResponse.success(pool)
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_pool(self, uuid) -> APIResponse:
        try:
            storage_service.delete_pool_by_uuid(uuid)
            return APIResponse.success(msg='Pool deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_pool(self, uuid) -> APIResponse:
        try:
            pool = storage_service.get_pool_by_uuid(uuid)
            return APIResponse.success(pool)
        except Exception as e:
            return APIResponse.error(400, e)

    def get_all_pools(self) -> APIResponse:
        try:
            pool_list = storage_service.list_pools()
            return APIResponse.success(pool_list)
        except Exception as e:
            return APIResponse.error(400, e)

    def attach_volume_to_guest(self,
                               guest_uuid: str,
                               volume_uuid: str = None,
                               volume_name: str = None,
                               size: int = 20*1024,
                               rt_flag: Optional[int] = 0,
                               *,
                               pool_uuid: str = None) -> APIResponse:
        if pool_uuid is None:
            pool_uuid = CONF['volume']['pool_uuid']
        try:
            volume = storage_service.attach_volume_to_guest(guest_uuid, volume_uuid,
                                                            pool_uuid, volume_name, size)
            response = APIResponse.success('The volume is successfully'
                                           'attached to the client.')
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

    def detach_volume_from_guest(self, volume_uuid: str) -> APIResponse:
        try:
            storage_service.remove_volume_from_guest(volume_uuid)
            return APIResponse.success('The volume has been detached')
        except Exception as e:
            return APIResponse.error(400, e)

    def create_volume(self,
                      volume_name: str,
                      allocation: int = 20*1024,
                      guest_uuid: Optional[str] = None,
                      rt_flag: Optional[int] = 0,
                      *,
                      pool_uuid: str = None) -> APIResponse:
        if pool_uuid is None:
            pool_uuid = CONF['volume']['pool_uuid']
        try:
            volume = storage_service.create_volume(pool_uuid, volume_name,
                                                   allocation, guest_uuid)
            response = APIResponse.success()
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

    def create_volume_from_snap(self,
                                snap_uuid: str,
                                volume_name: str,
                                guest_uuid: Optional[str] = None,
                                rt_flag: Optional[int] = 0) -> APIResponse:
        try:
            response = APIResponse.success()
            volume = storage_service.create_from_snapshot(snap_uuid,
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

    def clone_volume(self,
                     src_volume_uuid: str,
                     dest_volume_name: str,
                     guest_uuid: Optional[str] = None,
                     rt_flag: Optional[int] = 0,
                     *,
                     dest_pool_uuid: str = CONF['volume']['pool_uuid']) -> APIResponse:
        try:
            response = APIResponse.success()
            dest_volume = storage_service.clone_volume(src_volume_uuid,
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

    def delete_volume_by_uuid(self, uuid: str) -> APIResponse:
        try:
            storage_service.delete_volume_by_uuid(uuid)
            return APIResponse.success(msg='Volume deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_volume(self, uuid: str, rt_flag: Optional[int] = 0) -> APIResponse:
        try:
            response = APIResponse.success()
            volume = storage_service.get_volume_by_uuid(uuid)
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

    def get_all_volumes(self, **kwargs) -> APIResponse:
        if 'pool_uuid' not in kwargs or kwargs['pool_uuid'] is None:
            kwargs['pool_uuid'] = CONF['volume']['pool_uuid']

        # 删除空值
        for key in list(kwargs.keys()):
            if not kwargs[key]:
                del kwargs[key]

        try:
            volume_list = storage_service.get_all_volumes(**kwargs)
            return APIResponse.success(volume_list)
        except Exception as e:
            return APIResponse.error(400, e)

    def get_volume_xml(self, volume_uuid: str) -> APIResponse:
        try:
            xml = storage_service.get_volume_xml(volume_uuid)
            return APIResponse.success(xml)
        except Exception as e:
            return APIResponse.error(400, e)

    def fetch_backup_list(self, volume_uuid: str) -> APIResponse:
        try:
            backup_list = storage_service.get_all_volumes(parent_uuid=volume_uuid)
            return APIResponse.success(backup_list)
        except Exception as e:
            return APIResponse.error(400, e)

    def rollback_to_snap(self, volume_uuid: str, snap_uuid: str) -> APIResponse:
        try:
            storage_service.rollback_to_snapshot(volume_uuid, snap_uuid)
            return APIResponse.success('Rollback successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def create_snapshot(self, volume_uuid: str, snap_name: str) -> APIResponse:
        try:
            snapshot = storage_service.create_snapshot(volume_uuid, snap_name)
            return APIResponse.success(snapshot)
        except Exception as e:
            return APIResponse.error(400, e)

    def delete_snapshot_by_uuid(self, uuid: str) -> APIResponse:
        try:
            storage_service.delete_snapshot_by_uuid(uuid)
            return APIResponse.success(msg='Snapshot deleted successfully')
        except Exception as e:
            return APIResponse.error(400, e)

    def get_snaptshot_info(self, snap_uuid: str = None) -> APIResponse:
        try:
            info = storage_service.get_snap_info(snap_uuid)
            return APIResponse.success(data=info)
        except Exception as e:
            return APIResponse.error(400, e)

    def fetch_snapshot_list(self, volume_uuid: str = None) -> APIResponse:
        try:
            snap_list = storage_service.get_snapshots(volume_uuid)
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


# import pdb
# from src.domain_xml.device.disk import DeviceDisk
# from src.volume import db
# from src.volume.db.models import Volume
# from src.utils.sqlalchemy import enginefacade
# from src.utils.serializable import JsonSerializable
# from src.utils.singleton import singleton


# @singleton
# class TestList(JsonSerializable):
#     def __init__(self) -> APIResponse:
#         self.list = []
        
#     def append(self, name: str, age: int) -> APIResponse:
#         self.list.append({'name': name,
#                           'age': age})
    
#     def remove(self, index: int) -> APIResponse:
#         if index >= 0 and index < len(self.list):
#             self.list.remove(index)
        
# class TestClass(JsonSerializable):
#     def __init__(self, list: TestList) -> APIResponse:
#         self.a = 'a'
#         self.num = 3
#         self.bool = True
#         self.list = list
#         self.dict = {'key1': 'value1', 'key2': 'value2'}
        
#     def append(self, name: str, age: int) -> APIResponse:
#         self.list.append({'name': name,
#                           'age': age})
    
#     def remove(self, index: int) -> APIResponse:
#         if index >= 0 and index < len(self.list):
#             self.list.remove(index)
            
#     def __call__(self, *args, **kwargs) -> APIResponse:
#         print('TestClass.__call')

# with enginefacade.get_session() as session:
#     volume: Volume = db.select_by_uuid(session, Volume, '8d214bc2-6228-435e-943c-784efb3668cb')
#     disk: DeviceDisk = volume.get_device()
#     serialize = volume.serialize()
#     print(serialize)
#     deserialize = JsonSerializable.deserialize(serialize)
#     print(deserialize)

#     test_list = TestList()
#     test_list.append(name='ZYQ1', age=23)
#     test_list.append(name='ZYQ2', age=23)
#     test_list.append(name='ZYQ3', age=23)
    
#     test_class = TestClass(test_list)
#     serialize1 = test_class.serialize()
#     print(serialize1)
#     deserialize = JsonSerializable.deserialize(serialize1)

#     pdb.set_trace()

#     # response = APIResponse.success(data=volume)
#     # print(response.to_json_str())