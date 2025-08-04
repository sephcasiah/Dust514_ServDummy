# Dust514_ServDummy

## Test Plan

## Objective

Validate the behavior, stability, and configurability of the `Dust514_ServDummy` fake server used to simulate Dust 514’s defunct backend.

---

## Test Environment

* **OS**: Windows 10/11
* **Python Version**: 3.10+
* **RPCS3 Version**: Latest stable
* **Client**: Dust 514 (Version 3.0.0 Beta) (via RPCS3)
* **Network**: Localhost or LAN

---

##  Test Categories

### 1. Basic Endpoint Response Tests

| Test | Description                                   | Expected Result              |
| ---- | --------------------------------------------- | ---------------------------- |
| 1.1  | Start server, GET to `/ping`                  | 200 OK with default response |
| 1.2  | POST to known endpoint with no matching rules | Returns default response     |
| 1.3  | GET/POST to unknown endpoint                  | 404 Not Found                |

---

### 2. Dynamic Configuration Tests

| Test | Description                        | Expected Result                    |
| ---- | ---------------------------------- | ---------------------------------- |
| 2.1  | Update response via `/config`      | Subsequent requests reflect change |
| 2.2  | Add matching rule with query param | Response matches correctly         |
| 2.3  | Add rule for JSON body match       | Matches body and returns response  |
| 2.4  | Remove config entry                | Endpoint reverts to default or 404 |
| 2.5  | Submit invalid config              | 400 Bad Request                    |

---

### 3. Auth and Access Tests

| Test | Description                   | Expected Result           |
| ---- | ----------------------------- | ------------------------- |
| 3.1  | Access `/config` without auth | 401 Unauthorized          |
| 3.2  | Wrong auth to `/shutdown`     | 401 Unauthorized          |
| 3.3  | Correct auth to `/shutdown`   | Server shuts down cleanly |

---

### 4. Concurrency & Threading

| Test | Description                    | Expected Result                |
| ---- | ------------------------------ | ------------------------------ |
| 4.1  | Simulate 10+ parallel requests | No crash or race condition     |
| 4.2  | Modify config while serving    | Consistent behavior            |
| 4.3  | Observe logging under load     | Output is readable and ordered |

---

### 5. Advanced Response Features

| Test | Description             | Expected Result                |
| ---- | ----------------------- | ------------------------------ |
| 5.1  | Add simulated delay     | Response delayed correctly     |
| 5.2  | Simulate HTTP 500, 403  | Game handles errors gracefully |
| 5.3  | Send large JSON payload | Full payload delivered         |

---

### 6. Dashboard & UI Tests

| Test | Description                 | Expected Result                 |
| ---- | --------------------------- | ------------------------------- |
| 6.1  | Open dashboard              | Dashboard loads successfully    |
| 6.2  | Modify config via dashboard | Changes take effect and persist |
| 6.3  | Shutdown from UI            | Server stops gracefully         |

---

### 7. 🔌 RPCS3 Integration Tests

| Test | Description                   | Expected Result                 |
| ---- | ----------------------------- | ------------------------------- |
| 7.1  | Dust 514 initiates connection | Server receives requests        |
| 7.2  | Game reaches main menu        | Mocked responses permit startup |
| 7.3  | Simulate server error         | Game retries or logs cleanly    |

---

## Post-Test Checklist

* Verify `responses.json` updates properly.
* Review logs for consistency.
* Ensure no hanging server threads.
* Optional: run performance profiling.

---

## Optional Enhancements

* Automate using a Python harness (see test harness script)
* Add CI testing with mock clients
* Include full request/response payload validation

---

*End of Test Plan*
