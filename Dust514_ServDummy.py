import json
import threading
import time
import os
import signal
from flask import Flask, request, jsonify, abort
from werkzeug.serving import make_server
from functools import wraps

app = Flask(__name__)
response_config = {}
config_file = "responses.json"
lock = threading.Lock()

USERNAME = os.environ.get("SERVDUMMY_USER", "admin")
PASSWORD = os.environ.get("SERVDUMMY_PASS", "admin")

# --- Basic Authentication ---
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return jsonify({"error": "Authentication required."}), 401, {"WWW-Authenticate": "Basic realm=Login Required"}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Load and Save Config ---
def load_config():
    global response_config
    try:
        with open(config_file, "r") as f:
            with lock:
                response_config = json.load(f)
    except FileNotFoundError:
        response_config = {}
    except json.JSONDecodeError:
        print("Invalid JSON in config file.")
        response_config = {}

def save_config():
    with lock:
        try:
            with open(config_file, "w") as f:
                json.dump(response_config, f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")

# --- Matching Logic ---
def match_conditions(req_data, conditions):
    for key, expected in conditions.items():
        parts = key.split(".")
        value = req_data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if str(value) != str(expected):
            return False
    return True

# --- Main Routing ---
@app.route("/<path:endpoint>", methods=["GET", "POST"])
def handle_request(endpoint):
    method = request.method.upper()
    key = f"{method} /{endpoint}"

    with lock:
        rules = response_config.get(key, [])

    req_data = {}
    try:
        if request.is_json:
            req_data = request.get_json(silent=True) or {}
    except Exception:
        pass

    req_data.update(request.args.to_dict())
    req_data.update(request.form.to_dict())

    for rule in rules:
        if match_conditions(req_data, rule.get("conditions", {})):
            delay = rule.get("delay", 0)
            if delay > 0:
                time.sleep(delay)
            return jsonify(rule.get("response", {})), rule.get("status", 200)

    return jsonify({"error": "No matching rule"}), 404

# --- Dashboard API ---
@app.route("/_config", methods=["GET", "POST"])
@requires_auth
def config():
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400
        new_config = request.get_json()
        if not isinstance(new_config, dict):
            return jsonify({"error": "Invalid format"}), 400
        with lock:
            response_config.clear()
            response_config.update(new_config)
            save_config()
        return jsonify({"status": "Configuration updated."})
    return jsonify(response_config)

@app.route("/_shutdown", methods=["POST"])
@requires_auth
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()
        return "Server shutting down..."
    abort(500)

# --- Server Thread ---
class ServerThread(threading.Thread):
    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__()
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.daemon = True

    def run(self):
        self.ctx.push()
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

# --- Main Entrypoint ---
if __name__ == "__main__":
    load_config()
    server_thread = ServerThread()
    server_thread.start()
    print("Dust514_ServDummy running on http://localhost:8000")
    try:
        while server_thread.is_alive():
            server_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server_thread.shutdown()
        server_thread.join()
        print("Stopped.")
