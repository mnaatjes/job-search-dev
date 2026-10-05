---
title: "Risk Management Register: Attributed Lead Generation and Conversion Analytics Platform"
created_at: 2026-09-17T01:36:43-04:00
updated_at: 2026-09-17T01:36:43-04:00
tags:
  - unified-process
  - inception
  - risks
  - reference
desc: Risk register tracking technical, operational, and external risks with severity and mitigations
---

# Risk Management Register

## 1. Risk Matrix Overview

| Risk ID | Category | Risk Description | Impact | Probability | Status | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RSK-01` | Technical | Third-party job board DOM / API schema changes break parsers | High | High | Active | Implement hermetic test fixtures and modular scraper extractors; track upstream JobSpy hotfixes. |
| `RSK-02` | Operational | Aggressive HTTP 429 rate limiting and temporary IP bans | High | Medium | Active | Enforce minimum request intervals, batch limits ($\le 25$ per board), and optional SOCKS5/HTTP proxy rotation. |
| `RSK-03` | Data Quality | Cross-board duplicate postings inflate listing volumes | Medium | High | Mitigated | Apply SHA256 composite hashing (`company:title:location`) during ELT deduplication stage. |
| `RSK-04` | Data Quality | LinkedIn unauthenticated search returns out-of-country positions | Medium | Medium | Active | Inject explicit country and ISO currency validation filters during normalization. |
| `RSK-05` | Storage | Raw JSONL storage accumulation creates disk bloat | Low | Medium | Active | Isolate data in gitignored `data/raw/` directories and implement automated 30-day gzip compression. |
| `RSK-06` | Generation | Automated resume tailoring produces hallucinated or mismatched skills | High | Medium | Active | Restrict generator selection strictly to validated profile repository nodes; require human verification before submission. |
| `RSK-07` | Operational | Follow-up notification misses due to scheduler dormancy | Medium | Medium | Active | Persist follow-up states in database with catch-up logic executed on every CLI runner startup. |
| `RSK-08` | Data Quality | Incomplete HITL attribution logging skews conversion telemetry | Medium | High | Active | Enforce mandatory variant linkage and status transition validations in CLI/API entry points. |
| `RSK-09` | Technical | In-process DTO models desynchronize from API JSON schemas | Medium | Low | Active | Maintain single-source-of-truth Pydantic models in `src/job_search_dev/models/` reused directly in FastAPI routers. |
| `RSK-10` | Operational | Unix domain socket permission or stale socket file locks block thin clients | Low | Medium | Active | Implement clean socket unlinking on daemon startup and restrict socket permissions to current UID (`0600`). |
| `RSK-11` | Technical | Scraper library drift or breaking updates desynchronize adapter outputs | High | High | Active | Abstract scrapers behind a formal `JobScraperPort`; isolate library upgrades behind hermetic integration tests. |
| `RSK-12` | Data Quality | Broken or corrupted scraper outputs silently poison persistent database | High | Medium | Active | Enforce strict Pydantic validation before database loading; discard malformed entries to quarantine files. |
| `RSK-13` | Operational | Stale, closed, or expired job postings waste candidate review time | Medium | High | Active | Implement automated staleness decay scoring (30-day archive thresholds) and last-seen timestamp refreshes. |
| `RSK-14` | Operational | Unattended scraper dependency upgrades introduce silent parsing regressions | High | Medium | Active | Enforce gated HITL upgrade workflow with canary integration tests before production deployment. |
| `RSK-15` | Security | Accidental credential, private key, or `.env` secret commit to repository | High | Low | Active | Configure pre-commit hooks, `.gitignore` rules, and automated `gitleaks` scans in CI. |
| `RSK-16` | Verification | Stale or unrepresentative mock fixtures pass CI while production scrapers fail | Medium | Medium | Active | Implement automated fixture recorder (`scripts/capture_fixtures.py`) to refresh offline JSON payloads on upgrades. |
| `RSK-17` | Operational | Dependency drift and environment bloat between development and production | Medium | Low | Active | Enforce `pyproject.toml` as single source of truth; separate `[project.dependencies]` from `[project.optional-dependencies].dev`. |
| `RSK-18` | Security | Runtime configuration secrets (`.env`) packaged into distribution wheels | High | Low | Active | Decouple build metadata (`pyproject.toml`) from runtime config; resolve `.env` dynamically via `pydantic-settings`. |

---

## 2. Risk Detail & Mitigations

### RSK-01: Upstream Scraper Breakage
* **Root Cause:** External job boards frequently alter HTML classes, JavaScript bundles, or GraphQL query endpoints to obstruct scrapers.
* **Mitigation:** Maintain decoupled scraper adapters with offline test fixtures (`tests/fixtures/`) to rapidly catch parsing regressions without relying on live network connectivity during CI.

### RSK-02: Rate Limiting & 429 Responses
* **Root Cause:** LinkedIn and Indeed monitor request frequency per IP and challenge repetitive unauthenticated clients.
* **Mitigation:** The runner implements randomized sleep intervals between requests and supports rotating residential/datacenter proxy pools configured via `--proxies`.

### RSK-03: Cross-Board Duplicate Inflation
* **Root Cause:** Employers syndicate single job openings to LinkedIn, Indeed, and ZipRecruiter simultaneously.
* **Mitigation:** The transformation service computes a normalized lowercase string hash before database insertion, deduplicating multi-board syndications into a single canonical entry with multiple source links.

### RSK-06: Resume Tailoring & Profile Drift
* **Root Cause:** Automated alignment algorithms may over-optimize or misrepresent competencies relative to listing requirements.
* **Mitigation:** Enforce strict deterministic extraction from structured profile YAML/SQLite datastores; never perform ungrounded generative expansion without verified candidate nodes.

### RSK-07: Follow-up Notification Delivery Failures
* **Root Cause:** Local daemons or cron jobs may sleep or experience interrupted executions during notification trigger windows.
* **Mitigation:** Store all follow-up tasks in a persistent SQLite table with status flags (`pending`, `notified`, `completed`, `snoozed`) and execute catch-up scans on any CLI invocation.

### RSK-08: Telemetry Attribution Degradation
* **Root Cause:** Candidates bypass CLI attribution prompts when submitting ad-hoc applications directly on external portals.
* **Mitigation:** Provide streamlined quick-log commands (`python scripts/log_application.py --listing-id ... --variant ...`) with default fallbacks and post-hoc attribution assignment.

### RSK-09: Schema & Serialization Desynchronization
* **Root Cause:** Independent evolution of Phase 2 dev script models and Phase 3 API endpoints.
* **Mitigation:** Enforce strict import sharing from `src/job_search_dev/models/`; both the internal Use Cases and FastAPI routes must bind to identical Pydantic classes.

### RSK-10: IPC / Stale Socket Collisions
* **Root Cause:** Daemon crashes leave uncleaned `.sock` files in runtime directory, causing subsequent thin client connections to hang.
* **Mitigation:** Daemon initialization routine checks socket health, removes stale socket files before binding, and wraps shutdown in signal handlers (`SIGTERM`, `SIGINT`).

### RSK-11: Scraper Interface Drift & Dependency Upgrades
* **Root Cause:** Upstream libraries (e.g. `python-jobspy`) release updates that alter DataFrame column names, types, or return signatures.
* **Mitigation:** Wrap each scraper in a dedicated adapter module adhering to `JobScraperPort`. Core domain logic never imports third-party scraper packages directly.

### RSK-12: Upstream Parser Regressions & Dataset Poisoning
* **Root Cause:** Target site changes return partial or empty fields (e.g., missing company name or corrupted title) that slip past scrapers.
* **Mitigation:** All raw payloads must pass strict Pydantic model validation before reaching the database. Validation failures are routed to `data/quarantine/` with structured error logs rather than poisoning `jobs.db`.

### RSK-13: Listing Staleness Decay
* **Root Cause:** Ingested postings remain in active views long after the role has been filled or closed by the employer.
* **Mitigation:** The ingestion engine records `first_seen_date` and `last_seen_date`. Postings not re-discovered within 30 days are automatically transitioned to `Archived` status via `UC-08`.

### RSK-14: Unattended Scraper Upgrades & Silent Parser Regressions
* **Root Cause:** Automatic background dependency updates install untested library versions that break extraction rules.
* **Mitigation:** Require explicit developer canary tests (`UC-09`) against local mock fixtures and a live single-target canary run before updating pinned project requirements.

### RSK-15: Secret & Credential Leakage in Version Control
* **Root Cause:** Developers inadvertently commit local API keys, SMTP credentials, or `.env` configuration files to git.
* **Mitigation:** Enforce strict `.gitignore` blocking `.env`, `*.pem`, `*.key`; install `pre-commit` hook running `gitleaks` locally; execute automated secret scanners in GitHub Actions CI (`UC-10`).

### RSK-16: Stale or Inaccurate Scraper Mock Fixtures
* **Root Cause:** Offline static fixtures in `tests/fixtures/` fall out of sync with updated scraper outputs, leading to false-positive test passes.
* **Mitigation:** Maintain `scripts/capture_fixtures.py` (`UC-11`) to re-record authentic sanitized scraper JSON payloads whenever scraper dependencies are upgraded.

### RSK-17: Dependency Drift & Environment Bloat
* **Root Cause:** Multiple conflicting requirement files (`requirements.txt`, `requirements-dev.txt`) fall out of synchronization.
* **Mitigation:** Unify all dependencies under `pyproject.toml` (ADR 0002); install core packages in production and optional `[dev]` extras in development environments.

### RSK-18: Packaging Runtime Environment Secrets in Distribution Wheels
* **Root Cause:** Declaring runtime config or `.env` files within `pyproject.toml` package data leaks local environment secrets into built distribution wheels.
* **Mitigation:** Maintain a strict separation between build metadata (`pyproject.toml`) and runtime environment loading (`pydantic-settings`); package exclusively source code.
