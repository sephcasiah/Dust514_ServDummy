import json
import threading
import time
from flask import Flask, request, jsonify, abort, Response
from functools import wraps
import os

app = Flask(__name__)
response_config = {}
CONFIG_FILE = 'responses.json'
USERNAME = 'admin'
PASSWORD = 'dust514'
CONFIG_LOCK = threading.Lock()

# Basic Auth Decorator
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        json.dumps({"error": "Authentication required."}),
        401,
        {'WWW-Authenticate': 'Basic realm="Dust514 Server Dummy"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        print(f"[DEBUG] Auth received: {auth}")  # Debug info
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Load Config
def load_config():
    global response_config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                response_config = json.load(f)
            except json.JSONDecodeError:
                print("[ERROR] Failed to parse responses.json")
                response_config = {}
    else:
        response_config = {}

# Save Config
def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(response_config, f, indent=2)

# Match Incoming Requests
def match_request(path, method, req):
    if path in response_config and method in response_config[path]:
        rules = response_config[path][method]
        if not isinstance(rules, list):
            print(f"[ERROR] Rules for {method} {path} are not a list.")
            return jsonify({"error": "Invalid rule format"}), 500

        for rule in rules:
            if not isinstance(rule, dict):
                print(f"[WARN] Skipping malformed rule: {rule}")
                continue
            conditions = rule.get("match", {})
            matched = True
            for key, expected in conditions.items():
                if request.args.get(key) != expected:
                    matched = False
                    break
            if matched:
                delay = rule.get("delay")
                if delay:
                    time.sleep(float(delay))
                return jsonify(rule.get("response", {})), rule.get("status", 200)
    return jsonify({"error": "No matching rule"}), 404

# Config Endpoint
@app.route('/_config', methods=['POST'])
@requires_auth
def update_config():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            raise ValueError("Config must be a JSON object")

        # Validate format
        for path, methods in data.items():
            if not isinstance(methods, dict):
                raise ValueError(f"Methods for path '{path}' must be a dictionary.")
            for method, rules in methods.items():
                if not isinstance(rules, list):
                    raise ValueError(f"Rules for '{method} {path}' must be a list.")
                for rule in rules:
                    if not isinstance(rule, dict):
                        raise ValueError(f"Each rule must be a dict (got {type(rule)}).")

        with CONFIG_LOCK:
            response_config.update(data)
            save_config()
        return jsonify({"status": "Configuration updated"}), 200
    except Exception as e:
        print(f"[ERROR] Failed to update config: {e}")
        return jsonify({"error": "Failed to update config"}), 400

# Shutdown Endpoint
@app.route('/_shutdown', methods=['POST'])
@requires_auth
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        return jsonify({"error": "Shutdown not supported"}), 501
    shutdown_func()
    return jsonify({"status": "Server shutting down..."}), 200

# 📡 Catch-All Handler
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path):
    return match_request(f"/{path}", request.method, request)

# Start Server
if __name__ == '__main__':
    load_config()
    try:
        app.run(host='127.0.0.1', port=8000)
    except KeyboardInterrupt:
        print("Shutting down server...")
