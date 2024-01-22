from src.network_manager import service as netapi


def create_bridge(bridge_name: str):
    return netapi.create_bridge(bridge_name)


def delete_bridge(bridge_name: str):
    return netapi.delete_bridge(bridge_name)
    

def add_port_to_bridge(bridge_name: str, port_name: str, *interface_attribute_tuples):
    return netapi.add_port_to_bridge(bridge_name, port_name, *interface_attribute_tuples)


def add_vxlan_port_to_bridge(bridge_name: str, port_name: str, remote_ip: str):
    return netapi.add_vxlan_port_to_bridge(bridge_name, port_name, remote_ip)


def delete_port_from_bridge(bridge_name: str, port_name: str):
    return netapi.delete_port_from_bridge(bridge_name, port_name)


def set_port_tag(bridge_name: str, port_name: str, tag: str):
    return netapi.set_port_tag(bridge_name, port_name, tag)


def remove_port_tag(bridge_name: str, port_name: str, tag: str):
    return netapi.remove_port_tag(bridge_name, port_name, tag)


def create_ovs_nat_network(network_addr:str, bridge_name: str):
    return netapi.create_ovs_nat_network(network_addr, bridge_name)

    
def delete_ovs_nat_network(network_addr: str):
    return netapi.delete_ovs_nat_network(network_addr)


def init_iptables():
    # TODO: if modified rules are not saved, add iptable-save here
    return netapi.init_iptables()
    

def create_route(netA: str, netB: str, parent: str):
    return netapi.create_route(netA, netB, parent)
    

def delete_route(netA: str, netB: str, parent: str):
    return netapi.delete_route(netA, netB, parent)

    
def set_guest_ip_ubuntu(uuid: str,
                        ip_address: str,
                        gateway: str,
                        interface_name: str,
                        dns: str = "8.8.8.8",
                        file_path: str = "/etc/netplan/01-network-manager-all.yaml"):
    return netapi.retry_with_delay(netapi.set_guest_ip_ubuntu, uuid, ip_address, gateway, interface_name, dns, file_path)

def init_set_guest_ips_ubuntu(uuid: str,
                        ip_addresses: list[str],
                        gateways: list[str],
                        interface_names: list[str],
                        dns: str = "8.8.8.8",
                        file_path: str = "/etc/netplan/01-network-manager-all.yaml"):
    return netapi.retry_with_delay(netapi.init_set_guest_ips_ubuntu, uuid, ip_addresses, gateways, interface_names, dns, file_path)


def remove_domain_ip_ubuntu(uuid: str, interface_name: str=None, file_path: str = "/etc/netplan/01-network-manager-all.yaml"):
    return netapi.retry_with_delay(netapi.remove_guest_ip_ubuntu, uuid, interface_name, file_path)


