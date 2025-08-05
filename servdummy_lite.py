import json, os, threading, ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CONFIG_PATH = "responses.json"
AUTH_HEADER = "Basic YWRtaW46ZHVzdDUxNA=="

response_config = {}
config_lock = threading.Lock()

def load_config():
    global response_config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                with config_lock:
                    response_config = json.load(f)
                    print("[INFO] Config loaded.")
            except Exception as e:
                print(f"[ERROR] Failed to load config: {e}")

class DustHandler(BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Dust514 Dummy"')
        self.end_headers()

    def check_auth(self):
        auth = self.headers.get("Authorization", "")
        return auth == AUTH_HEADER

    def do_GET(self): self.route("GET")
    def do_POST(self): self.route("POST")

    def route(self, method):
        path = urlparse(self.path).path
        if path == "/_config" and method == "POST":
            if not self.check_auth():
                self.do_AUTHHEAD()
                self.wfile.write(b"Authentication required")
                return
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                new_config = json.loads(body)
                if not isinstance(new_config, dict): raise ValueError("Expected dict")
                with config_lock:
                    response_config.clear()
                    response_config.update(new_config)
                with open(CONFIG_PATH, "w") as f:
                    json.dump(response_config, f, indent=2)
                self.send_response(200); self.end_headers()
                self.wfile.write(b"Config updated.")
            except Exception as e:
                self.send_response(400); self.end_headers()
                self.wfile.write(f"Invalid config: {e}".encode())
            return

        self.match_request(method, path)

    def match_request(self, method, path):
        key = f"{method} {path}"
        rules = response_config.get(key)
        if not rules:
            self.send_response(404); self.end_headers()
            self.wfile.write(b"No matching rule."); return
        length = int(self.headers.get('Content-Length', 0))
        try: body = self.rfile.read(length); body_json = json.loads(body)
        except: body_json = {}
        query = parse_qs(urlparse(self.path).query)
        for rule in rules:
            match = rule.get("match", {})
            found = all(
                match.get(k) in (query.get(k, [None])[0], body_json.get(k))
                for k in match
            )
            if found:
                delay = rule.get("delay", 0)
                if delay: import time; time.sleep(delay)
                status = rule.get("status", 200)
                payload = json.dumps(rule.get("response", {})).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
                return
        self.send_response(404); self.end_headers()
        self.wfile.write(b"No matching rule.")

    def log_message(self, *args): return

def run_server(port, use_ssl=False):
    httpd = HTTPServer(('0.0.0.0', port), DustHandler)
    if use_ssl:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile="server.pem", server_side=True)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f" Dummy server running on port {port} {'(HTTPS)' if use_ssl else '(HTTP)'}")

if __name__ == "__main__":
    load_config()
    run_server(80)
    run_server(443, use_ssl=True)
    run_server(59224)
    run_server(59233)
    print(" All Dust ports bound. Ctrl+C to exit.")
    try:
        while True: pass
    except KeyboardInterrupt:
        print("\n[!] Server stopped.")
