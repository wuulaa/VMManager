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


app = Flask(__name__)

app.register_blueprint(network_bp)
app.register_blueprint(guest_bp)
app.register_blueprint(slave_bp)
app.register_blueprint(storage_bp)
app.register_blueprint(user_bp)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

domainMonitor = DomainMonitor()
domainMonitor.start_monitoring()


@app.route("/")
@jwt_set_user
def backend():
    return "VMManager backend"


@app.route("/test")
def test():
    pass

if __name__ == "__main__":
    websockify_manager = WebSockifyManager()
    atexit.register(websockify_manager.stop_websockify)
    websockify_manager.start_websockify()
    app.run(host="0.0.0.0", port=5000)


