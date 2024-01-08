from flask import Blueprint
from flask import request
import requests
from src.domain_xml.xml_init import create_initial_xml
from src.guest.api import *
import src.utils.consts as consts
guest_bp = Blueprint("guest-bp", __name__, url_prefix="/kvm/guest")



@guest_bp.route("/")
def guest():
    return "kvm guest"

@guest_bp.route("/list", methods=["GET"])
def get_domains_list():
    return get_domains_list()

@guest_bp.route("/detail", methods=["GET"])
def get_domain_detail():
    return 

@guest_bp.route("/rename", methods=["POST"])
def rename_domain():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    new_name = request.values.get(consts.P_NEW_NAME)
    slave_name = request.values.get(consts.P_SLAVE_NAME)

@guest_bp.route("/add", methods=["POST"])
def add():
    domain_name = request.values.get(consts.P_DOMAIN_NAME)
    slave = request.values.get("slave")
    return create_domain(domain_name, slave)


@guest_bp.route("/shutdown", methods=["POST"])
def shutdown():
    name = request.values.get("name")
    slave = request.values.get("slave")
    return shutdown_domain(name, slave)


@guest_bp.route("/destroy", methods=["POST"])
def destroy():
    name = request.values.get("name")
    slave = request.values.get("slave")
    return destroy_domain(name, slave)


@guest_bp.route("/start", methods=["POST"])
def start():
    name = request.values.get("name")
    slave = request.values.get("slave")
    return start_domain(name, slave)


#to do
@guest_bp.route("/clone", methods=["POST"])
def clone():
    name = request.values.get("name")
    child_name = request.values.get("childName")
    slave = request.values.get("slave")
    return clone_domain(name, child_name, slave)


@guest_bp.route("/addDevice", methods=["POST"])
def add_device():
    pass


@guest_bp.route("/addEthernet", methods=["POST"])
def add_ethernet():
    pass


@guest_bp.route("/attachDick", methods=["POST"])
def attach_disk():
    pass


@guest_bp.route("/attachNic", methods=["POST"])
def attach_nic():
    pass


@guest_bp.route("/createList")
def create_list():
    pass


@guest_bp.route("/del", methods=["POST"])
def delete():
    pass


@guest_bp.route("/delDevice", methods=["POST"])
def delete_device():
    pass


@guest_bp.route("/detachDisk", methods=["POST"])
def detach_disk():
    pass


@guest_bp.route("/detachNic", methods=["POST"])
def detach_nic():
    pass


@guest_bp.route("/detail")
def detail():
    pass


@guest_bp.route("/diskCopyCancel", methods=["POST"])
def disk_copy_cancel():
    pass


@guest_bp.route("/diskCopyDel", methods=["POST"])
def disk_copy_del():
    pass


@guest_bp.route("/diskCopyList")
def disk_copy_list():
    pass


@guest_bp.route("/diskCopyRecover", methods=["POST"])
def disk_copy_recover():
    pass


@guest_bp.route("/display", methods=["POST"])
def display():
    pass


@guest_bp.route("/file", methods=["POST"])
def file():
    pass


@guest_bp.route("/list")
def list_guest():
    pass


@guest_bp.route("/mergesnapshot", methods=["POST"])
def merge_snapshot():
    pass


@guest_bp.route("/migrate", methods=["POST"])
def migrate():
    pass


@guest_bp.route("/modify/vncPasswd", methods=["POST"])
def modify_vnc_passwd():
    pass


@guest_bp.route("/mountCdrom", methods=["POST"])
def mount_cdrom():
    pass


@guest_bp.route("/mountDisk", methods=["POST"])
def mount_disk():
    pass


@guest_bp.route("/mountLun", methods=["POST"])
def mount_lun():
    pass


@guest_bp.route("/mountUsb", methods=["POST"])
def mount_usb():
    pass


@guest_bp.route("/move", methods=["POST"])
def move():
    pass


@guest_bp.route("/pause", methods=["POST"])
def pause():
    pass


@guest_bp.route("/putDes", methods=["POST"])
def put_description():
    pass


@guest_bp.route("/putDevice", methods=["POST"])
def put_device():
    pass


@guest_bp.route("/putDiskBus", methods=["POST"])
def put_disk_bus():
    pass


@guest_bp.route("/putEthernet", methods=["POST"])
def put_ethernet():
    pass


@guest_bp.route("/putName", methods=["POST"])
def put_name():
    pass


@guest_bp.route("/putSnapshotName", methods=["POST"])
def put_snapshot_name():
    pass


@guest_bp.route("/reboot", methods=["POST"])
def reboot():
    pass


@guest_bp.route("/setAutoRestart", methods=["POST"])
def set_auto_restart():
    pass


@guest_bp.route("/setCpu", methods=["POST"])
def set_cpu():
    pass


@guest_bp.route("/sflow")
def sflow():
    pass


