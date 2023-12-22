from flask import Flask
from blueprints.slave_guest_bp import guest_bp

app = Flask(__name__)
app.register_blueprint(guest_bp)


@app.route("/")
def root():
    return "root"
