import json, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CONFIG_PATH = "responses.json"
response_config = {}
lock = threading.Lock()

def load_config():
    global response_config
    try:
        with open(CONFIG_PATH, "r") as f:
            with lock:
                response_config = json.load(f)
                print("[INFO] Loaded response config.")
    except Exception as e:
        print(f"[ERROR] Config load failed: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.respond("GET")
    def do_POST(self): self.respond("POST")
    def respond(self, method):
        path = urlparse(self.path).path
        key = f"{method} {path}"
        rules = response_config.get(key, [])
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b""
        try: body_json = json.loads(body.decode())
        except: body_json = {}
        params = parse_qs(urlparse(self.path).query)
        for rule in rules:
            cond = rule.get("match", {})
            if all(str(cond[k]) == str(params.get(k, [None])[0]) or str(body_json.get(k)) == str(cond[k]) for k in cond):
                delay = rule.get("delay", 0)
                if delay: import time; time.sleep(delay)
                self.send_response(rule.get("status", 200))
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(rule.get("response", {})).encode())
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"No matching rule.")
    def log_message(self, *args): return

def run_on_port(port):
    server = HTTPServer(("0.0.0.0", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"✅ Listening on port {port}")

if __name__ == "__main__":
    load_config()
    run_on_port(59224)
    run_on_port(59233)
    run_on_port(443)  # optional HTTP interface
    run_on_port(80)
    print("🟢 Dust514 Dummy Server running. Press Ctrl+C to stop.")
    try: input();  # keep running
    except KeyboardInterrupt: pass
