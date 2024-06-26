import libvirt
import time
import yaml
from src.network_manager.idl import ovs_lib
from src.network_manager.iptables import nat
from src.network_manager import qemu_guest_agent as qa
from src.utils.response import APIResponse
from src.utils import connect
from src.network_manager import ip as iptools

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


def add_gre_port_to_bridge(bridge_name: str, port_name: str, remote_ip: str):
    if not base_ovs.bridge_exists(bridge_name):
        return APIResponse.error(401)
    
    bridge = ovs_lib.OVSBridge(bridge_name, ovsdb_helper.ovsIdl)
    bridge.add_tunnel_port(port_name, remote_ip, tunnel_type="gre")
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
    

def uninit_iptables():
    return nat.delete_drop_from_forward()


def create_route(netA: str, netB: str, parent: str):
    return nat.create_route_networks(netA, netB, parent)
    

def delete_route(netA: str, netB: str, parent: str):
    return nat.delete_route_networks(netA, netB, parent)


def init_set_guest_ips_ubuntu(uuid: str,
                        ip_addresses: list,
                        gateways: list,
                        interface_names: list,
                        dns: str = "8.8.8.8",
                        file_path: str = "/etc/netplan/00-installer-config.yaml"):
    """
    clear file and add all static ips provided.
    This function should be called as the init function to handle all static ips.
    """
    domain: libvirt.virDomain = connection.lookupByUUIDString(uuid)
    yaml_data = {}
    yaml_data["network"] = {}
    yaml_data["network"]["version"] = 2
    
    if len(interface_names) != 0:
        yaml_data["network"]["ethernets"] = {}
        for interface_name, ip_address, gateway in zip(interface_names, ip_addresses, gateways):
            interface_data = {
                'dhcp4': 'no',
                'addresses': [ip_address],
                'optional': "true",
                'gateway4': gateway,
                'nameservers': {
                    'addresses': [dns]
                    }
                }
            yaml_data["network"]["ethernets"][interface_name] = interface_data
            

    # open in write mode, old content would be cleared
    res = qa.guest_open_file(domain, file_path, mode="w")
    file_handle = qa.get_file_handle(res)
    modified_content = yaml.dump(yaml_data, default_flow_style=False)
    # write  modified content
    res = qa.guest_write_file(domain, file_handle, modified_content)
    # close file and apply
    res = qa.guest_close_file(domain, file_handle)
    res = qa.guest_exec(domain, "netplan", ["apply"])
    return APIResponse.success()


    
def set_guest_ip_ubuntu(uuid: str,
                        ip_address: str,
                        gateway: str,
                        interface_name: str,
                        dns: str = "8.8.8.8",
                        file_path: str = "/etc/netplan/00-installer-config.yaml"):
    """
    set static ip for domain, domain must be running.
    """
    domain: libvirt.virDomain = connection.lookupByUUIDString(uuid)
    res = qa.guest_open_file(domain, file_path, mode="r")
    file_handle = qa.get_file_handle(res)
    read_content = qa.guest_read_file(domain, file_handle)
    content = qa.decode_file_read_res(read_content)
    yaml_data = yaml.safe_load(content)
    if "network" in yaml_data:
        if not "ethernets" in yaml_data["network"]:
            yaml_data["network"]["ethernets"] = {}
        
        interface_data = {
            'dhcp4': 'no',
            'addresses': [ip_address],
            'optional': "true",
            'gateway4': gateway,
            'nameservers': {
                'addresses': [dns]
                }
            }
        yaml_data["network"]["ethernets"][interface_name] = interface_data
            
    # close file
    res = qa.guest_close_file(domain, file_handle)
    
    
    # open in write mode
    res = qa.guest_open_file(domain, file_path, mode="w")
    file_handle = qa.get_file_handle(res)
    modified_content = yaml.dump(yaml_data, default_flow_style=False)
    # write back modified content
    res = qa.guest_write_file(domain, file_handle, modified_content)
    # close file and apply
    res = qa.guest_close_file(domain, file_handle)
    res = qa.guest_exec(domain, "netplan", ["apply"])
    return APIResponse.success()


def remove_guest_ip_ubuntu(uuid: str, interface_name: str = None, file_path: str = "/etc/netplan/00-installer-config.yaml"):
    """
    remove static ip for domain, domain must be running.
    if no interface name is provided, remove all
    otherwise remove the given interface only
    """
    domain: libvirt.virDomain = connection.lookupByUUIDString(uuid)
    if interface_name is None:
        # remove all interface configs if no name is provided
        res = qa.guest_open_file(domain, file_path, mode="w")
        file_handle = qa.get_file_handle(res)
        network_str = f"""
network:
  version:2
        """
        res = qa.guest_write_file(domain, file_handle, network_str)
        res = qa.guest_close_file(domain, file_handle)
        res = qa.guest_exec(domain, "netplan", ["apply"])
        return APIResponse.success()
    
    # open in read mode
    res = qa.guest_open_file(domain, file_path, mode="r")
    file_handle = qa.get_file_handle(res)
    read_content = qa.guest_read_file(domain, file_handle)
    content = qa.decode_file_read_res(read_content)
    yaml_data = yaml.safe_load(content)
    if ("network" in yaml_data and "ethernets" in yaml_data["network"]
        and interface_name in yaml_data["network"]["ethernets"]):
        # read content and delete the specific interface
        del yaml_data["network"]["ethernets"][interface_name]
    # close file
    res = qa.guest_close_file(domain, file_handle)
    
    # open in write mode
    res = qa.guest_open_file(domain, file_path, mode="w")
    file_handle = qa.get_file_handle(res)
    modified_content = yaml.dump(yaml_data, default_flow_style=False)
    # write back modified content
    res = qa.guest_write_file(domain, file_handle, modified_content)
    # close file and apply
    res = qa.guest_close_file(domain, file_handle)
    res = qa.guest_exec(domain, "netplan", ["apply"])
    return APIResponse.success()
    

def retry_with_delay(func, *args, max_retries = 10, delay = 2):
    time.sleep(2)
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args)
            return result
        except libvirt.libvirtError as e:
           print(f"Attempt {attempt} failed. Exception: {str(e)}")
           if attempt < max_retries:
               time.sleep(delay)
    
    return APIResponse.error(code=400, msg=f"Function {func.__name__} failed after {max_retries} attempts")


def ip_link_set_up(interface_name:str):
    iptools.ip_link_set_up(interface_name)
    

def ip_link_add_addr(interface_name:str, addr:str):
    iptools.ip_addr_add(interface_name, addr)
    
def ip_link_del_addr(interface_name:str, addr:str):
    iptools.ip_addr_del(interface_name, addr)