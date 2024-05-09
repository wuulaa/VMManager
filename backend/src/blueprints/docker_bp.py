from flask import Blueprint
from flask import request
import requests
from src.utils.jwt import jwt_set_user
from src.utils.response import APIResponse
from src.utils import consts
from src.docker.api import DockerAPI
docker_bp = Blueprint("docker-bp", __name__, url_prefix="/docker")

docker_api = DockerAPI()

@docker_bp.route("/detail", methods=["GET"])
@jwt_set_user
def get_domain_detail():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.docker_guests_detail(container_uuid).to_json_str()

@docker_bp.post("/listGuest")
def unpause_container():
    return docker_api.list_docker_guests().to_json_str()


@docker_bp.post("/createGuest")
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
def delete_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.delete_docker_guest(container_uuid).to_json_str()
   


@docker_bp.post("/startGuest")
def start_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.start_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/stopGuest")
def stop_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.stop_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/restartGuest")
def restart_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.restart_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/pauseGuest")
def pause_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.pause_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/unpauseGuest")
def unpause_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    return docker_api.unpause_docker_guest(container_uuid).to_json_str()


@docker_bp.post("/renameGuest")
def rename_container():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    new_name = request.values.get(consts.P_CONTAINER_NAME)
    res = docker_api.rename_docker_guest(container_uuid, new_name=new_name)
    return res.to_json_str()


@docker_bp.post("/setGuestCPU")
def set_cpu():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    cpu_shares = request.values.get(consts.P_CPU_SHARES)
    res = docker_api.set_docker_guest_cpu_share(container_uuid, cpu_shares=cpu_shares)
    return res.to_json_str()


@docker_bp.post("/setGuestMemory")
def set_mamory():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    mem_limit = request.values.get(consts.P_MEMORY_SIZE)
    res = docker_api.set_docker_guest_memory(container_uuid, memory_limit=mem_limit)
    return res.to_json_str()
    

@docker_bp.post("/attachNic")
def attach_nic():
    container_uuid = request.values.get(consts.P_CONTAINER_UUID)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    res = docker_api.attach_docker_nic(container_uuid, interface_name)
    return res.to_json_str()


@docker_bp.post("/detachNic")
def detach_nic():
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    res = docker_api.detach_docker_nic(interface_name)
    return res.to_json_str()