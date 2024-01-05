from flask import Blueprint
from flask import request
from src.slave_network import service
network_bp = Blueprint("network-bp", __name__)


@network_bp.post("/init")
def init_cluster_network():
    ip_ddr = request.values.get("network_address")
    bridge_name = request.values.get("bridge_name")
    service.init_iptables()
    service.create_ovs_nat_network(ip_ddr, bridge_name)


@network_bp.post("/createBridge")
def add_bridge():
    bridge_name = request.values.get("bridge_name")
    res = service.create_bridge(bridge_name)
    return res.code()


@network_bp.post("/deleteBridge")
def del_bridge():
    bridge_name = request.values.get("bridge_name")
    res = service.delete_bridge(bridge_name)
    return res.code()


@network_bp.post("/addPort")
def add_port():
    bridge_name = request.values.get("bridge_name")
    port_name = request.values.get("port_name")
    port_type = request.values.get("type")
    res = service.add_port_to_bridge(bridge_name, port_name, ("type", port_type))
    return res.code()


@network_bp.post("/delPort")
def del_port():
    bridge_name = request.values.get("bridge_name")
    port_name = request.values.get("port_name")
    res = service.delete_port_from_bridge(bridge_name, port_name)
    return res.code()


@network_bp.post("/addVxlanPort")
def add_vxlan_port():
    bridge_name = request.values.get("bridge_name")
    port_name = request.values.get("port_name")
    remote_ip = request.values.get("remote_ip")
    res = service.add_vxlan_port_to_bridge(bridge_name, port_name, remote_ip)
    return res.code()


@network_bp.post("/setTag")
def set_tag():
    bridge_name = request.values.get("bridge_name")
    port_name = request.values.get("port_name")
    tag = request.values.get("tag")
    res = service.set_port_tag(bridge_name, port_name, tag)
    return res.code()


@network_bp.post("/removeTag")
def remove_tag():
    bridge_name = request.values.get("bridge_name")
    port_name = request.values.get("port_name")
    tag = request.values.get("tag")
    res = service.remove_port_tag(bridge_name, port_name, tag)
    return res.code()


@network_bp.post("/addRoute")
def create_route():
    networkA = request.values.get("networkA")
    networkB = request.values.get("networkB")
    parent = request.values.get("parent")
    res = service.create_route(networkA, networkB, parent)
    return res.code()


@network_bp.post("/deleteRoute")
def delete_troute():
    networkA = request.values.get("networkA")
    networkB = request.values.get("networkB")
    parent = request.values.get("parent")
    res = service.delete_route(networkA, networkB, parent)
    return res.code()