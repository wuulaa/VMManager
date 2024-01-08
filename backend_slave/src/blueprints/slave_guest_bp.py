from flask import Blueprint
from flask import request
from src.slave_guest import service
from src.utils import consts
import requests
guest_bp = Blueprint("guest-bp", __name__)

@guest_bp.route("/test")
def test():
    return "test from child"


@guest_bp.route("/addDomain/", methods=["POST"])
def add_domain():
    domain_name = request.values.get("domain_name")
    xml = request.values.get("domain_xml")
    xml = request.values.get(consts.P_DOMAIN_XML)
    res = service.create_domain(xml)
    if (res.code == 0):
        uuid = service.get_uuid_by_name(domain_name = domain_name)
        return {"success": True, "uuid":uuid}
    else:
        return {"success": False, "uuid": None}


@guest_bp.route("/shutdownDomain/", methods=["POST"])
def shutdown_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = service.shutdown_domain(domain_name)
    return str(res)


@guest_bp.route("/destroyDomain/", methods=["POST"])
def destroy_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = service.destroy_domain(domain_name)
    return str(res)


@guest_bp.route("/startDomain/", methods=["POST"])
def start_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = service.start_domain(domain_name)
    return str(res)


@guest_bp.route("/cloneDomain/", methods=["POST"])
def clone_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    child_name = request.values.get(consts.P_CHILD_NAME)
    res = service.start_domain(domain_name, child_name)
    return str(res)