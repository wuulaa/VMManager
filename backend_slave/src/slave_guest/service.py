from src.domain_manager import guest
from src.utils import connect

connection = connect.get_libvirt_connection()

def create_domain(config_xml: str):
    res = guest.create_unpersistent_domain(connection, config_xml)
    return str(res.code)


def shutdown_domain(domain_name: str):
    uuid = guest.get_uuid_by_name(connection, domain_name)
    res = guest.shutdown_domain(connection, uuid)
    return str(res.code)


def destroy_domain(domain_name: str):
    uuid = guest.get_uuid_by_name(connection, domain_name)
    res = guest.destroy_domain(connection, uuid)
    return str(res.code)


def start_domain(domain_name: str):
    uuid = guest.get_uuid_by_name(connection, domain_name)
    res = guest.start_domain(connection, uuid)
    return str(res.code)

def get_uuid_by_name(domain_name: str):
    return guest.get_uuid_by_name(connection, domain_name)

def clone_domain(domain_name: str, child_name: str):
    
    return str()