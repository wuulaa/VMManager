import requests
from flask import request
import atexit
from flask import Flask
from src.utils.websockify.websockify_manager import WebSockifyManager
from src.common.scheduler import DomainMonitor
from src.blueprints.network_bp import network_bp
from src.blueprints.guest_bp import guest_bp
from src.blueprints.slave_bp import slave_bp
from src.blueprints.storage_bp import storage_bp
from src.blueprints.user_bp import user_bp
from flask import g
from flask_jwt_extended import JWTManager
from src.utils.jwt import jwt_set_user
import logging
from logging.handlers import TimedRotatingFileHandler
from src.utils.response import APIResponse
from src.utils.config import CONF

app = Flask(__name__)

# register blueprint
app.register_blueprint(network_bp)
app.register_blueprint(guest_bp)
app.register_blueprint(slave_bp)
app.register_blueprint(storage_bp)
app.register_blueprint(user_bp)

# config jwt for user model
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# start monitor 
domainMonitor = DomainMonitor()
domainMonitor.start_monitoring()


@app.route("/")
@jwt_set_user
def backend():
    return "VMManager backend"


@app.route("/test")
def test():
    return APIResponse.success().to_json_str()

if __name__ == "__main__":
    
    # # ininit websockify for vnc
    websockify_manager = WebSockifyManager()
    atexit.register(websockify_manager.stop_websockify)
    websockify_manager.start_websockify()
    
    # logging
    # logging.basicConfig(level=logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler(
        "vm_manager.log", when="D", interval=1, backupCount=15,
        encoding="UTF-8", delay=False, utc=True)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # run app
    port = CONF["flask"]["port"]
    app.run(host="0.0.0.0", port=port)


