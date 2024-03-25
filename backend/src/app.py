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

app = Flask(__name__)
app.register_blueprint(network_bp)
app.register_blueprint(guest_bp)
app.register_blueprint(slave_bp)
app.register_blueprint(storage_bp)
domainMonitor = DomainMonitor()
domainMonitor.start_monitoring()

@app.route("/")
def backend():
    return "VMManager backend"


@app.route("/test")
def test():
    pass

if __name__ == "__main__":
    websockify_manager = WebSockifyManager()
    atexit.register(websockify_manager.stop_websockify)
    websockify_manager.start_websockify()
    app.run(host="127.0.0.1", port=5000)
