from flask import Blueprint
from flask import request
import requests
from src.domain_xml.xml_init import create_initial_xml
from src.guest.api import GuestAPI, SlaveAPI
from src.utils.response import APIResponse
from src.utils import consts
guest_bp = Blueprint("guest-bp", __name__, url_prefix="/kvm/guest")

guestAPI = GuestAPI()

@guest_bp.route("/test")
def guest():
    response: requests.Response = requests.get(url="http://127.0.0.1:5001/test")
    return APIResponse().deserialize_response(response.json()).to_json_str()

@guest_bp.route("/list", methods=["GET"])
def get_domains_list():
    response =APIResponse()
    response.set_code(0)
    guest_list = []
    for item in guestAPI.get_domains_list():
        guest = {}
        guest["domain_name"] = item.name
        guest["domain_uuid"] = item.uuid
        guest["slave_name"] = item.slave_name
        guest_list.append(guest)
    response.set_data(guest_list)
    return response.to_json_str()

@guest_bp.route("/detail", methods=["GET"])
def get_domain_detail():
    return 

@guest_bp.route("/add", methods=["POST"])
def create_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.create_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/putName", methods=["POST"])
def rename_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    new_name = request.values.get(consts.P_NEW_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.rename_domain(domain_name, new_name, slave_name).to_json_str()

@guest_bp.route("/putDes", methods=["POST"])
def put_description():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    new_description = request.values.get(consts.P_NEW_DESCRIPTION)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.put_description(domain_name, new_description, slave_name).to_json_str()

@guest_bp.route("/del", methods=["POST"])
def delete_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.delete_domain(domain_name, slave_name).to_json_str()


@guest_bp.route("/start", methods=["POST"])
def start():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.start_domain(domain_name, slave_name).to_json_str()


@guest_bp.route("/shutdown", methods=["POST"])
def shutdown_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.shutdown_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/destroy", methods=["POST"])
def destroy_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.destroy_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/pause", methods=["POST"])
def pause_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.pause_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/resume", methods=["POST"])
def resume_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.resume_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/reboot", methods=["POST"])
def reboot():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.reboot_domain(domain_name, slave_name).to_json_str()

@guest_bp.route("/batchStartDomains", methods=["POST"])
def batch_start_domain():
    domains_name_list = request.values.get(consts.P_DOMAINS_NAME_LIST)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.batch_start_domains(domains_name_list, slave_name).to_json_str()

@guest_bp.route("/batchPauseDomains", methods=["POST"])
def batch_pause_domain():
    domains_name_list = request.values.get(consts.P_DOMAINS_NAME_LIST)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.batch_pause_domains(domains_name_list, slave_name).to_json_str()

@guest_bp.route("/batchShutdownDomains", methods=["POST"])
def batch_shutdown_domain():
    domains_name_list = request.values.get(consts.P_DOMAINS_NAME_LIST)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.batch_shutdown_domains(domains_name_list, slave_name).to_json_str()

@guest_bp.route("/batchDeleteDomains", methods=["POST"])
def batch_delete_domain():
    domains_name_list = request.values.get(consts.P_DOMAINS_NAME_LIST)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.batch_delete_domains(domains_name_list, slave_name).to_json_str()

@guest_bp.route("/batchRestartDomains", methods=["POST"])
def batch_restart_domain():
    domains_name_list = request.values.get(consts.P_DOMAINS_NAME_LIST)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.batch_restart_domains(domains_name_list, slave_name).to_json_str()


@guest_bp.route("/attachNic", methods=["POST"])
def attach_nic():
    """
    attach a interface to domain
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.attach_nic(domain_name, slave_name, interface_name, int(flags)).to_json_str()


@guest_bp.route("/detachNic", methods=["POST"])
def detach_nic():
    """
    detach a nic from domain
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.detach_nic(domain_name, slave_name, interface_name, int(flags)).to_json_str()


@guest_bp.route("/listNic", methods=["POST"])
def list_nic():
    """
    list nics of domain
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
  
    return guestAPI.list_nic(domain_name, slave_name).to_json_str()


@guest_bp.route("/addVNC", methods=["POST"])
def add_vnc():
    """
    attach a vnc to domain
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.add_vnc(domain_name, slave_name, port, passwd, flags).to_json_str()


@guest_bp.route("/addSPICE", methods=["POST"])
def add_spice():
    """
    attach a vnc to domain
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.add_spice(domain_name, slave_name, port, passwd, flags).to_json_str()


@guest_bp.route("/setGraphicPasswd", methods=["POST"])
def change_graphic_passwd():
    """
    change passwd for vnc or spice
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    vnc = request.values.get(consts.P_VNC)
    if vnc is None:
        vnc = True
    return guestAPI.change_graphic_passwd(domain_name, slave_name,
                                          port, passwd, int(flags),
                                          vnc).to_json_str()

 
@guest_bp.route("/monitor")
def monitor_domain():
    """
    monitor domain status, note that domain should be running
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return guestAPI.monitor(domain_name, slave_name).to_json_str()


@guest_bp.route("/setUserPasswd")
def set_user_passwd():
    """
    set domain user passwd, domain should be running
    """
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    user_name = request.values.get(consts.P_USER_NAME)
    passwd = request.values.get(consts.P_PASSWD)
    return guestAPI.set_user_passwd(domain_name, slave_name, user_name, passwd).to_json_str()


@guest_bp.route("/clone", methods=["POST"])
def clone():
    pass
    
    
@guest_bp.route("/migrate", methods=["POST"])
def migrate():
    pass


@guest_bp.route("/attachDisk", methods=["POST"])
def attach_disk():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    size = request.values.get(consts.P_MEMORY_SIZE)
    volume_name = request.values.get(consts.P_VOLUME_NAME)
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.attach_disk(domain_name, slave_name, volume_name, volume_uuid, size,flags)


@guest_bp.route("/detachDisk", methods=["POST"])
def detach_disk():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.detach_disk(domain_name, slave_name, volume_uuid, flags)


@guest_bp.route("/diskCopy", methods=["POST"])
def disk_copy():
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    copy_name = request.values.get(consts.P_COPY_NAME)
    return guestAPI.add_disk_copy(volume_uuid, copy_name)


@guest_bp.route("/diskCopyCancel", methods=["POST"])
def disk_copy_cancel():
    pass


@guest_bp.route("/diskCopyDel", methods=["POST"])
def disk_copy_del():
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return guestAPI.del_disk_copy(volume_uuid)


@guest_bp.route("/diskCopyList")
def disk_copy_list():
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return guestAPI.get_disk_copys(volume_uuid)


@guest_bp.route("/diskCopyRecover", methods=["POST"])
def disk_copy_recover():
    pass


@guest_bp.route("/snapshotAdd", methods=["POST"])
def add_snapshot():
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    snap_name = request.values.get(consts.P_SNAP_NAME)    
    return guestAPI.add_snapshot(volume_uuid, snap_name)


@guest_bp.route("/putSnapshotName", methods=["POST"])
def put_snapshot_name():
    pass


@guest_bp.route("/snapshotDetail", methods=["POST"])
def snapshot_detail():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.get_snap_info(snap_uuid)
    

@guest_bp.route("/snapshotDel", methods=["POST"])
def del_snapshot():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.del_snapshot(snap_uuid)


@guest_bp.route("/snapshotRestore", methods=["POST"])
def restore_snapshot():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.rollback_to_snapshot(snap_uuid)


@guest_bp.route("/snapshotSave", methods=["POST"])
def save_snapshot():
    pass


@guest_bp.route("/snapshotToImage", methods=["POST"])
def snapshot_to_image():
    pass


@guest_bp.route("/setCPU", methods=["POST"])
def set_cpu():
    cpu_num = request.values.get(consts.P_CPU_NUM)
    flag = request.values.get(consts.P_FLAGS)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    return guestAPI.set_domain_vcpu(domain_name, slave_name, cpu_num, flag).to_json_str()

@guest_bp.route("/setMemory", methods=["POST"])
def set_memory():
    memory_size = request.values.get(consts.P_MEMORY_SIZE)
    flag = request.values.get(consts.P_FLAGS)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    return guestAPI.set_domain_memory(domain_name, slave_name, memory_size, flag).to_json_str()

