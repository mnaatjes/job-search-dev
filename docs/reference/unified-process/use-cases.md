---
title: "Use Cases: Attributed Lead Generation and Conversion Analytics Platform"
created_at: 2026-09-17T01:36:43-04:00
updated_at: 2026-09-17T01:36:43-04:00
tags:
  - unified-process
  - elaboration
  - use-cases
  - reference
desc: Detailed Use Case catalog detailing actors, preconditions, main success scenarios, and alternative flows
---

# Use Cases Specification

## 1. Actors

* **Candidate / Operator (Primary Actor):** Configures search profiles, triggers ad-hoc scrapes, reviews reports, and records application state transitions via Dev Scripts (Phase 2) or Thin CLI / Web UI (Phase 4).
* **Cron / Scheduler Daemon (Primary Actor):** Periodically triggers batch scrapes and evaluates follow-up task queues via headless API endpoints.
* **API Driving Adapter (Supporting Actor):** FastAPI/UDS router translating external JSON requests into typed Core Use Case invocations.
* **Target Job Board Endpoints (Supporting Actor):** External servers (LinkedIn, Indeed, ZipRecruiter) responding to unauthenticated queries.

## 2. Use Case Survey

| ID | Use Case Name | Actor | Summary |
| :--- | :--- | :--- | :--- |
| `UC-01` | Ingest Multi-Board Postings | Candidate / Cron | Scrapes unauthenticated job boards based on a QueryProfile and writes raw JSONL payloads. |
| `UC-02` | Deduplicate & Normalize Postings | System | Transforms raw JSONL into normalized records and upserts them into the SQLite database. |
| `UC-03` | Track Human-in-the-Loop Application Lifecycle | Candidate | Logs interactive and terminal application state changes (`Staged`, `Applying`, `Applied`, `Screening`, `Interview`, `Offer`, `Rejected`). |
| `UC-04` | Generate Attribution & Variant Conversion Analytics | Candidate | Aggregates conversion metrics segmented by query profiles, target channels, application duration, and resume variants. |
| `UC-05` | Generate Tailored Application Artifacts | Candidate / System | Assembles targeted resumes and cover letters from structured profile repositories matching listing requirements. |
| `UC-06` | Schedule and Dispatch Follow-Up Notifications | Candidate / Cron | Establishes automated cadences and alerts for post-application follow-up milestones. |
| `UC-07` | Ingest Application Responses via Inbound Channels | Candidate / Cron | Ingests incoming emails/webhooks, detects interview/rejection keywords, and auto-links response events to active applications. |
| `UC-08` | Prune Stale Postings & Archive Inactive Leads | System / Cron | Evaluates listing staleness decay, marks expired unapplied postings as archived, and compresses historical raw partitions. |
| `UC-09` | Audit Scraper Health & Check Upstream Updates | Candidate / Cron | Proactively detects consecutive scrape failures, queries PyPI/GitHub for scraper updates, and executes canary validation tests. |
| `UC-10` | Execute CI Quality Gates & Hermetic Test Suite | CI Runner / Candidate | Runs linting (black/flake8), secret scanning (gitleaks), and offline pytest suites on pull requests and pushes. |
| `UC-11` | Capture & Refresh Hermetic Scraper Fixtures | Candidate | Executes isolated live canary scrape to serialize and sanitize raw scraper output payloads for offline regression fixtures. |

---

## 3. Detailed Use Case Specifications

### UC-01: Ingest Multi-Board Postings
* **Primary Actor:** Candidate or Cron Daemon
* **Preconditions:** Network connection is active; `QueryProfile` is defined with valid search terms.
* **Main Success Scenario (Basic Flow):**
  1. Actor triggers scrape with `query_profile_id` or explicit CLI arguments (`--term`, `--location`, `--sites`).
  2. System initializes scraper worker using TLS-impersonating HTTP client.
  3. Scraper queries target job boards concurrently.
  4. System partitions retrieved records by site and writes raw JSONL files into `data/raw/<site>/YYYY-MM-DD/`.
  5. System returns execution telemetry (listings discovered, execution duration).
* **Alternative Flows (Exceptions):**
  * *HTTP 429 Rate Limit:* System logs warning telemetry, backs off with exponential jitter, switches proxy if configured, and continues remaining boards.
  * *No Results Found:* System writes empty partition log and exits cleanly with zero error code.

### UC-02: Deduplicate and Normalize Postings
* **Primary Actor:** System (Transformation Service)
* **Preconditions:** Raw JSONL files exist in `data/raw/`.
* **Main Success Scenario:**
  1. System reads new raw JSONL partition files.
  2. For each record, computes composite SHA256 deduplication hash (`company + title + location`).
  3. Parses salary strings into `min_amount`, `max_amount`, and converts to standardized annual USD.
  4. Checks SQLite database for existing deduplication hash.
  5. If new, inserts record into `job_listings` linked to the originating `query_profile_id`.
  6. If existing, updates `last_seen_date` and appends alternative board URLs.

### UC-03: Track Human-in-the-Loop Application Lifecycle
* **Primary Actor:** Candidate
* **Preconditions:** Target `job_listing_id` exists in `job_listings` table.
* **Main Success Scenario:**
  1. Candidate selects a target `job_listing_id` to prepare an application (state transition: `Staged`).
  2. Candidate initiates manual entry workflow (state transition: `Applying`) and generates/attaches tailored artifacts (`UC-05`).
  3. Candidate completes submission on external ATS/board and confirms submission with applied timestamp, external application ID, and variant linkage (state transition: `Applied`).
  4. System records timestamped transition in `application_events` and automatically registers default follow-up reminders (`UC-06`).
  5. Candidate subsequently records progressive outcomes (`Screening`, `Interview`, `Offer`, `Rejected`, `Ghosted`).

### UC-04: Generate Attribution & Variant Conversion Analytics
* **Primary Actor:** Candidate
* **Preconditions:** Application events and attribution tags logged across multiple listings and resume variants.
* **Main Success Scenario:**
  1. Candidate requests conversion and attribution analytics filtered by date range or target parameters.
  2. System queries database joining `job_listings`, `applications`, `application_events`, and `resume_variants`.
  3. Calculates performance metrics:
     * **Application Conversion Yield:**
       $$\text{Yield} = \frac{\text{Interviews}}{\text{Applications}} \times 100$$
     * **Resume Variant Effectiveness:** Conversion rates by tailored resume variant template and keyword alignment score.
     * **Acquisition Funnel Velocity:** Mean time elapsed between `Staged` $\rightarrow$ `Applied` and `Applied` $\rightarrow$ `Screening`.
     * **Channel Efficiency:** Yields segmented by source job boards and referral routes.
  4. Exports structured summary metrics to `data/reports/exports/`.

### UC-05: Generate Tailored Application Artifacts
* **Primary Actor:** Candidate / System
* **Preconditions:** Target `job_listing_id` exists; candidate profile repository (skills, experience nodes, education, project blocks) is initialized.
* **Main Success Scenario:**
  1. Candidate requests resume generation tailored for `job_listing_id`.
  2. System extracts job requirements, required competencies, and tech stack tokens from listing text.
  3. Generator ranks and selects matching skill nodes, project contributions, and work history bullet points from the profile repository.
  4. Generator compiles output into target formats (Markdown, PDF, LaTeX) and persists artifact metadata into `resume_variants`.
  5. Candidate reviews generated artifact, applies optional manual overrides, and links variant to the pending application.

### UC-06: Schedule and Dispatch Follow-Up Notifications
* **Primary Actor:** Candidate / Cron Daemon
* **Preconditions:** Target application is in `Applied` or `Interview` status with pending follow-up schedules.
* **Main Success Scenario:**
  1. System initializes follow-up task schedule upon application submission ($T+7$ days for status inquiry, $T+1$ day post-interview thank-you).
  2. Cron Daemon evaluates pending tasks against current UTC timestamp during scheduled runs.
  3. When a task reaches maturity, system triggers notification (CLI alert banner, exported action list, or system alert).
  4. Candidate reviews follow-up alert, executes outreach, and records completion or snooze interval.

### UC-07: Ingest Application Responses via Inbound Channels
* **Primary Actor:** Candidate / Cron Daemon
* **Preconditions:** Inbound email client configured (IMAP/OAuth) or webhook listener active; active applications exist in database.
* **Main Success Scenario:**
  1. Cron worker fetches unread messages from designated application mailbox/folder.
  2. Extract sender domain, company name, and candidate subject reference.
  3. Match message against pending `applications` using company name and application date range.
  4. Classify intent via deterministic keyword pattern matcher (`rejection`, `invitation_to_screen`, `assessment_request`).
  5. Propose or insert state transition event into `application_events` and flag task for candidate review.

### UC-08: Prune Stale Postings & Archive Inactive Leads
* **Primary Actor:** System (Maintenance Service) / Cron Daemon
* **Preconditions:** Scheduled execution trigger; configurable retention policy (`STALENESS_DAYS_THRESHOLD = 30`).
* **Main Success Scenario:**
  1. System scans `job_listings` for records in `Discovered` state where `last_seen_date < (NOW - STALENESS_DAYS_THRESHOLD)`.
  2. Flags stale listings as `Archived` to remove them from active discovery views while retaining them for attribution history.
  3. Scans `data/raw/` partition files older than 30 days and compresses them to `.jsonl.gz`.
  4. Emits storage reclamation telemetry (records archived, bytes compressed).

### UC-09: Audit Scraper Health & Check Upstream Updates
* **Primary Actor:** Candidate / Cron Daemon
* **Preconditions:** Operational telemetry logged for recent scrape executions.
* **Main Success Scenario:**
  1. System analyzes scrape telemetry for consecutive zero-yield runs or parsing exceptions per job board.
  2. System queries PyPI registry (`pip list --outdated`) or upstream GitHub release feeds for scraper package bumps (e.g. `python-jobspy`).
  3. If updates exist or failure thresholds are exceeded, emits an alert recommending a dependency update.
  4. Candidate executes isolated canary test (`pytest tests/integration/test_scrapers.py`) to verify new version before promoting to production.

### UC-10: Execute CI Quality Gates & Hermetic Test Suite
* **Primary Actor:** CI Runner / Candidate
* **Preconditions:** Git commit or pull request submitted to repository.
* **Main Success Scenario:**
  1. GitHub Actions runner executes pre-commit hooks: checks for trailing whitespace, JSON/YAML syntax validity, and runs `black --check` and `flake8`.
  2. Executes `gitleaks` secret detection scanner across commit diff to verify zero leaked API keys or `.env` secrets (`RSK-15`).
  3. Verifies packaging isolation: asserts that minimal production installation (`pip install .`) succeeds cleanly without developer dependencies, and full test suite executes under `pip install -e ".[dev]"` (`RSK-17`).
  4. Runs hermetic `pytest` suite across `tests/unit/`, `tests/api/`, and `tests/integration/` using static fixtures without live network calls.
  5. Assesses coverage against minimum threshold ($\ge 85\%$). Fails build if regressions occur.

### UC-11: Capture & Refresh Hermetic Scraper Fixtures
* **Primary Actor:** Candidate (Developer)
* **Preconditions:** Developer workstation with network access; scraper dependency updated.
* **Main Success Scenario:**
  1. Developer invokes fixture recorder: `python scripts/capture_fixtures.py --site indeed --limit 5`.
  2. Recorder calls `JobSpy` scraper, intercepts the raw DataFrame/dictionary output, and serializes the exact payload to `tests/fixtures/mock_indeed_raw.json`.
  3. Sanitizes user session tokens, dynamic session timestamps, or private identifiers.
  4. Developer commits the updated fixture files to Git for hermetic CI consumption.
