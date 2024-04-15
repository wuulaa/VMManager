from flask import Blueprint
from flask import request
from src.user.api import UserAPI
from src.utils.response import APIResponse
from src.utils import consts
user_bp = Blueprint("user-bp", __name__, url_prefix="/kvm/user")
user_api = UserAPI()

@user_bp.route("/register", methods=["POST"])
def register():
    user_name = request.values.get(consts.P_USER_NAME)
    user_password = request.values.get(consts.P_PASSWD)
    is_admin = request.values.get(consts.P_IS_ADMIN)
    if is_admin == "True":
        is_admin = True
    else:
        is_admin = False
    return user_api.register(user_name, user_password, is_admin).to_json_str()


@user_bp.route("/unregister", methods=["POST"])
def unregister():
    user_name = request.values.get(consts.P_USER_NAME)
    return user_api.unregister(user_name).to_json_str()


@user_bp.route("/login", methods=["POST"])
def login():
    user_name = request.values.get(consts.P_USER_NAME)
    user_password = request.values.get(consts.P_PASSWD)
    return user_api.login(user_name, user_password).to_json_str()


@user_bp.route("/logout", methods=["POST"])
def logout():
    user_name = request.values.get(consts.P_USER_NAME)
    return user_api.logout(user_name).to_json_str()


@user_bp.route("/getUsers")
def get_users():
    return user_api.get_user_list().to_json_str()


@user_bp.route("/changePassword")
def change_user_password():
    user_name = request.values.get(consts.P_USER_NAME)
    old_password = request.values.get(consts.P_OLD_PASSWORD)
    new_password = request.values.get(consts.P_NEW_PASSWORD)
    return user_api.change_password(user_name, old_password, new_password).to_json_str()

@user_bp.route("/getUserLastLogin")
def get_user_last_login():
    user_name = request.values.get(consts.P_USER_NAME)
    return user_api.get_user_last_login(user_name).to_json_str()