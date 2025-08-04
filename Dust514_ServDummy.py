import os
import json
import threading
from flask import Flask, request, jsonify, abort, make_response
from functools import wraps
from base64 import b64decode

app = Flask(__name__)
CONFIG_PATH = "responses.json"
USERNAME = "admin"
PASSWORD = "dust514"
AUTH_HEADER = f"Basic {os.environ.get('AUTH', 'YWRtaW46ZHVzdDUxNA==')}"

response_config = {}
config_lock = threading.Lock()


def load_config():
    global response_config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                with config_lock:
                    response_config = data
            except Exception as e:
                print(f"[ERROR] Failed to load config: {e}")


def save_config():
    with config_lock:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(response_config, f, indent=2)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        print(f"[DEBUG] Auth received: {auth}")
        if auth != AUTH_HEADER:
            return make_response(jsonify({"error": "Authentication required."}), 401)
        return f(*args, **kwargs)
    return decorated


def match_request(path, method, req):
    rules = response_config.get(f"{method} {path}")
    if not rules:
        return make_response(jsonify({"error": "No matching rule"}), 404)

    if not isinstance(rules, list):
        print(f"[ERROR] Invalid rule format for {method} {path}")
        return make_response(jsonify({"error": "Invalid rule format"}), 500)

    for rule in rules:
        conditions = rule.get("match", {})
        query_params = req.args.to_dict()
        form_params = req.form.to_dict()
        body_json = {}
        try:
            if req.is_json:
                body_json = req.get_json()
        except Exception:
            pass

        match_found = True
        for k, v in conditions.items():
            if query_params.get(k) != v and form_params.get(k) != v and body_json.get(k) != v:
                match_found = False
                break
        if match_found:
            delay = rule.get("delay", 0)
            if delay:
                import time
                time.sleep(delay)
            return jsonify(rule.get("response", {})), rule.get("status", 200)

    return make_response(jsonify({"error": "No matching rule"}), 404)


@app.route("/_config", methods=["POST"])
@requires_auth
def update_config():
    try:
        new_config = request.get_json()
        if not isinstance(new_config, dict):
            raise ValueError("Config must be a dictionary")
        # Validate that each key maps to a list of rules
        for k, v in new_config.items():
            if not isinstance(v, list):
                raise ValueError(f"Rules for '{k}' must be a list.")
        with config_lock:
            response_config.clear()
            response_config.update(new_config)
        save_config()
        return jsonify({"status": "Configuration updated"})
    except Exception as e:
        print(f"[ERROR] Failed to update config: {e}")
        return make_response(jsonify({"error": "Failed to update config"}), 400)


@app.route("/_shutdown", methods=["POST"])
@requires_auth
def shutdown():
    return make_response(jsonify({"error": "Shutdown not supported"}), 501)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def handle_request(path):
    return match_request(f"/{path}", request.method, request)


if __name__ == "__main__":
    load_config()
    print("✅ Dust514_ServDummy running on port 80...")
    app.run(host="0.0.0.0", port=80)
