from flask import Blueprint
from flask import request
from src.utils import consts
from src.slave_network import service
network_bp = Blueprint("network-bp", __name__)


@network_bp.post("/init")
def init_cluster_network():
    ip_ddr = request.values.get(consts.P_NETWORK_ADDRESS)
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    service.init_iptables()
    res = service.create_ovs_nat_network(ip_ddr, bridge_name)
    return res.json()


@network_bp.post("/createBridge")
def add_bridge():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    res = service.create_bridge(bridge_name)
    return res.json()


@network_bp.post("/deleteBridge")
def del_bridge():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    res = service.delete_bridge(bridge_name)
    return res.json()


@network_bp.post("/addPort")
def add_port():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    port_name = request.values.get(consts.P_PORT_NAME)
    port_type = request.values.get(consts.P_TYPE)
    res = service.add_port_to_bridge(bridge_name, port_name, ("type", port_type))
    return res.json()


@network_bp.post("/delPort")
def del_port():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    port_name = request.values.get(consts.P_PORT_NAME)
    res = service.delete_port_from_bridge(bridge_name, port_name)
    return res.json()


@network_bp.post("/addVxlanPort")
def add_vxlan_port():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    port_name = request.values.get(consts.P_PORT_NAME)
    remote_ip = request.values.get(consts.P_REMOTE_IP)
    res = service.add_vxlan_port_to_bridge(bridge_name, port_name, remote_ip)
    return res.json()


@network_bp.post("/setTag")
def set_tag():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    port_name = request.values.get(consts.P_PORT_NAME)
    tag = request.values.get(consts.P_TAG)
    res = service.set_port_tag(bridge_name, port_name, tag)
    return res.json()


@network_bp.post("/removeTag")
def remove_tag():
    bridge_name = request.values.get(consts.P_BRIDGE_NAME)
    port_name = request.values.get(consts.P_PORT_NAME)
    tag = request.values.get(consts.P_TAG)
    res = service.remove_port_tag(bridge_name, port_name, tag)
    return res.json()


@network_bp.post("/addRoute")
def create_route():
    networkA = request.values.get(consts.P_NETWORKA)
    networkB = request.values.get(consts.P_NETWORKB)
    parent = request.values.get(consts.P_PARENT)
    res = service.create_route(networkA, networkB, parent)
    return res.json()


@network_bp.post("/deleteRoute")
def delete_troute():
    networkA = request.values.get(consts.P_NETWORKA)
    networkB = request.values.get(consts.P_NETWORKB)
    parent = request.values.get(consts.P_PARENT)
    res = service.delete_route(networkA, networkB, parent)
    return res.json()


@network_bp.post("/setStaticIP")
def set_static_ip():
    domain_UUID = request.values.get(consts.P_DOMAIN_UUID)
    ipaddress = request.values.get(consts.P_NETWORK_ADDRESS)
    gateway = request.values.get(consts.P_GATEWAY)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    res = service.set_guest_ip_ubuntu(domain_UUID, ipaddress, gateway, interface_name)
    return res.json()