from flask import Flask
from blueprints.network_bp import network_bp
from blueprints.guest_bp import guest_bp

app = Flask(__name__)
app.register_blueprint(network_bp)
app.register_blueprint(guest_bp)


@app.route("/")
def backend():
    return "VMManager backend"
