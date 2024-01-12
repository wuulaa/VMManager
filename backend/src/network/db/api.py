from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.network.db.models import Interface, Network, OVSPort
from src.utils.sqlalchemy.api import *

###############
## interface ##
###############

@enginefacade.auto_session
def create_interface(session,
                    name: str,
                    network_name: str,
                    ip_address: str,
                    mac: str = None,
                    inerface_type: str = "direct"
                   ):
    network_uuid = select_by_name(session, Network, network_name).uuid
    interface = Interface(name, network_uuid, ip_address,
                          mac, inerface_type)
    insert(session, interface)
    return interface 

@enginefacade.auto_session
def delete_interface_by_uuid(session,
                   uuid: str):
    interface = select_by_uuid(session, Interface, uuid)
    delete(session, interface)


@enginefacade.auto_session
def batch_delete_interface(session, interfaces):
    batch_delete(session, interfaces)


@enginefacade.auto_session
def get_interface_by_uuid(session, uuid):
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def get_interface_by_name(session, name):
    return select_by_name(session, Interface, name)


@enginefacade.auto_session
def update_interface_ip(session, uuid, new_ip):
    condition_update(session, Interface, uuid, {"ip_address": new_ip})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_mac(session, uuid, mac):
    condition_update(session, Interface, uuid, {"mac": mac})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_port(session, uuid, port_uuid):
    condition_update(session, Interface, uuid, {"port_uuid": port_uuid})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_status(session, uuid, new_status: str):
    condition_update(session, Interface, uuid, {"status": new_status})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_slave_uuid(session, uuid, slave_uuid: str):
    condition_update(session, Interface, uuid, {"slave_uuid": slave_uuid})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_guest_uuid(session, uuid, guest_uuid: str):
    condition_update(session, Interface, uuid, {"guest_uuid": guest_uuid})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def update_interface_xml(session, uuid, xml: str):
    condition_update(session, Interface, uuid, {"xml": xml})
    return select_by_uuid(session, Interface, uuid)


@enginefacade.auto_session
def get_interface_list(session):
    return condition_select(session, Interface)
    
#############
## network ##
#############

@enginefacade.auto_session
def create_network(session,
                   name: str,
                   ip_address: str):
    network = Network(name, ip_address)
    insert(session, network)
    return network


@enginefacade.auto_session
def delete_network_by_uuid(session,
                    uuid: str):
    network = select_by_uuid(session, Network, uuid)
    delete(session, network)
    
    
@enginefacade.auto_session
def delete_network_by_name(session,
                   name: str):
    network = select_by_name(session, Network, name)
    delete(session, network)


@enginefacade.auto_session
def get_network_by_uuid(session, uuid):
    return select_by_uuid(session, Network, uuid)


@enginefacade.auto_session
def get_network_by_name(session, name):
    return select_by_name(session, Network, name)


@enginefacade.auto_session
def get_network_uuid_by_name(session, name):
    network: Network = select_by_name(session, Network, name)
    return network.uuid


@enginefacade.auto_session
def get_network_list(session):
    return condition_select(session, Network)


@enginefacade.auto_session
def get_network_interface_list(session, network_uuid):
    return condition_select(session, Interface, values={"network_uuid" : network_uuid})


##############
## ovs port ##
##############

@enginefacade.auto_session
def create_port(session,
                name: str,
                interface_uuid: str,
                port_type: str = "internal",
                remote_ip: str= None,
                vlan_tag: str = None
                ):
    port = OVSPort(name, interface_uuid, port_type, remote_ip, vlan_tag)
    insert(session, port)
    return port


@enginefacade.auto_session
def get_port_by_uuid(session,port_uuid: str):
    port = select_by_uuid(session, OVSPort, port_uuid)
    return port


@enginefacade.auto_session
def get_port_by_name(session, port_name: str):
    port = select_by_name(session, OVSPort, port_name)
    return port


@enginefacade.auto_session
def delete_port(session,
                port_uuid: str
                ):
    port = select_by_uuid(session, OVSPort, port_uuid)
    delete(session, port)
    
    
@enginefacade.auto_session
def set_port_tag(session,
                port_uuid: str,
                tag: str
                ):
    condition_update(session, OVSPort, port_uuid, {"vlan_tag": tag})
    port: OVSPort = select_by_uuid(session, OVSPort, port_uuid)
    return port
