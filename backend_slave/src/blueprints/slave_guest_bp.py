from flask import Blueprint
from slave_guest import service
guest_bp = Blueprint("guest-bp", __name__)

@guest_bp.route("/test")
def test():
    return "test from child"


@guest_bp.route("/addDomain/<xml>/", methods=["POST"])
def add_domain(xml):
    res = service.add_domain(xml)
    return res
