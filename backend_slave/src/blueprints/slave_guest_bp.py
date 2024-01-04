from flask import Blueprint
from flask import request
from src.slave_guest import service
import requests
guest_bp = Blueprint("guest-bp", __name__)

@guest_bp.route("/test")
def test():
    return "test from child"


@guest_bp.route("/addDomain/", methods=["POST"])
def add_domain():
    xml = request.values.get("domain_xml")
    res = service.create_domain(xml)
    return str(res)


@guest_bp.route("/shutdownDomain/", methods=["POST"])
def shutdown_domain():
    domain_name = request.values.get("domain_name")
    res = service.shutdown_domain(domain_name)
    return str(res)


@guest_bp.route("/destroyDomain/", methods=["POST"])
def destroy_domain():
    domain_name = request.values.get("domain_name")
    res = service.destroy_domain(domain_name)
    return str(res)


@guest_bp.route("/startDomain/", methods=["POST"])
def start_domain():
    domain_name = request.values.get("domain_name")
    res = service.start_domain(domain_name)
    return str(res)


@guest_bp.route("/cloneDomain/", methods=["POST"])
def clone_domain():
    domain_name = request.values.get("domainName")
    child_name = request.values.get("childName")
    res = service.start_domain(domain_name, child_name)
    return str(res)