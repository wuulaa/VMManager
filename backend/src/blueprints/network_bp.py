import requests
from flask import Blueprint
from flask import request
from src.network.api import NetworkAPI
from src.utils import consts

network_bp = Blueprint("network-bp", __name__, url_prefix="/kvm")
network_api = NetworkAPI()

@network_bp.route("/cluster/detail")
def cluster_detail():
    pass


@network_bp.route("/cluster/list")
def cluster_list():
    pass


@network_bp.route("/network/ethernet")
def ethernet():
    pass


@network_bp.route("/network/portAdd", methods=["POST"])
def port_add():
    name = request.values.get(consts.P_INTERFACE_NAME)
    network_name = request.values.get(consts.P_NETWORK_NAME)
    ipaddress = request.values.get(consts.P_IP_ADDRESS)
    mac = request.values.get(consts.P_MAC)
    return network_api.create_interface(name, network_name, ipaddress, mac).json()


@network_bp.route("/network/portDel", methods=["POST"])
def port_del():
    name = request.values.get(consts.P_INTERFACE_NAME)
    return network_api.delete_interface(name).json()


@network_bp.route("/network/portGroupPut", methods=["POST"])
def port_put():
    pass


@network_bp.route("/network/virtualAdd", methods=["POST"])
def virtual_add():
    """
    add virtual network
    """
    network_name = request.values.get(consts.P_NETWORK_NAME)
    address = request.values.get(consts.P_NETWORK_ADDRESS)
    return network_api.create_network(network_name, address).json()


@network_bp.route("/network/virtualDel", methods=["POST"])
def virtual_del():
    """
    delete virtual network
    """
    network_name = request.values.get(consts.P_NETWORK_NAME)
    return network_api.delete_network(network_name).json()


@network_bp.route("/network/virtualPut", methods=["POST"])
def virtual_put():
    pass


@network_bp.route("/portGroup/detail")
def port_group_detail():
    pass


@network_bp.route("/portGroup/list")
def port_group_list():
    pass



