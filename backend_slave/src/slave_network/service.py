import libvirt
import time
from src.network_manager.idl import ovs_lib
from src.network_manager.iptables import nat
from src.network_manager import qemu_guest_agent as qa
from src.utils.response import APIResponse
from src.utils import connect

connection = connect.get_libvirt_connection()

ovsdb_helper = ovs_lib.OVSDBHelper()
base_ovs = ovs_lib.BaseOVS(ovsdb_helper.ovsIdl)

def create_bridge(bridge_name: str):
    if base_ovs.bridge_exists(bridge_name):
        return APIResponse.success()
    
    bridge = base_ovs.add_bridge(bridge_name)
    if bridge:
        return APIResponse.success()
    return APIResponse.error(code=400)


def delete_bridge(bridge_name: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    base_ovs.delete_bridge(bridge_name)
    return APIResponse.success()
    

def add_port_to_bridge(bridge_name: str, port_name: str, *interface_attribute_tuples):
    if not base_ovs.bridge_exists(bridge_name):
         return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    bridge.add_port(port_name, *interface_attribute_tuples)
    return APIResponse.success()


def add_vxlan_port_to_bridge(bridge_name: str, port_name: str, remote_ip: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    bridge.add_tunnel_port(port_name, remote_ip)
    return APIResponse.success()


def delete_port_from_bridge(bridge_name: str, port_name: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    if not bridge.port_exists(port_name):
        return APIResponse.error(401)
    bridge.delete_port(port_name)
    return APIResponse.success()


def set_port_tag(bridge_name: str, port_name: str, tag: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    if not bridge.port_exists(port_name):
        return APIResponse.error(401)
    bridge.set_port_tag(port_name, tag)
    return APIResponse.success()


def remove_port_tag(bridge_name: str, port_name: str, tag: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    if not bridge.port_exists(port_name):
        return APIResponse.error(401)
    bridge.remove_port_tag(port_name, tag)
    return APIResponse.success()


def create_ovs_nat_network(network_addr:str, bridge_name: str):
    return nat.create_ovs_nat_network(network_addr, bridge_name)

    
def delete_ovs_nat_network(network_addr: str):
    return nat.delete_ovs_nat_network(network_addr)


def init_iptables():
    # TODO: if modified rules are not saved, add iptable-save here
    return nat.append_drop_to_forward()
    

def create_route(netA: str, netB: str, parent: str):
    return nat.create_route_networks(netA, netB, parent)
    

def delete_route(netA: str, netB: str, parent: str):
    return nat.delete_route_networks(netA, netB, parent)

    
def set_guest_ip_ubuntu(uuid: str,
                        ip_address: str,
                        gateway: str,
                        interface_name: str,
                        dns: str = "114.114.114.114",
                        file_path: str = "/etc/netplan/01-network-manager-all.yaml"):
    """
    set static ip for domain, domain must be running.
    """
    domain: libvirt.virDomain = connection.lookupByUUIDString(uuid)
    res = qa.guest_open_file(domain, file_path, mode="w")
    # print("open", res)
    file_handle = qa.get_file_handle(res)
    network_str = f"""
network:
    ethernets:
        {interface_name}:
            dhcp4: no
            addresses: [{ip_address}]
            optional: true
            gateway4: {gateway}
            nameservers:
                    addresses: [{dns}]
 
    version: 2
"""
    res = qa.guest_write_file(domain, file_handle, network_str)
    # print("write", res)
    res = qa.guest_close_file(domain, file_handle)
    # print("close", res)
    res = qa.guest_exec(domain, "netplan", ["apply"])
    return APIResponse.success()


def