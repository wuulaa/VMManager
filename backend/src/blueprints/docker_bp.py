from flask import Blueprint
from flask import request
import requests
from src.utils.jwt import jwt_set_user
from src.utils.response import APIResponse
from src.utils import consts
from src.docker.api import DockerAPI
docker_bp = Blueprint("docker-bp", __name__, url_prefix="/docker")

docker_api = DockerAPI()

@docker_bp.route("/detail", methods=["POST"])
@jwt_set_user
def get_domain_detail():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.docker_guests_detail(container_uuid).to_json_str()

@docker_bp.post("/listGuest")
@jwt_set_user
def list_container():
    return docker_api.list_docker_guests().to_json_str()


@docker_bp.post("/createGuest")
@jwt_set_user
def create_container():
    guest_name = request.values.get(consts.P_CONTAINER_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    vnc_ipport = request.values.get(consts.P_VNC_IP_PORT)
    vnc_passwd = request.values.get(consts.P_VNC_PASSWD, "123456")
    cpu_shares = request.values.get(consts.P_CPU_SHARES, 1024)
    memory_size = request.values.get(consts.P_MEMORY_SIZE, "1024m")
    return docker_api.create_docker_guest(guest_name, slave_name,
                                          vnc_ipport, vnc_passwd,
                                          cpu_shares, memory_size).to_json_str()
    
    
@docker_bp.post("/deleteGuest")
@jwt_set_user
def delete_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.delete_docker_guest(container_uuid).to_json_str()
   


@docker_bp.post("/startGuest")
@jwt_set_user
def start_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.start_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/stopGuest")
@jwt_set_user
def stop_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.stop_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/restartGuest")
@jwt_set_user
def restart_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.restart_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/pauseGuest")
@jwt_set_user
def pause_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.pause_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/unpauseGuest")
@jwt_set_user
def unpause_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.unpause_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/renameGuest")
@jwt_set_user
def rename_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    new_name = request.values.get(consts.P_CONTAINER_NAME)
    res = docker_api.rename_docker_guest(container_uuid, new_name=new_name)
    return res.to_json_str()


@docker_bp.post("/setGuestCPU")
@jwt_set_user
def set_cpu():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    cpu_shares = request.values.get(consts.P_CPU_SHARES)
    res = docker_api.set_docker_guest_cpu_share(container_uuid, cpu_shares=cpu_shares)
    return res.to_json_str()


@docker_bp.post("/setGuestMemory")
@jwt_set_user
def set_memory():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    mem_limit = request.values.get(consts.P_MEMORY_SIZE)
    res = docker_api.set_docker_guest_memory(container_uuid, memory_limit=mem_limit)
    return res.to_json_str()
    

@docker_bp.post("/attachNic")
@jwt_set_user
def attach_nic():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    res = docker_api.attach_docker_nic(container_uuid, interface_name)
    return res.to_json_str()


@docker_bp.post("/detachNic")
@jwt_set_user
def detach_nic():
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    res = docker_api.detach_docker_nic(interface_name)
    return res.to_json_str()


@docker_bp.route("/getStoredMonitor", methods=["POST"])
def get_stored_monitor_container():
    """
    get stored container monitor status, note that if container was not running
    there would be no data.
    store at most one hour's data in redis
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return docker_api.get_stored_monitor_data(domain_uuid).to_json_str()