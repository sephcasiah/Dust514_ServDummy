# Dust514_ServDummy Test Plan (v2)

## Objective
Validate the behavior, stability, configurability, and integration of the `Dust514_ServDummy` fake server used to simulate Dust 514’s defunct backend, including support for HTTPS, TLS certificates, and RPCS3 compatibility.

---

## Progress Summary
- ✔️ Created `Dust514_ServDummy` Flask-based mock server.
- ✔️ Implemented dynamic configuration via `/config` with basic auth (`admin:dust514`).
- ✔️ Implemented mock response matching and custom JSON rules via `responses.json`.
- ✔️ Developed test harness to automate server validation.
- ✔️ Enabled HTTPS with self-signed certs (cert.pem + key.pem).
- ✔️ Integrated with RPCS3 via IP swap list in `config.yml`.
- ❗ Game does not yet successfully call server endpoints — likely TLS port binding / trust issues.

---

## Test Environment
- **OS**: Windows 10/11
- **Python Version**: 3.13
- **RPCS3 Version**: Latest stable
- **Client**: Dust 514 (via RPCS3)
- **Server Port**: HTTPS (443)
- **TLS**: Self-signed cert

---

## Test Categories

### 1. Basic Endpoint Response Tests
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 1.1 | Start server, GET to `/ping` | 200 OK with `{"message":"pong!"}` |
| 1.2 | POST to unknown endpoint | 404 Not Found |
| 1.3 | GET to endpoint with no config | 404 Not Found |

### 2. TLS & HTTPS Support
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 2.1 | Server binds to port 443 with TLS | Flask logs HTTPS startup |
| 2.2 | Test self-signed cert validity | Client accepts cert without crash |
| 2.3 | Re-map port using `netsh` (443→8443) | Server accessible via 443 |

### 3. Dynamic Configuration Tests
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 3.1 | Load config from `responses.json` | Server registers config |
| 3.2 | POST valid config to `/config` | Config updated, 200 OK |
| 3.3 | POST invalid config | 400 Bad Request |
| 3.4 | Load config before startup | Loads into memory |

### 4. Authentication Handling
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 4.1 | Access `/config` without auth | 401 Unauthorized |
| 4.2 | Correct credentials | 200 OK |
| 4.3 | Incorrect credentials | 401 Unauthorized |

### 5. File Serving & Caching
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 5.1 | Game requests cached HTTP file | Server logs request |
| 5.2 | Serve valid `IMPORTANTMESSAGE.TXT.JSON` | Game accepts response (no crash) |
| 5.3 | Request unknown file | Server returns 404 |

### 6. RPCS3 Integration Tests
| Test | Description | Expected Result |
|------|-------------|-----------------|
| 6.1 | Add Dust 514 hosts to `config.yml` | Resolved to 127.0.0.1 |
| 6.2 | Game initiates request to HTTPS server | Server logs connection |
| 6.3 | Observe RPCS3 TLS errors | Identify handshake or trust issues |

---

## Diagnostics Checklist
- Confirm server is listening on port 443: `netstat -ano | findstr :443`
- Validate certs exist and are not expired
- Use `curl -k https://localhost/ping` to verify HTTPS locally
- Use Wireshark to capture game traffic and verify host resolution

---

## Post-Test Checklist
- Confirm server logs received RPCS3 requests
- Validate working endpoints with test harness
- Ensure game client makes HTTPS requests to expected domains
- Test with patched or unpatched TLS trust

---

## Optional Enhancements
- TLS certificate authority trust patching (for PS3 certs)
- Add HTTP/2 or redirection support
- Fallback to HTTP on untrusted TLS detection
- Use `nginx` or `mitmproxy` as reverse proxy for more control

---

*End of Test Plan v2*
