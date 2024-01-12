from flask import Flask
from src.blueprints.slave_guest_bp import guest_bp
from src.blueprints.slave_network_bp import network_bp

app = Flask(__name__)
app.register_blueprint(guest_bp)
app.register_blueprint(network_bp)


@app.route("/")
def root():
    return "root"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)