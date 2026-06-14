"""
Hello-Homelab Flask application.

Port and health path are configured via APP_PORT and HEALTH_PATH in config.env.
"""

import os

from flask import Flask, jsonify

app = Flask(__name__)

APP_PORT = int(os.environ.get("APP_PORT", "5001"))
HEALTH_PATH = os.environ.get("HEALTH_PATH", "/health")


@app.route("/")
def home():
    return "Hello from the homelab!"


@app.route(HEALTH_PATH)
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
