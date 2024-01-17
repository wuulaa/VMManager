import requests
from flask import Blueprint
from flask import request

from src.utils import consts

storage_bp = Blueprint("storage-bp", __name__, url_prefix="/kvm")


@storage_bp.route("/backup/create", methods=["POST"])
def create_backup():
   pass


@storage_bp.route("/backup/del", methods=["POST"])
def del_backup():
   pass


@storage_bp.route("/backup/detail")
def backup_detail():
   pass


@storage_bp.route("/backup/backupCreate", methods=["POST"])
def backup_create():
   pass


@storage_bp.route("/backup/list")
def backup_list():
   pass


@storage_bp.route("/template/add")
def add_template():
   pass


@storage_bp.route("/template/del")
def del_template():
   pass


@storage_bp.route("/template/detail")
def template_detail():
   pass


@storage_bp.route("/template/list")
def template_list():
   pass


@storage_bp.route("/template/put")
def put_template():
   pass

