from flask import Blueprint
import ast
from flask import request
from src.utils import consts
import json
from src.slave_docker.service import docker_service as service
docker_bp = Blueprint("docker-bp", __name__)


@docker_bp.post("/createContainer/")
def create_container():
    image = request.values.get(consts.P_IMAGE)
    cpu_shares = request.values.get(consts.P_CPU_SHARES)
    mem_limit = request.values.get(consts.P_MEMORY_SIZE)
    container_name = request.values.get(consts.P_CONTAINER_NAME)
    network_name = request.values.get(consts.P_NETWORK_NAME)
    ports = request.values.get(consts.P_PORTS)
    if ports:
        ports = ast.literal_eval(ports)
    if cpu_shares:
        cpu_shares = int(cpu_shares)
    res = service.create_container(image=image, name=container_name,
                             cpu_shares=cpu_shares, memory_limit=mem_limit,
                             network=network_name, ports=ports)
    return res.to_json_str()


@docker_bp.post("/deleteContainer/")
def delete_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.remove_container(container_id)
    return res.to_json_str()


@docker_bp.post("/startContainer/")
def start_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.start_container(container_id)
    return res.to_json_str()


@docker_bp.post("/stopContainer/")
def stop_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.stop_container(container_id)
    return res.to_json_str()


@docker_bp.post("/restartContainer/")
def restart_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.restart_container(container_id)
    return res.to_json_str()


@docker_bp.post("/pauseContainer/")
def pause_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.pause_container(container_id)
    return res.to_json_str()


@docker_bp.post("/unpauseContainer/")
def unpause_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.unpause_container(container_id)
    return res.to_json_str()


@docker_bp.post("/updateContainer/")
def update_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    cpu_shares = request.values.get(consts.P_CPU_SHARES)
    mem_limit = request.values.get(consts.P_MEMORY_SIZE)
    new_name = request.values.get(consts.P_CONTAINER_NAME)
    res = service.update_container(container_id, mem_limit=mem_limit, cpu_shares=cpu_shares, new_name=new_name)
    return res.to_json_str()


@docker_bp.post("/monitorContainer/")
def monitor_container():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    res = service.container_status(container_id)
    return res.to_json_str()


@docker_bp.post("/joinSwarm/")
def joinSwarm():
    swarm_worker_token = request.values.get(consts.P_SWARM_WORKER_TOKEN)
    swarm_manager_token = request.values.get(consts.P_SWARM_MANAGER_TOKEN)
    remote_addrs = request.values.get(consts.P_REMOTE_ADDRS)
    advertise_addr = request.values.get(consts.P_ADVERTISE_ADDR)
    listen_addr = request.values.get(consts.P_LISTEN_ADDR)
    
    remote_addrs = remote_addrs.split(",")
    if listen_addr is None:
        listen_addr = "0.0.0.0:2377"
        
    if swarm_manager_token is not None:
        token = swarm_manager_token
    else:
        token = swarm_worker_token
    res = service.join_swarm(remote_addrs, token, advertise_addr, listen_addr)
    return res.to_json_str()


@docker_bp.post("/leaveSwarm/")
def leaveSwarm():
    force = request.values.get(consts.P_FORCE)
    if force is None:
        force = False
    res = service.leave_swarm(force)
    return res.to_json_str()
    

@docker_bp.post("/connectNetwork/")
def connect_network():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    network_name = request.values.get(consts.P_NETWORK_NAME)
    ip_addr = request.values.get(consts.P_IP_ADDRESS)
    res = service.connect_container_to_network(container_id, network_name, ip_addr)
    return res.to_json_str()


@docker_bp.post("/disconnectNetwork/")
def disconnect_network():
    container_id = request.values.get(consts.P_CONTAINER_ID)
    network_name = request.values.get(consts.P_NETWORK_NAME)
    force = request.values.get(consts.P_FORCE)
    res = service.disconnect_container_to_network(container_id, network_name, force)
    return res.to_json_str()