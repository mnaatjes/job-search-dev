---
title: "Architectural Explanation: API-First Design"
created_at: 2026-09-17T12:21:05-04:00
updated_at: 2026-09-17T12:21:05-04:00
tags:
  - api-first
  - architecture
  - design-patterns
  - explanation
desc: Conceptual foundation of API-First Design, contract-driven development, and interface-first software construction
---

# API-First Design

## 1. Conceptual Foundation

**API-First Design** is an architectural philosophy where the programmatic interface (the API contract) is treated as a first-class product and designed **before** writing implementation code or user interfaces.

Rather than building domain logic and retrofitting an API as an afterthought, API-First establishes explicit, machine-readable contracts (such as OpenAPI/JSON Schema) that dictate how external consumers interact with the system.

```text
Traditional Approach:
[ Application Logic / DB ] ──► [ Ad-hoc Scripts / Views ] ──► (Bolted-on API)

API-First Approach:
[ Formal Contract (OpenAPI / JSON Schema) ]
          │
          ├──► [ Application Core Implementation ]
          ├──► [ CLI Client / Terminal Tools ]
          └──► [ Web / Mobile / Daemon Consumers ]
```

---

## 2. Core Tenets

### 2.1 Contract as the Single Source of Truth
The API contract defines data types, request parameters, response structures, and error envelopes. Both client applications and backend services build against this contract concurrently, eliminating implicit assumptions.

### 2.2 Strict Schema Validation at Ingestion Boundaries
All data entering the system is validated against rigid schemas (e.g., Pydantic v2 models in Python) before reaching the application core. Malformed payloads fail immediately with standardized 4xx error responses.

### 2.3 Interface Stability & Versioning
Because the API serves multiple independent consumers, interface changes are deliberate, semantic, and backward-compatible. Breaking changes require explicit version negotiation (`/v1/`, `/v2/`).

---

## 3. Comparison: Code-First vs. API-First

| Dimension | Code-First / Script-Driven | API-First Design |
| :--- | :--- | :--- |
| **Primary Artifact** | Python functions, scripts, database tables | OpenAPI specification / JSON Schema |
| **Client Coupling** | Tight coupling to filesystem and runtime environment | Loose coupling over standardized transport protocols |
| **Extensibility** | Adding a web UI requires rewriting script logic | Any client consuming JSON can connect immediately |
| **Testing Boundary** | Subprocess CLI execution or monkeypatched scripts | Standardized HTTP/IPC request testing (`TestClient`) |

---

## 4. Relevance to Hexagonal Architecture

In Hexagonal (Ports & Adapters) architecture, API-First design formalizes the **Driving Port**:
* The API contract defines the port's inbound expectations.
* The API handler (e.g., FastAPI routing layer) acts as the **Driving Adapter**, translating incoming JSON into typed domain commands.
* The core application remains completely isolated from HTTP transport details.

---

## 5. Preserving API-First from Day 1 (Without an HTTP Server)

"API-First" does **not** require deploying a web framework or running an HTTP daemon on Day 1. Instead, it requires establishing contract boundaries first:

| Step | How API-First is Applied | Concrete Artifact |
| :--- | :--- | :--- |
| **Day 1: Design the Contract** | Define the input schema, output schema, and operation signature first. | `ScrapeRequest`, `ScrapeResponse` (Pydantic models), `JobListingSchema`. |
| **Day 2: Implement Against the Contract** | Write the core use case to accept only the contract DTO and return only the contract DTO. | `class ScrapeUseCase: def execute(self, req: ScrapeRequest) -> ScrapeResponse:` |
| **Day 3: Prototype via Script** | The script acts as the very first client consumer of that contract. | `scripts/run_scrape.py` constructs `ScrapeRequest` and feeds it to the Use Case. |

Because the Use Case logic is strictly bound to input/output DTOs (and never reaches out to global CLI args or script globals), the API contract already exists. Exposing it over HTTP later requires zero changes to the business logic.

### 5.1 The Two Approaches Compared

| Approach | How Scripts Communicate | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Approach A: In-Process Code API** *(Recommended for early development)* | Script imports Python class: `from job_search_dev.use_cases import ScrapeUseCase; result = ScrapeUseCase().execute(request)` | • Zero daemon/server setup required.<br>• Instant debugging with breakpoints.<br>• Ultra-fast unit/integration testing. | Doesn't test HTTP serialization/network layer directly. |
| **Approach B: Endpoint API via JSON** *(Thin-Client Model)* | Script makes HTTP request: `response = httpx.post("http://localhost:8000/api/scrapes", json={...})` | • 100% tests the real network API contract.<br>• Exact same code path as future web UI or CLI. | Requires running backend server daemon in background during development. |

### 5.2 The Ideal Strategy: Clean Two-Stage Evolution

```text
================================================================================
Stage 1: Early Development & Rapid Prototyping (In-Process Code API)
================================================================================
scripts/run_scrape.py  ──(Python import / Pydantic DTO)──►  Application Core (Use Case)

• Developer runs script directly: `python scripts/run_scrape.py`
• No background server needed.
• Scripts use Python domain models that mirror the future JSON structure.

================================================================================
Stage 2: API Integration & Production Thin-Client (HTTP/JSON Endpoints)
================================================================================
FastAPI Server         ──(Wraps)────────────────────────►  Application Core (Use Case)
                                                                   ▲
                                                                   │ (JSON over HTTP)
scripts/jobctl (CLI)   ────────────────────────────────────────────┘

• Dev scripts evolve into a unified thin CLI (`jobctl`) that speaks JSON to the server.
• Web dashboards, cron jobs, and CLIs all share the exact same HTTP/JSON contract.
```

---

## 6. The Inflection Point: When to Build Endpoints & Thin Clients

The transition from in-process scripts to HTTP/Socket endpoints and a Thin Client occurs when hitting any of these **4 architectural inflection triggers**:

```text
                               [ DEVELOPMENT TIMELINE ]
Phase 1: Inception & Discovery                   Phase 2: System Integration & Automation
--------------------------------------------     --------------------------------------------
• Exploring external job board scrapers          • Multiple interfaces needed (CLI + Web UI)
• Testing regexes & salary parsers               • Headless background daemons / Cron tasks
• Rapid iteration on domain models               • Concurrency / SQLite multi-process locking
• In-process scripts calling Python DTOs         • Need asynchronous task queue / polling
                                       ▲
                                       │
                              [ INFLECTION POINT ]
                       "Domain boundaries are stable;
                        cross-process orchestration begins."
```

### Trigger 1: Multiple Consumers Emerge
* **Symptom:** Both a CLI tool and a local web dashboard (or tray notifier) are required.
* **Action:** Expose the Use Cases via FastAPI so both clients consume identical JSON.

### Trigger 2: Asynchronous / Long-Running Tasks
* **Symptom:** Scraping multiple boards takes 60 seconds; terminal scripts block, preventing parallel workflow.
* **Action:** Move scraping into a background FastAPI/daemon queue where the thin CLI receives an instant `task_id` to poll status.

### Trigger 3: Concurrency & Database Lock Contention
* **Symptom:** A scheduled cron scrape runs concurrently with an ad-hoc CLI script, resulting in `sqlite3.OperationalError: database is locked`.
* **Action:** Transition all writes to a single persistent server process handling SQLite transactions sequentially.

### Trigger 4: Contract Stability Reached
* **Symptom:** Domain models (`JobPost`, `ApplicationEvent`, `ResumeVariant`) stabilize.
* **Action:** Generate the formal OpenAPI JSON specification from Pydantic schemas and deploy the HTTP routing layer.

---

## 7. End-to-End API-First Engineering Lifecycle

The full lifecycle progresses across four structured phases, moving from contract design to in-process dev scripts, then to HTTP/IPC endpoints, and finally to production thin clients:

```text
+---------------------------------------------------------------------------------------------------------+
|                                    API-FIRST DEVELOPMENT LIFECYCLE                                      |
+---------------------------------------------------------------------------------------------------------+
|  Phase 1: Contract Specification   │  Pydantic Schemas (DTOs), Method Signatures, Error Types           |
|  Phase 2: In-Process Prototyping   │  Application Core Use Cases + Standalone Dev Scripts (Python DTOs) |
|  Phase 3: Driving Adapter Exposure │  FastAPI/UDS Routes + Background Task Queue + OpenAPI JSON         |
|  Phase 4: Thin-Client Delivery     │  Unified CLI (`jobctl`), Web Dashboard, Systemd / Cron Integration |
+---------------------------------------------------------------------------------------------------------+
```

---

### Phase 1: Contract Specification (Day 1)
* **Objective:** Define explicit input, output, and domain boundaries before writing logic.
* **Actions:**
  1. Author Pydantic v2 schemas representing request payloads (e.g., `ScrapeRequest`, `TrackApplicationRequest`, `CompileResumeRequest`).
  2. Author Pydantic v2 schemas representing response payloads (e.g., `JobListingResponse`, `TaskStatusResponse`).
  3. Define abstract Use Case protocols/interfaces with strict type hints.
* **Primary Artifacts:** `src/job_search_dev/models/` schemas and type definitions.

---

### Phase 2: In-Process Prototyping & Developer Scripting
* **Objective:** Build and verify domain services and external adapters with zero server overhead.
* **Actions:**
  1. Implement concrete Use Cases (`src/job_search_dev/use_cases/`) accepting solely Phase 1 DTOs.
  2. Implement Driven Adapters (SQLite repositories, scraper clients, artifact file renderers).
  3. Write developer scripts (`scripts/run_scrape.py`, `scripts/manage_profile.py`) that instantiate Use Cases directly in-process.
  4. Write hermetic unit and integration tests using offline fixtures.
* **Developer Experience:** Instant iteration, standard breakpoints (`pdb`/IDE), zero background server setup.

---

### Phase 3: Driving Adapter Exposure (The API Layer)
* **Objective:** Expose the stabilized core over HTTP/Unix Domain Sockets and introduce asynchronous execution.
* **Actions:**
  1. Mount FastAPI router endpoints that map 1:1 to Phase 2 Use Cases:
     ```python
     @router.post("/api/v1/scrapes", response_model=TaskStatusResponse, status_code=202)
     def submit_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
         task_id = task_manager.enqueue(scrape_use_case.execute, req)
         return TaskStatusResponse(task_id=task_id, status="queued")
     ```
  2. Implement asynchronous worker queues for long-running batch scrapes or LaTeX compilations.
  3. Export automatically generated OpenAPI JSON (`/openapi.json`) and Swagger documentation (`/docs`).
  4. Write API endpoint tests using `fastapi.testclient.TestClient`.

---

### Phase 4: Production Thin-Client & System Automation
* **Objective:** Deliver unified, decoupled client tools and production daemon automation.
* **Actions:**
  1. Build a unified thin CLI client (`scripts/jobctl` or installed `jobctl` binary) that translates terminal flags into HTTP/IPC requests to the local API.
  2. Configure production background daemons (`systemd` user service or cron worker) calling local API endpoints via `curl` or client CLI.
  3. (Optional) Connect graphical interfaces (web dashboard, tray notifier) consuming the identical OpenAPI specification.
  4. Retain Phase 2 developer scripts as low-level diagnostic and benchmark utilities.
