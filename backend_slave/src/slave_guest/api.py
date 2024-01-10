from src.domain_manager import guest as guest_manager
from src.utils import connect

connection = connect.get_libvirt_connection()

def create_domain(config_xml: str):
    return guest_manager.create_unpersistent_domain(connection, config_xml)

def shutdown_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.shutdown_domain(connection, uuid)

def destroy_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.destroy_domain(connection, uuid)

def start_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.start_domain(connection, uuid)

def rename_domain(domain_name: str, new_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.rename_domain(connection, uuid, new_name)

def get_uuid_by_name(domain_name: str):
    return guest_manager.get_uuid_by_name(connection, domain_name)

def put_description(domain_name: str, description: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.set_domain_description(connection, uuid, description)

def delete_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.delete_domain(connection, uuid)

def pause_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.pause_domain(connection, uuid)

def resume_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.resume_domain(connection, uuid)

def set_auto_start_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.set_auto_start(connection, uuid)