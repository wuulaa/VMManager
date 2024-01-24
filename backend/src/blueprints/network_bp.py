import requests
from flask import Blueprint
from flask import request
from src.network.api import NetworkAPI
from src.utils import consts

network_bp = Blueprint("network-bp", __name__, url_prefix="/kvm")
network_api = NetworkAPI()

@network_bp.route("/network/list")
def list():
    """
    list all networks
    """
    return network_api.list_networks().to_json_str()


@network_bp.route("/network/detail")
def network_detail():
    """
    get detail of a network
    """
    network_name = request.values.get(consts.P_NETWORK_NAME)
    return network_api.network_detail(network_name).to_json_str()


@network_bp.route("/network/ports")
def list_ethernets():
    """
    list all virtual interfaces
    """
    return network_api.list_interfaces().to_json_str()


@network_bp.route("/network/detailPort")
def detailEthernet():
    """
    get a all virtual interfaces detail
    """
    name = request.values.get(consts.P_INTERFACE_NAME)
    return network_api.interface_detail(name).to_json_str()


@network_bp.route("/network/portAdd", methods=["POST"])
def port_add():
    """
    add virtual port to a internet
    """
    name = request.values.get(consts.P_INTERFACE_NAME)
    network_name = request.values.get(consts.P_NETWORK_NAME)
    ipaddress = request.values.get(consts.P_IP_ADDRESS)
    gateway = request.values.get(consts.P_GATEWAY)
    mac = request.values.get(consts.P_MAC)
    return network_api.create_interface(name, network_name, ipaddress, gateway, mac).to_json_str()


@network_bp.route("/network/portDel", methods=["POST"])
def port_del():
    """
    delete virtual port from internet
    """
    name = request.values.get(consts.P_INTERFACE_NAME)
    return network_api.delete_interface(name).to_json_str()


@network_bp.route("/network/portClone", methods=["POST"])
def port_clone():
    """
    add virtual port to a internet
    """
    name = request.values.get(consts.P_INTERFACE_NAME)
    new_name = request.values.get(consts.P_NEW_NAME)
    new_ip = request.values.get(consts.P_NEW_IP_ADDRESS)
    return network_api.clone_interface(name, new_name, new_ip).to_json_str()


@network_bp.route("/network/portPut", methods=["POST"])
def port_put():
    """
    modify a virtual port, currently supports gateway and ipaddr only
    """
    name = request.values.get(consts.P_INTERFACE_NAME)
    ipaddress = request.values.get(consts.P_IP_ADDRESS)
    gateway = request.values.get(consts.P_GATEWAY)
    return network_api.modify_interface(name, ipaddress, gateway).to_json_str()


@network_bp.route("/network/virtualAdd", methods=["POST"])
def virtual_add():
    """
    add virtual network
    """
    network_name = request.values.get(consts.P_NETWORK_NAME)
    address = request.values.get(consts.P_NETWORK_ADDRESS)
    return network_api.create_network(network_name, address).to_json_str()


@network_bp.route("/network/virtualDel", methods=["POST"])
def virtual_del():
    """
    delete virtual network
    """
    network_name = request.values.get(consts.P_NETWORK_NAME)
    return network_api.delete_network(network_name).to_json_str()


@network_bp.route("/network/createTop", methods=["POST"])
def create_top():
    """
    create top bridges and nat network
    """
    network_addr = request.values.get(consts.P_NETWORK_ADDRESS)
    return network_api.create_top_network(network_addr).to_json_str()


@network_bp.route("/network/deleteTop", methods=["POST"])
def delete_top():
    """
    delete top bridges and nat network
    """
    network_addr = request.values.get(consts.P_NETWORK_ADDRESS)
    return network_api.delete_top_network(network_addr).to_json_str()


@network_bp.route("/network/initSetStaticIps", methods=["POST"])
def init_set_ips():
    """
    set all domain interface static ips
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return network_api.init_set_domain_static_ip(domain_uuid=domain_uuid).to_json_str()


