from domain_manager import guest
from utils import connect


def add_domain(config_xml: str):
    connection = connect.get_libvirt_connection()
    res = guest.create_unpersistent_domain(connection, config_xml)
    return res
