from flask import Blueprint
from flask import request

from src.utils import consts
from src.utils.response import APIResponse
from src.utils.serializable import JsonSerializable
from src.volume.api import StorageAPI
from src.utils.jwt import jwt_set_user

storage_bp = Blueprint("storage-bp", __name__, url_prefix="/kvm/storage")
storage_api = StorageAPI()


@storage_bp.post("/backup/create")
def create_backup():
    ''' create a backup for a volume '''
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    new_name = request.values.get(consts.P_NEW_NAME)
    return storage_api.clone_volume(volume_uuid, new_name, rt_flag=0)


@storage_bp.post("/backup/delete")
def remove_backup():
    ''' remove a backup from a volume'''
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return storage_api.delete_volume(volume_uuid)


@storage_bp.get("/backup/detail")
def get_backup_info():
    ''' get backup infomation '''
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return storage_api.get_volume(volume_uuid)


@storage_bp.get("/backup/list")
def fetch_backup_list():
    ''' get backup list '''
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return storage_api.fetch_backup_list(parent_uuid=volume_uuid)


@storage_bp.post("/snapshot/create")
def create_snapshot():
    ''' create a snapshot for a volume '''
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    snap_name = request.values.get(consts.P_SNAP_NAME)
    return storage_api.create_snapshot(volume_uuid, snap_name)


@storage_bp.get("/list")
def fetch_disk_list():
    ''' get disk list (of a volume) '''
    guest_uuid = request.values.get(consts.P_GUEST_UUID)
    response: APIResponse = storage_api.get_all_volumes(guest_uuid=guest_uuid)
    list = []
    volume_list = response.get_data()
    for volume in volume_list:
        list.append(JsonSerializable.deserialize(volume.serialize()))
    response.set_data(list)
    return response.to_json_str()


@storage_bp.post("/create")
@jwt_set_user
def create_volume():
    pool_uuid = request.values.get(consts.P_POOL_UUID)
    volume_name = request.values.get(consts.P_VOLUME_NAME)
    size = request.values.get(consts.P_VOLUME_SIZE)
    response = storage_api.create_volume(volume_name, int(size), pool_uuid=pool_uuid)
    response.set_data(JsonSerializable.deserialize(response.get_data().serialize()))
    return response.to_json_str()


@storage_bp.post("/delete")
@jwt_set_user
def delete_volume():
    volmue_uuid = request.values.get(consts.P_VOLUME_UUID)
    return storage_api.delete_volume(volmue_uuid).to_json_str()


@storage_bp.post("/listVolumes")
@jwt_set_user
def get_volumes():
    user_name = request.values.get(consts.P_USER_NAME)
    if user_name:
        return storage_api.list_all_volumes(user_name).to_json_str()
    else:
        return storage_api.list_all_volumes().to_json_str()

    
@storage_bp.post("/listPools")
@jwt_set_user
def get_pools():
    user_name = request.values.get(consts.P_USER_NAME)
    if user_name:
        return storage_api.get_all_pools(user_name).to_json_str()
    else:
        return storage_api.get_all_pools(user_name=None).to_json_str()


@storage_bp.route("/template/add")
def create_template():
   pass


@storage_bp.route("/template/del")
def remove_template():
   pass


@storage_bp.route("/template/detail")
def get_template_detail():
   pass


@storage_bp.route("/template/list")
def fetch_template_list():
   pass


@storage_bp.route("/template/put")
def update_template():
   pass
