---
title: "Architectural Explanation: Client-Server Architecture with Thin Clients"
created_at: 2026-09-17T12:21:13-04:00
updated_at: 2026-09-17T12:21:13-04:00
tags:
  - client-server
  - thin-client
  - cli
  - architecture
  - explanation
desc: Architectural mechanics of the Thin-Client pattern, CLI-as-API-consumer design, and Hexagonal Driving Adapter mapping
---

# Client-Server Architecture with Thin Clients

## 1. Architectural Overview

In a **Client-Server Architecture with Thin Clients**, application responsibilities are strictly partitioned between a lightweight presentation client and a feature-complete application server.

A **Thin Client** contains minimal business logic. Its primary functions are:
1. Collecting input from the user (CLI arguments, stdin, flags).
2. Serializing user input into structured JSON requests.
3. Transmitting payloads over transport channels (HTTP REST, Unix Domain Sockets).
4. Deserializing server responses and rendering human-readable outputs (tables, colors, exit codes).

```text
[ Developer / Terminal ]
         │
         ▼
+─────────────────────────────────────────+
|               Thin CLI                  |
|  1. Parse Flags (--term, --limit)       |
|  2. Build JSON Payload                  |
|  3. Transmit to IPC / HTTP Socket       |
|  4. Pretty-Print JSON Response          |
+────────────────────┬────────────────────+
                     │ (JSON over HTTP / Unix Socket)
                     ▼
+─────────────────────────────────────────+
|           Application Server            |
|  1. Validate Schema (Pydantic / OpenAPI)|
|  2. Invoke Domain Services / Use Cases  |
|  3. Execute Storage / Scraping / Tasks  |
|  4. Return Status JSON & Telemetry      |
+─────────────────────────────────────────+
```

---

## 2. Fat Client (Script) vs. Thin Client (API Consumer)

| Dimension | Fat CLI / Standalone Scripts | Thin CLI (API Consumer) |
| :--- | :--- | :--- |
| **Logic Location** | Business logic embedded directly in CLI scripts | Business logic encapsulated in application core |
| **Database Access** | Direct SQLite file connection per script run | Mediated exclusively by server process |
| **Concurrency** | Prone to file locking issues across parallel runs | Managed safely by central server transaction loop |
| **Portability** | Requires full runtime dependencies on every client | Client only requires a lightweight HTTP/IPC client |
| **Interface Consistency** | CLI and Web interfaces duplicate domain rules | All interfaces share identical server validation rules |

---

## 3. Communication Transports for Local CLI Applications

Local-first systems typically leverage two transport mechanisms for thin client communication:

### 3.1 Unix Domain Sockets (UDS)
* **Transport:** `/run/user/<UID>/job-search.sock` or `~/.local/share/job-search/daemon.sock`
* **Characteristics:** Fast, bypasses network stack overhead, naturally secured via POSIX filesystem permissions (no open TCP ports).

### 3.2 Localhost HTTP / REST (FastAPI)
* **Transport:** `http://127.0.0.1:8000`
* **Characteristics:** Easy to debug using standard tools (`curl`, Postman), easily accessible by browser frontends and webhooks.

---

## 4. Hexagonal Architecture Mapping

Under Ports & Adapters, the thin client model creates a clean separation of driving concerns:

* **Driving Port:** Abstract application interfaces defining use cases (e.g., `JobSearchService`, `ApplicationTrackingService`).
* **Driving Adapter (Server Side):** HTTP router / IPC endpoint handler that receives JSON, validates input, and delegates to the Driving Port.
* **External Actor (Client Side):** The thin CLI executable, which acts purely as an outside caller to the driving adapter.
