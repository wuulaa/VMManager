from flask import Blueprint
from flask import request
from src.slave_guest import service as guestAPI
from src.utils import consts
from src.utils.response import APIResponse
import json
guest_bp = Blueprint("guest-bp", __name__)

@guest_bp.route("/test")
def test():
    return APIResponse(1, {"test": "16561616"}, msg = "tessadbasjbhj").to_json_str()

@guest_bp.route("/addDomain/", methods=["POST"])
def add_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    xml = request.values.get(consts.P_DOMAIN_XML)
    res = guestAPI.create_domain(xml)
    if (res.code == 0):
        uuid = guestAPI.get_uuid_by_name(domain_name = domain_name)
        return APIResponse.success(data = {"uuid": uuid}).to_json_str()
    else:
        return APIResponse.error(code = 400, msg = res.msg).to_json_str()

@guest_bp.route("/shutdownDomain/", methods=["POST"])
def shutdown_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.shutdown_domain(domain_uuid)
    return res.to_json_str()


@guest_bp.route("/destroyDomain/", methods=["POST"])
def destroy_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.destroy_domain(domain_uuid)
    return res.to_json_str()
    
@guest_bp.route("/pauseDomain/", methods=["POST"])
def pause_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.pause_domain(domain_uuid)
    return res.to_json_str()
    
@guest_bp.route("/resumeDomain/", methods=["POST"])
def resume_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.resume_domain(domain_uuid)
    return res.to_json_str()
    
@guest_bp.route("/setAutoRestartDomain/", methods=["POST"])
def set_auto_start_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.set_auto_start_domain(domain_uuid)
    return res.to_json_str()

@guest_bp.route("/startDomain/", methods=["POST"])
def start_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.start_domain(domain_uuid)
    return res.to_json_str()

@guest_bp.route("/rebootDomain/", methods=["POST"])
def reboot_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.reboot_domain(domain_uuid)
    return res.to_json_str()

@guest_bp.route("/batchStartDomains/", methods=["POST"])
def start_domains():
    domain_uuid_list = request.values.getlist(consts.P_DOMAINS_NAME_LIST)
    res = guestAPI.batch_start_domains(domain_uuid_list)
    return res.to_json_str()

@guest_bp.route("/batchPauseDomains/", methods=["POST"])
def pause_domains():
    domain_uuid_list = request.values.getlist(consts.P_DOMAINS_NAME_LIST)
    res = guestAPI.batch_pause_domains(domain_uuid_list)
    return res.to_json_str()

@guest_bp.route("/batchShutdownDomains/", methods=["POST"])
def shutdown_domains():
    domain_uuid_list = request.values.getlist(consts.P_DOMAINS_NAME_LIST)
    res = guestAPI.batch_shutdown_domains(domain_uuid_list)
    return res.to_json_str()

@guest_bp.route("/batchDeleteDomains/", methods=["POST"])
def delete_domains():
    domain_uuid_list = request.values.getlist(consts.P_DOMAINS_NAME_LIST)
    res = guestAPI.batch_delete_domains(domain_uuid_list)
    return res.to_json_str()

@guest_bp.route("/batchRestartDomains/", methods=["POST"])
def restart_domains():
    domain_uuid_list = request.values.getlist(consts.P_DOMAINS_NAME_LIST)
    res = guestAPI.batch_restart_domains(domain_uuid_list)
    return res.to_json_str()

@guest_bp.route("/renameDomain/", methods=["POST"])
def rename_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    new_name = request.values.get(consts.P_NEW_NAME)
    res = guestAPI.rename_domain(domain_uuid, new_name)
    return res.to_json_str()

@guest_bp.route("/putDes/", methods=["POST"])
def put_description():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    new_description = request.values.get(consts.P_NEW_DESCRIPTION)
    res = guestAPI.put_description(domain_uuid, new_description)
    return res.to_json_str()

@guest_bp.route("/delDomain/", methods=["POST"])
def delete_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res = guestAPI.delete_domain(domain_uuid)
    return res.to_json_str()

@guest_bp.route("/attachDevice/", methods=["POST"])
def attach_device():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    xml = request.values.get(consts.P_DEVICE_XML)
    flags = request.values.get(consts.P_FLAGS)
    if flags:
        flags = int(flags)
    res = guestAPI.attach_device(domain_uuid, xml, flags)
    return res.to_json_str()

@guest_bp.route("/detachDevice/", methods=["POST"])
def detach_device():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    xml = request.values.get(consts.P_DEVICE_XML)
    flags = request.values.get(consts.P_FLAGS)
    if flags:
        flags = int(flags)
    res = guestAPI.detach_device(domain_uuid, xml, flags)
    return res.to_json_str()

@guest_bp.route("/updateDevice/", methods=["POST"])
def update_device():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    xml = request.values.get(consts.P_DEVICE_XML)
    flags = request.values.get(consts.P_FLAGS)
    if flags:
        flags = int(flags)
    res = guestAPI.update_device(domain_uuid, xml, flags)
    return res.to_json_str()

@guest_bp.route("/setCPU/", methods=["POST"])
def set_domain_vcpu():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    cpu_num = int(request.values.get(consts.P_CPU_NUM))
    flags = request.values.get(consts.P_FLAGS)
    if flags:
        flags = int(flags)
    res = guestAPI.set_domain_vcpu(domain_uuid, cpu_num, flags)
    return res.to_json_str()

@guest_bp.route("/setMemory/", methods=["POST"])
def set_domain_memory():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    memory_size = int(request.values.get(consts.P_MEMORY_SIZE))
    flags = request.values.get(consts.P_FLAGS)
    if flags:
        flags = int(flags)
    res = guestAPI.set_domain_memory(domain_uuid, memory_size, flags)
    return res.to_json_str()

@guest_bp.route("/monitor/", methods=["POST"])
def monitor():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res: APIResponse = guestAPI.monitor(domain_uuid)
    return res.to_json_str()

@guest_bp.route("/setUserPasswd/", methods=["POST"])
def set_user_passwd():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    user_name = request.values.get(consts.P_USER_NAME)
    passwd = request.values.get(consts.P_PASSWD)
    res: APIResponse = guestAPI.set_user_passwd(domain_uuid, user_name, passwd)
    return res.to_json_str()


@guest_bp.route("/getInterfaceAddresses/", methods=["POST"])
def get_domain_ip_addressed():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    res: APIResponse = guestAPI.get_domain_interface_addresses(domain_uuid)
    return res.to_json_str()
