---
title: "Architectural Explanation: Headless-Service Architecture"
created_at: 2026-09-17T12:21:08-04:00
updated_at: 2026-09-17T12:21:08-04:00
tags:
  - headless-service
  - architecture
  - backend
  - explanation
desc: Exploration of Headless-Service Architecture, daemonized background execution, and presentation-decoupled core operations
---

# Headless-Service Architecture

## 1. Definition and Rationale

A **Headless-Service Architecture** structures the system as a decoupled background service (a daemon, worker, or API server) that operates entirely without a built-in graphical user interface (GUI) or direct terminal presentation logic.

The core service manages state persistence, background orchestration, domain computations, and external integrations, exposing its capabilities purely through standardized network or Inter-Process Communication (IPC) interfaces.

```text
+-------------------------------------------------------------------------+
|                        Headless Core Service                            |
|                                                                         |
|  [ Ingestion Worker ]    [ Normalization Engine ]   [ SQLite Storage ]  |
|  [ Task Scheduler   ]    [ Artifact Generator   ]   [ Telemetry Logger] |
|                                                                         |
+------------------------------------+------------------------------------+
                                     │ (JSON / IPC / REST)
                                     ▼
           +-------------------------+-------------------------+
           │                         │                         │
     [ CLI Utility ]          [ Web Dashboard ]        [ Systemd / Cron ]
```

---

## 2. Key Architectural Characteristics

### 2.1 Process Boundary Isolation
The core domain logic executes in its own dedicated process lifecycle. Clients connect, execute operations, and disconnect without interrupting ongoing background tasks (such as long-running multi-board scrapes).

### 2.2 Asynchronous Job Orchestration
Instead of forcing client interfaces to block during heavy operations, the headless service adopts a task-based workflow:
1. Client submits a request (e.g., `POST /api/v1/scrapes`).
2. Service accepts the task, returns immediately with a `202 Accepted` and a `task_id`.
3. Service executes the job in an internal background queue.
4. Client polls status (`GET /api/v1/tasks/{id}`) or receives a notification upon completion.

### 2.3 Single-Process Resource Authority
By centralizing all database reads, writes, and file manipulations within a single running daemon, the system avoids concurrency hazards such as SQLite write-lock contention (`sqlite3.OperationalError: database is locked`) that occur when multiple independent CLI scripts access a database file concurrently.

---

## 3. Operational Advantages

* **Lifecycle Independence:** The service can run continuously as a systemd user unit (`job-searchd.service`), executing periodic scrapes on schedule regardless of whether a user terminal is open.
* **Pluggable Frontends:** Presentation layers can be swapped or added (terminal CLI, local React dashboard, system tray alerts) without restarting or altering the headless backend.
* **Security & Sandboxing:** The daemon can execute under dedicated user permissions with restricted filesystem access, while client tools simply talk over a secured local Unix Domain Socket (`/run/user/$UID/job-search.sock`).
