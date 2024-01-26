from flask import Blueprint
from flask import request
from src.guest.api import GuestAPI, SlaveAPI
from src.utils.response import APIResponse
from src.utils import consts
slave_bp = Blueprint("slave-bp", __name__, url_prefix="/kvm/slave")

guestAPI = GuestAPI()
slaveAPI = SlaveAPI()


@slave_bp.route("/initSlaves", methods=["POST"])
def init_slaves():
    return slaveAPI.init_slave_db().to_json_str()


@slave_bp.route("/add", methods=["POST"])
def add_slave():
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    slave_addr = request.values.get(consts.P_ADDRESS)
    return slaveAPI.create_slave(slave_name, slave_addr).to_json_str()


@slave_bp.route("/del", methods=["POST"])
def delete_slave():
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return slaveAPI.delete_slave(slave_name).to_json_str()


@slave_bp.route("/detail")
def slave_detail():
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return slaveAPI.slave_detail(slave_name).to_json_str()


@slave_bp.route("/getGuests")
def get_slave_guests():
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return slaveAPI.get_slave_guests(slave_name).to_json_str()


@slave_bp.route("/status")
def slave_status():
    slave_name = request.values.get(consts.P_SLAVE_NAME)
    return slaveAPI.get_slave_status(slave_name).to_json_str()