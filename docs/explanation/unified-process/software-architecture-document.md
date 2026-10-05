---
title: "Software Architecture Document: Attributed Lead Generation and Conversion Analytics Platform"
created_at: 2026-09-17T01:36:43-04:00
updated_at: 2026-09-17T01:36:43-04:00
tags:
  - unified-process
  - elaboration
  - architecture
  - sad
  - explanation
desc: Software Architecture Document outlining Hexagonal layers, component interactions, and data models
---

# Software Architecture Document (SAD)

## 1. Architectural Representation

The system is structured according to the **Ports & Adapters (Hexagonal Architecture)** design pattern to decouple volatile external dependencies (scraping engines, storage engines, CLI/API interfaces) from core domain entities and business rules.

```text
       [ Driving Ports / Adapters ]                             [ Driven Ports / Adapters ]
+---------------------------------------+                         +---------------------------+
| - Production Thin Client (`jobctl`)   |                         | - JobSpy / TLS Scraper    |
| - Standalone Dev Scripts (Phase 2)    |                         | - Raw Storage (data/raw)  |
| - Local API Server (FastAPI / UDS)    |                         | - SQLite DB (processed)   |
| - Cron / Systemd Scheduler (HTTP/CLI) |                         | - Artifact FS (data/out)  |
+-------------------+-------------------+                         +-------------+-------------+
                    │                                                           │
                    v                                                           v
+-------------------+-----------------------------------------------------------+-------------+
|                                        APPLICATION CORE                                     |
|  +---------------------------------------------------------------------------------------+  |
|  | Use Cases (Inbound Ports): ScrapeUseCase, TrackAppUseCase, CompileResumeUseCase       |  |
|  | Domain Entities:           JobPost, QueryProfile, ResumeVariant, FollowUpTask        |  |
|  | Domain Services:           Normalization, AttributionTracker, NotificationEngine      |  |
|  +---------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------+
```

## 2. Layer Definitions

1. **Ingestion & Scraper Adapters (Driven Adapter / Extract):**
   * Invoked via Core Use Cases.
   * Parameterizes and invokes `JobSpy` scraping modules concurrently.
   * Emits immutable JSONL files to `data/raw/<site>/YYYY-MM-DD/`.
2. **Transformation & Normalization (Core Service / Transform):**
   * Parses raw JSONL records into domain models.
   * Computes SHA256 composite deduplication keys (`company:title:location`).
   * Normalizes salary frequencies to annual USD values.
3. **Artifact Compilation & Profile Layer (Core Service / Generate):**
   * Reads structured candidate profile models (skills, experience, project blocks).
   * Aligns posting requirements against profile nodes to assemble tailored Markdown/PDF/LaTeX artifacts.
   * Tracks artifact versions and keyword relevance scores in `resume_variants`.
4. **Lifecycle & Notification Layer (Core Service / Orchestrate):**
   * Manages Human-in-the-Loop application transitions (`Staged` $\rightarrow$ `Applying` $\rightarrow$ `Applied` $\rightarrow$ ...).
   * Generates and evaluates follow-up notification rules ($T+7$ inquiry, $T+1$ interview note) stored in `follow_up_tasks`.
5. **Persistence Layer (Driven Port / Load):**
   * Stores relational entities in SQLite (`data/processed/jobs.db`) under WAL mode.
   * Implements tables: `query_profiles`, `job_listings`, `candidate_profiles`, `resume_variants`, `applications`, `application_events`, `follow_up_tasks`, and `scrape_telemetry`.
6. **Driving Adapter & API Layer (Driving Adapter / Transport):**
   * Mounts FastAPI router endpoints on local Unix Domain Sockets or HTTP ports.
   * Translates incoming JSON into typed Pydantic DTOs and forwards them to Core Use Cases.
   * Coordinates background execution queues and returns immediate task status IDs.
7. **Presentation & Thin Clients (Driving Client / Presentation):**
   * Standalone Dev Scripts (Phase 2 in-process prototypes) and Production Thin CLI (`jobctl` in Phase 4) rendering rich terminal views and CSV exports.

## 3. Data Flow Architecture

```text
External Job Boards
        │ (TLS Scrape Payload)
        ▼
data/raw/<site>/YYYY-MM-DD/ (Immutable JSONL)
        │
        ▼
Transformation & Normalization Service
        │ (Normalized Schema + Composite Hash)
        ▼
SQLite Database (data/processed/jobs.db)
        │
        ├──► Artifact Compilation Engine (Profile Repositories) ──► data/artifacts/resumes/
        │                                                                   │
        ├──► HITL Application Tracker & Follow-Up Scheduler ◄───────────────┘
        │
        ▼
Core Use Cases (Inbound Ports)
        ▲
        │ (DTO / Internal Calls in Phase 2)
        ├── Standalone Dev Scripts (scripts/run_scrape.py, etc.)
        │
        │ (JSON over HTTP/UDS in Phase 3 & 4)
        └── FastAPI Driving Adapter ◄── Production Thin CLI (`jobctl`) / Cron / Web UI
```

## 4. Implementation View (Directory Layout)

The physical directory tree maps directly to the Hexagonal layers and API-First lifecycle:

```text
job-search-dev/
├── data/                                # Driven Port: File-backed persistence
│   ├── raw/                             # Immutable partitioned JSONL scrapes
│   │   └── <source>/YYYY-MM-DD/*.jsonl
│   ├── processed/                       # Relational database (SQLite WAL)
│   │   └── jobs.db
│   ├── artifacts/                       # Generated resumes & cover letters
│   │   └── resumes/YYYY-MM-DD/*.pdf
│   └── reports/                         # Conversion analytics & variance outputs
│       └── exports/*.csv
├── docs/                                # Diátaxis documentation framework
│   ├── tutorials/                       # Learning-oriented walkthroughs
│   ├── how-to/                          # Operational procedural recipes
│   ├── reference/                       # Authoritative specs & UP registers
│   │   └── unified-process/             # Use cases, risk lists, test plans
│   └── explanation/                     # Architectural design & rationale
│       └── unified-process/             # Vision, SAD, ADRs
├── scripts/                             # Presentation & Driving Tools
│   ├── jobctl                           # Production Thin CLI (Phase 4 HTTP/IPC client)
│   ├── run_scrape.py                    # Phase 2 In-Process Scraper Prototyping Script
│   ├── manage_profile.py                # Phase 2 In-Process Profile Manager Script
│   ├── generate_artifacts.py            # Phase 2 In-Process Resume Compiler Script
│   ├── track_application.py             # Phase 2 In-Process Application Tracker Script
│   └── dispatch_notifications.py        # Phase 2 In-Process Follow-up Dispatcher Script
├── src/                                 # Application Core, Adapters & Services
│   └── job_search_dev/
│       ├── __init__.py
│       ├── __main__.py                  # Direct module execution entry point (`python -m`)
│       ├── cli.py                       # Installed console script entry point (`jobctl`)
│       ├── config.py                    # Twelve-Factor runtime settings (`pydantic-settings`)
│       ├── models/                      # Domain Entities & Contract DTOs (Phase 1)
│       │   ├── __init__.py
│       │   ├── job_post.py              # Canonical job posting models
│       │   ├── query_profile.py         # Search query parameter schemas
│       │   ├── profile_repo.py          # Candidate skills & history models
│       │   ├── application.py           # HITL funnel states & event models
│       │   └── tasks.py                 # Follow-up task schemas
│       ├── use_cases/                   # Inbound Core Ports (Phase 2)
│       │   ├── __init__.py
│       │   ├── scrape.py                # Scrape execution interactor
│       │   ├── tracking.py              # Application lifecycle interactor
│       │   ├── artifacts.py             # Resume compilation interactor
│       │   └── analytics.py             # Attribution calculation interactor
│       ├── api/                         # Driving Adapters: FastAPI Endpoints (Phase 3)
│       │   ├── __init__.py
│       │   ├── server.py                # FastAPI app initialization & UDS mount
│       │   ├── queue.py                 # Asynchronous background task manager
│       │   └── routes/                  # REST route handlers delegating to use cases
│       │       ├── scrapes.py
│       │       ├── applications.py
│       │       ├── artifacts.py
│       │       └── reports.py
│       ├── scrapers/                    # Driven Adapters: External job board clients
│       │   ├── __init__.py
│       │   └── jobspy_adapter.py        # TLS-impersonating JobSpy wrapper
│       ├── normalizers/                 # Core Service: Data cleansing & deduplication
│       │   ├── __init__.py
│       │   ├── deduplication.py         # SHA256 composite hashing
│       │   └── salary.py                # Frequency & currency normalizer
│       ├── generators/                  # Core Service: Artifact compiler
│       │   ├── __init__.py
│       │   ├── alignment.py             # Requirement-to-skill matcher
│       │   └── renderer.py              # Markdown/LaTeX/PDF template engines
│       ├── tracking/                    # Core Service: HITL & Follow-ups
│       │   ├── __init__.py
│       │   ├── lifecycle.py             # Funnel state machine
│       │   └── scheduler.py             # Follow-up reminder evaluation
│       ├── analytics/                   # Core Service: Conversion & variance telemetry
│       │   ├── __init__.py
│       │   └── attribution.py           # Multi-variant yield calculations
│       └── storage.py                   # Driven Adapter: SQLite & path utilities
└── tests/                               # Verification & Hermetic Fixtures
    ├── fixtures/                        # Static offline response payloads
    ├── unit/                            # Component-level unit test suites
    ├── api/                             # FastAPI TestClient endpoint test suites
    └── integration/                     # Pipeline integration test suites
```

## 5. Multi-Pipeline Architecture & Medallion Storage Pattern

The data engineering pipeline follows a **Medallion Data Architecture** across all ingested data streams (job board scrapes, email application responses, webhooks):

```text
+───────────────────────────────────────────────────────────────────────────────────+
|                               MEDALLION DATA TIERS                                |
+───────────────────────────────────────────────────────────────────────────────────+
| Bronze Tier (Raw Ingestion)       │ Immutable JSONL files partitioned by stream,  |
|                                   │ source, and UTC date (`data/raw/<pipeline>/`) |
| Silver Tier (Cleansed & Dedupe)   │ Normalized, validated, deduplicated records   |
|                                   │ in SQLite relational tables (`jobs.db`)       |
| Gold Tier (Attributed Analytics)  │ Aggregated conversion metrics, ROI yield, and |
|                                   │ variance reports (`data/reports/exports/`)    |
+───────────────────────────────────────────────────────────────────────────────────+
```

### 5.1 Multi-Pipeline Channel Abstraction
The system supports multiple independent ingestion pipelines sharing the unified core:
1. **Job Listing Pipeline:** Scrapes external boards (`JobSpy`, direct HTTP) $\rightarrow$ `data/raw/jobs/<source>/YYYY-MM-DD/`.
2. **Inbound Response Pipeline:** Pulls applicant emails (IMAP) / webhooks $\rightarrow$ `data/raw/inbound_responses/YYYY-MM-DD/`.
3. **Attribution & Telemetry Pipeline:** Aggregates event logs $\rightarrow$ `data/raw/telemetry/YYYY-MM-DD/`.

### 5.2 Scraper Port Abstraction & The Tolerant Reader Pattern
Third-party scraping libraries (e.g. `python-jobspy`) are treated as volatile external dependencies and **must never leak into application core logic**:
* **Port Interface:** All scrapers implement `JobScraperPort.scrape(query: QueryProfile) -> List[RawJobPayload]`.
* **Tolerant Ingestion Schema:** Ingestion adapters utilize flexible Pydantic models with extra-field tolerance (`extra="ignore"`) and `AliasChoices` to absorb minor upstream naming shifts without raising unhandled exceptions.
* **Strict Domain Validation:** The Application Core validates normalized data against canonical `JobPost` schemas. Malformed or unrecoverable records are isolated to `data/quarantine/` with structured warning logs to prevent dataset poisoning (`RSK-12`).
* **Canary Upgrade Gating:** Dependency updates on scrapers are strictly gated behind offline regression fixtures and live canary tests (`UC-09` / `RSK-14`) prior to updating production requirements.

---

## 6. Logging, Telemetry & Audit Taxonomy

System events are segregated into four distinct logging streams:

1. **Development & Debug Logs (`data/logs/debug.log`):** Human-readable diagnostic output, traceback details, and scraper DOM extraction warnings.
2. **Operational Telemetry (`data/logs/telemetry.jsonl`):** Structured JSON metrics capturing execution latency, HTTP response status codes, proxy health, and deduplication yield.
3. **Audit & Historical Trail (`application_events` table):** Immutable, timestamped state transition logs capturing candidate actions (`Staged`, `Applied`, `Screening`).
4. **Attribution & ROI Telemetry (`data/reports/`):** High-level performance indicators (conversion yield by search term, resume variant efficiency, application duration).

---

## 7. Continuous Integration (CI/CD) & Quality Architecture

Code quality and release stability are enforced through a layered pipeline:

```text
[ Developer Commit ] ──► [ Pre-Commit Hooks ] ──► [ GitHub Actions CI ] ──► [ Release / PR Gate ]
                           • Black formatter        • Python 3.12 runner
                           • Flake8 linter          • Gitleaks secret scan
                           • YAML / JSON checks     • Hermetic Pytest (>=85% cov)
                           • Gitleaks scan          • Zero live network calls
```

1. **Pre-Commit Enforcement (`.pre-commit-config.yaml`):** Runs locally before commit creation to standardize code styling (PEP 8, Black, trailing whitespace) and intercept accidental secret leaks (`RSK-15`).
2. **Hermetic CI Execution (`.github/workflows/ci.yml`):** Rebuilds the environment from scratch, runs linting checks, executes the test suite strictly against static mock fixtures (`tests/fixtures/`), and enforces the 85% total code coverage threshold.
3. **Secret Isolation (Twelve-Factor Factor III):** All local runtime settings and API credentials are kept in `.env` (gitignored). CI runners use simulated environment variables.

---

## 8. Architectural Baseline & Validation

The architectural prototype was validated via `scripts/run_scrape.py` and `tests/test_basic.py`, proving:
* Unauthenticated TLS scraping across LinkedIn and Indeed.
* Immutable JSONL partitioning adhering to ADR 0001.
* Pydantic v2 domain schema enforcement, artifact compilation isolation, and SQLite storage compatibility.
