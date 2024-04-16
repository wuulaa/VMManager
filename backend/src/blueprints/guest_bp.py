from flask import Blueprint
from flask import request
import requests
from src.utils.jwt import jwt_set_user
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

@guest_bp.route("/list", methods=["POST"])
@jwt_set_user
def get_domains_list():
    user_name = request.values.get(consts.P_USER_NAME)
    response = APIResponse()
    response.set_code(0)
    resp = guestAPI.get_domains_list(user_name = user_name)

    if not resp.is_success():
        return resp.to_json_str()
    
    if resp.get_data() is None:
        return resp.to_json_str()
    
    guest_list = []
    for item in resp.get_data():
        guest = {}
        guest[consts.P_DOMAIN_NAME] = item.name
        guest[consts.P_DOMAIN_UUID] = item.uuid
        guest[consts.P_SLAVE_NAME] = item.slave_name
        guest[consts.P_STATUS] = item.status
        guest[consts.P_ARCHITECTURE] = item.architecture
        guest[consts.P_DESCRIPTION] = item.description
        guest[consts.P_CPU] = item.cpu
        guest[consts.P_MAX_CPU] = item.max_cpu
        guest[consts.P_MEMORY] = item.memory
        guest[consts.P_MAX_MEMORY] = item.max_memory
        guest_list.append(guest)
    response.set_data(guest_list)
    return response.to_json_str()

@guest_bp.route("/detail", methods=["GET"])
@jwt_set_user
def get_domain_detail():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.get_domain_detail(domain_uuid).to_json_str()

@guest_bp.route("/add", methods=["POST"])
@jwt_set_user
def create_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    cpu_num = request.values.get(consts.P_CPU)
    memory_size = request.values.get(consts.P_MEMORY_SIZE, 2097152)
    architecture = request.values.get(consts.P_ARCHITECTURE, "x86")
    max_cpu =  request.values.get(consts.P_MAX_CPU, 2)
    max_memory =  request.values.get(consts.P_MAX_MEMORY, 2097152)
    
    
    return guestAPI.create_domain(domain_name,
                                  slave_name,
                                  architecture=architecture,
                                  cpu=cpu_num,
                                  memory=memory_size, 
                                  max_cpu=max_cpu,
                                  max_memory=max_memory).to_json_str()

@guest_bp.route("/putName", methods=["POST"])
@jwt_set_user
def rename_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    new_name = request.values.get(consts.P_NEW_NAME)
    return guestAPI.rename_domain(domain_uuid, new_name).to_json_str()

@guest_bp.route("/putDes", methods=["POST"])
@jwt_set_user
def put_description():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    new_description = request.values.get(consts.P_NEW_DESCRIPTION)
    return guestAPI.put_description(domain_uuid, new_description).to_json_str()

@guest_bp.route("/del", methods=["POST"])
@jwt_set_user
def delete_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.delete_domain(domain_uuid, flags = flags).to_json_str()


@guest_bp.route("/start", methods=["POST"])
@jwt_set_user
def start():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.start_domain(domain_uuid).to_json_str()


@guest_bp.route("/shutdown", methods=["POST"])
@jwt_set_user
def shutdown_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.shutdown_domain(domain_uuid).to_json_str()

@guest_bp.route("/destroy", methods=["POST"])
@jwt_set_user
def destroy_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.destroy_domain(domain_uuid).to_json_str()

@guest_bp.route("/pause", methods=["POST"])
@jwt_set_user
def pause_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.pause_domain(domain_uuid).to_json_str()

@guest_bp.route("/resume", methods=["POST"])
@jwt_set_user
def resume_domain():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.resume_domain(domain_uuid).to_json_str()

@guest_bp.route("/reboot", methods=["POST"])
@jwt_set_user
def reboot():
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.reboot_domain(domain_uuid).to_json_str()

@guest_bp.route("/clone", methods=["POST"])
@jwt_set_user
def clone():
    pass
    
    
@guest_bp.route("/migrate", methods=["POST"])
@jwt_set_user
def migrate():
    pass
 
@guest_bp.route("/monitor")
def monitor_domain():
    """
    monitor domain status, note that domain should be running
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.monitor(domain_uuid).to_json_str()

@guest_bp.route("/getStoredMonitor", methods=["POST"])
def get_stored_monitor_domain():
    """
    get stored domain monitor status, note that if domain was not running
    there would be no data.
    store at most one hour's data in redis
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.get_stored_monitor_data(domain_uuid).to_json_str()


@guest_bp.route("/setUserPasswd")
@jwt_set_user
def set_user_passwd():
    """
    set domain user passwd, domain should be running
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    user_name = request.values.get(consts.P_USER_NAME)
    passwd = request.values.get(consts.P_PASSWD)
    return guestAPI.set_user_passwd(domain_uuid, user_name, passwd).to_json_str()

@guest_bp.route("/setCPU", methods=["POST"])
@jwt_set_user
def set_cpu():
    cpu_num = request.values.get(consts.P_CPU_NUM)
    flags = request.values.get(consts.P_FLAGS)
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.set_domain_vcpu(domain_uuid, cpu_num = cpu_num, flags = flags).to_json_str()

@guest_bp.route("/setMemory", methods=["POST"])
@jwt_set_user
def set_memory():
    memory_size = request.values.get(consts.P_MEMORY_SIZE)
    flags = request.values.get(consts.P_FLAGS)
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.set_domain_memory(domain_uuid, memory_size = memory_size, flags = flags).to_json_str()

@guest_bp.route("/batchGetDoaminsDetail", methods=["POST"])
@jwt_set_user
def batch_get_domains_detail():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_domains_detail(domains_uuid_list).to_json_str()

@guest_bp.route("/batchStartDomains", methods=["POST"])
@jwt_set_user
def batch_start_domain():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_start_domains(domains_uuid_list).to_json_str()

@guest_bp.route("/batchPauseDomains", methods=["POST"])
@jwt_set_user
def batch_pause_domain():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_pause_domains(domains_uuid_list).to_json_str()

@guest_bp.route("/batchResumeDomains", methods=["POST"])
@jwt_set_user
def batch_resume_domain():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_restart_domains(domains_uuid_list).to_json_str()

@guest_bp.route("/batchShutdownDomains", methods=["POST"])
@jwt_set_user
def batch_shutdown_domain():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_shutdown_domains(domains_uuid_list).to_json_str()

@guest_bp.route("/batchDeleteDomains", methods=["POST"])
@jwt_set_user
def batch_delete_domain():
    flags = request.values.get(consts.P_FLAGS)
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_delete_domains(domains_uuid_list, flags = flags).to_json_str()

@guest_bp.route("/batchRestartDomains", methods=["POST"])
@jwt_set_user
def batch_restart_domain():
    domains_uuid_list = request.values.getlist(consts.P_DOMAINS_UUID_LIST)
    return guestAPI.batch_restart_domains(domains_uuid_list).to_json_str()


@guest_bp.route("/attachNic", methods=["POST"])
@jwt_set_user
def attach_nic():
    """
    attach a interface to domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.attach_nic(domain_uuid, interface_name, flags = flags).to_json_str()


@guest_bp.route("/detachNic", methods=["POST"])
@jwt_set_user
def detach_nic():
    """
    detach a nic from domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    interface_name = request.values.get(consts.P_INTERFACE_NAME)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.detach_nic(domain_uuid, interface_name, flags = flags).to_json_str()


@guest_bp.route("/listNic", methods=["POST"])
@jwt_set_user
def list_nic():
    """
    list nics of domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
  
    return guestAPI.list_nic(domain_uuid).to_json_str()


@guest_bp.route("/addVNC", methods=["POST"])
@jwt_set_user
def add_vnc():
    """
    attach a vnc to domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.add_vnc(domain_uuid, port, passwd, flags = flags).to_json_str()


@guest_bp.route("/deleteVNC", methods=["POST"])
@jwt_set_user
def delete_vnc():
    """
    delete a vnc from domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.delete_vnc(domain_uuid, flags = flags).to_json_str()


@guest_bp.route("/getVNC", methods=["POST"])
@jwt_set_user
def get_vnc_addr():
    """
    get domain's vnc addr
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    return guestAPI.get_vnc_addr(domain_uuid).to_json_str()


@guest_bp.route("/addSPICE", methods=["POST"])
@jwt_set_user
def add_spice():
    """
    attach a vnc to domain
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    return guestAPI.add_spice(domain_uuid, port, passwd, flags = flags).to_json_str()


@guest_bp.route("/setGraphicPasswd", methods=["POST"])
@jwt_set_user
def change_graphic_passwd():
    """
    change passwd for vnc or spice
    """
    domain_uuid = request.values.get(consts.P_DOMAIN_UUID)
    port = request.values.get(consts.P_PORT)
    passwd = request.values.get(consts.P_PASSWD)
    flags = request.values.get(consts.P_FLAGS)
    vnc = request.values.get(consts.P_VNC)
    if vnc is None:
        vnc = True
    return guestAPI.change_graphic_passwd(domain_uuid, 
                                          port, passwd, flags = flags,
                                          vnc = vnc).to_json_str()



@guest_bp.route("/attachDisk", methods=["POST"])
@jwt_set_user
def attach_disk():
    guest_uuid = request.values.get(consts.P_GUEST_UUID)
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    volume_name = request.values.get(consts.P_VOLUME_NAME)
    size = request.values.get(consts.P_VOLUME_SIZE)
    return guestAPI.attach_disk(guest_uuid, volume_name, size,
                                volume_uuid=volume_uuid).to_json_str()


@guest_bp.route("/detachDisk", methods=["POST"])
@jwt_set_user
def detach_disk():
    domain_uuid = request.values.get(consts.P_GUEST_UUID)
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    return guestAPI.detach_disk(domain_uuid, volume_uuid).to_json_str()


@guest_bp.route("/snapshotAdd", methods=["POST"])
@jwt_set_user
def add_snapshot():
    volume_uuid = request.values.get(consts.P_VOLUME_UUID)
    snap_name = request.values.get(consts.P_SNAP_NAME)    
    return guestAPI.add_snapshot(volume_uuid, snap_name).to_json_str()


@guest_bp.route("/putSnapshotName", methods=["POST"])
@jwt_set_user
def put_snapshot_name():
    pass


@guest_bp.route("/snapshotDetail", methods=["POST"])
@jwt_set_user
def snapshot_detail():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.get_snap_info(snap_uuid).to_json_str()
    

@guest_bp.route("/snapshotDel", methods=["POST"])
@jwt_set_user
def del_snapshot():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.del_snapshot(snap_uuid).to_json_str()


@guest_bp.route("/snapshotRestore", methods=["POST"])
@jwt_set_user
def restore_snapshot():
    snap_uuid = request.values.get(consts.P_SNAP_UUID)
    return guestAPI.rollback_to_snapshot(snap_uuid).to_json_str()


@guest_bp.route("/snapshotSave", methods=["POST"])
@jwt_set_user
def save_snapshot():
    pass


@guest_bp.route("/snapshotToImage", methods=["POST"])
@jwt_set_user
def snapshot_to_image():
    pass
