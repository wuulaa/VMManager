from flask import Blueprint
from flask import request
from src.slave_guest import api as guestAPI
from src.utils import consts
from src.utils.response import APIResponse
import json
import requests
guest_bp = Blueprint("guest-bp", __name__)

@guest_bp.route("/test")
def test():
    # res = json.loads(APIResponse.success(data={"uuid": "ssssssssssssss"}, msg = "a test").json())
    return "res['data']"


@guest_bp.route("/addDomain/", methods=["POST"])
def add_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    xml = request.values.get(consts.P_DOMAIN_XML)
    res = guestAPI.create_domain(xml)
    if (res.code == 0):
        uuid = guestAPI.get_uuid_by_name(domain_name = domain_name)
        return APIResponse.success(data = {"uuid": uuid}).json()
    else:
        return APIResponse.error(code = 400, msg = res.msg).json()


@guest_bp.route("/shutdownDomain/", methods=["POST"])
def shutdown_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.shutdown_domain(domain_name)
    return res.json()


@guest_bp.route("/destroyDomain/", methods=["POST"])
def destroy_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.destroy_domain(domain_name)
    return res.json()
    
@guest_bp.route("/pauseDomain/", methods=["POST"])
def pause_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.pause_domain(domain_name)
    return res.json()
    
@guest_bp.route("/resumeDomain/", methods=["POST"])
def resume_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.resume_domain(domain_name)
    return res.json()
    
@guest_bp.route("/setAutoRestartDomain/", methods=["POST"])
def set_auto_start_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.set_auto_start_domain(domain_name)
    return res.json()


@guest_bp.route("/startDomain/", methods=["POST"])
def start_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.start_domain(domain_name)
    return res.json()


@guest_bp.route("/renameDomain/", methods=["POST"])
def rename_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    new_name = request.values.get(consts.P_NEW_NAME)
    res = guestAPI.rename_domain(domain_name, new_name)
    return res.json()

@guest_bp.route("/putDes/", methods=["POST"])
def put_description():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    new_description = request.values.get(consts.P_NEW_DESCRIPTION)
    res = guestAPI.put_description(domain_name, new_description)
    return res.json()

@guest_bp.route("/delDomain/", methods=["POST"])
def put_description():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    res = guestAPI.delete_domain(domain_name)
    return res.json()


# @guest_bp.route("/cloneDomain/", methods=["POST"])
# def clone_domain():
#     domain_name = request.values.get(consts.P_DOMAIN_NAME)
#     child_name = request.values.get(consts.P_CHILD_NAME)
#     res = guestAPI.start_domain(domain_name, child_name)
#     if (res.code == 0):
#         return APIResponse.success().json()
#     else:
#         return APIResponse.error(code = 400, msg = res.msg).json()