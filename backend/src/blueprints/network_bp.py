from flask import Blueprint

network_bp = Blueprint("network-bp", __name__, url_prefix="/kvm")


@network_bp.route("/")
def network():
    return "network test"


@network_bp.route("/cluster/detail")
def cluster_detail():
    pass


@network_bp.route("/cluster/list")
def cluster_list():
    pass


@network_bp.route("/network/ethernet")
def ethernet():
    pass


@network_bp.route("/network/portGroupAdd", methods=["POST"])
def port_add():
    pass


@network_bp.route("/network/portGroupDel", methods=["POST"])
def port_del():
    pass


@network_bp.route("/network/portGroupPut", methods=["POST"])
def port_put():
    pass


@network_bp.route("/network/virtualAdd", methods=["POST"])
def virtual_add():
    pass


@network_bp.route("/network/virtualDel", methods=["POST"])
def virtual_del():
    pass


@network_bp.route("/network/virtualPut", methods=["POST"])
def virtual_put():
    pass


@network_bp.route("/portGroup/detail")
def port_group_detail():
    pass


@network_bp.route("/portGroup/list")
def port_group_list():
    pass



