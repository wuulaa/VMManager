import requests
import configparser
from flask import Flask
from src.blueprints.network_bp import network_bp
from src.blueprints.guest_bp import guest_bp

app = Flask(__name__)
app.register_blueprint(network_bp)
app.register_blueprint(guest_bp)


@app.route("/")
def backend():
    return "VMManager backend"


@app.route("/test")
def test():
    response = requests.get("http://127.0.0.1:5001/test")
    if response.status_code == 200:
        return response.text
    return "Failed"
