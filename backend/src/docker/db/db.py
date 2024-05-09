from src.utils.sqlalchemy import enginefacade
from src.docker.db.models import DockerGuest

import src.utils.sqlalchemy.api as db

@enginefacade.auto_session
def create_docker_guest(session, uuid: str, container_id, name: str, user_uuid: str,
                        slave_name: str, vnc_address: str,
                        cpu_shares: int=1024, mem_limit: str = "1024m"):
    status =  "shutoff"
    guest = DockerGuest(uuid, container_id, name, user_uuid, slave_name, status,
                        cpu_shares, mem_limit, vnc_address)
    db.insert(session, guest)
    return guest

@enginefacade.auto_session
def update_guest(session, uuid: str, values: dict):
    return db.condition_update(session, DockerGuest, uuid, values)

@enginefacade.auto_session
def status_update(session, uuid: str, status: str):
    db.condition_update(session, DockerGuest, uuid, values = {"status": status})
    guest: DockerGuest = db.select_by_uuid(session, DockerGuest, uuid)
    return guest

@enginefacade.auto_session
def get_docker_guest_uuid_by_name(session, container_name: str, slave_name: str):
    return db.condition_select(session, DockerGuest, values = {"name": container_name, "slave_name": slave_name})[0].uuid

@enginefacade.auto_session
def get_docker_guest_list(session, user_uuid=None):
    if user_uuid is None:
        return db.condition_select(session, DockerGuest)
    else:
        return db.condition_select(session, DockerGuest, values = {"user_uuid": user_uuid})

@enginefacade.auto_session
def delete_docker_guest_by_uuid(session, uuid: str):
    guest = db.select_by_uuid(session, DockerGuest, uuid)
    return db.delete(session, guest)

@enginefacade.auto_session
def get_docker_guest_slave_name(session, container_uuid: str):
    guest: DockerGuest = db.select_by_uuid(session, DockerGuest, container_uuid)
    return guest.slave_name

@enginefacade.auto_session
def get_docker_guest_status(session, container_uuid: str):
    guest: DockerGuest = db.select_by_uuid(session, DockerGuest, container_uuid)
    return guest.status

@enginefacade.auto_session
def get_docker_guest_by_uuid(session, container_uuid: str):
    guest: DockerGuest = db.select_by_uuid(session, DockerGuest, container_uuid)
    return guest
