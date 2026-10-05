---
title: "Verification and Test Plan: Attributed Lead Generation and Conversion Analytics Platform"
created_at: 2026-09-17T01:36:43-04:00
updated_at: 2026-09-17T01:36:43-04:00
tags:
  - unified-process
  - construction
  - testing
  - test-plan
  - reference
desc: Verification metrics, test frameworks, hermetic fixture isolation, and coverage benchmarks
---

# Verification and Test Plan

## 1. Verification Targets

The test suite validates eight core layers of the platform:

1. **Schema & Model Validation:** Strictly verify Pydantic v2 domain schemas (`JobPost`, `QueryProfile`, `ApplicationEvent`, `ResumeVariant`, `FollowUpTask`).
2. **Path & Storage Compliance (ADR 0001):** Ensure all raw partitions, rendered resumes, and export files follow deterministic ISO 8601 UTC timestamping and slug formats.
3. **Deduplication Integrity:** Verify that identical job entries across different sites collapse into a single canonical record with deterministic SHA256 hashes.
4. **Data Normalization:** Validate salary frequency conversion (hourly, monthly, yearly to annual USD) and location parsing.
5. **Artifact Compilation & Alignment:** Verify deterministic node extraction from profile repository data into Markdown/PDF/LaTeX artifacts without text distortion or hallucinations (`UC-05`).
6. **Notification Scheduling & Catch-Up:** Verify due date evaluation, state transitions (`pending` $\rightarrow$ `notified`), and missed task catch-up algorithms (`UC-06`).
7. **Attribution & Yield Telemetry:** Validate multi-dimensional conversion calculations across resume variants, query profiles, and application funnel velocity (`UC-04`).
8. **API Driving Adapters & Serialization:** Verify FastAPI routes, asynchronous background task queuing, and thin-client JSON serialization using `fastapi.testclient.TestClient`.

## 2. Testing Framework & Tooling

* **Test Runner:** `pytest` (v7.4.0+)
* **Coverage Engine:** `pytest-cov` (v4.1.0+)
* **API Testing:** `httpx` and `fastapi.testclient`
* **Code Formatting & Linters:** `black` (v23.0+), `flake8` (v6.0+), and `isort`
* **Secret Leak Detection:** `gitleaks` (v8.18+)
* **Hook Orchestration:** `pre-commit` (v3.5+)
* **Execution Commands:**
  ```bash
  # Run full hermetic test suite with coverage
  pytest --cov=job_search_dev --cov-report=term-missing tests/

  # Run formatting and linting checks
  black --check src/ scripts/ tests/
  flake8 src/ scripts/ tests/

  # Run pre-commit hooks manually
  pre-commit run --all-files
  ```

## 3. Hermetic Test Fixtures & Capture Strategy

CI and regression tests must **never make live network requests** to external job boards. All testing operates against static mock fixtures stored under `tests/fixtures/`:

### 3.1 Scraper Output Payload Fixtures (`tests/fixtures/scrapers/`)
Fixtures at the scraper boundary model the raw DataFrame/dictionary payloads returned by the scraper dependency (`JobSpy`), **not** raw HTML:
* `tests/fixtures/scrapers/mock_indeed_jobspy_raw.json`: Normalized dictionary payload representing an Indeed search response.
* `tests/fixtures/scrapers/mock_linkedin_jobspy_raw.json`: Normalized dictionary payload representing a LinkedIn guest response.
* `tests/fixtures/scrapers/mock_ziprecruiter_jobspy_raw.json`: Normalized dictionary payload representing ZipRecruiter results.
* `tests/fixtures/scrapers/mock_multiboard_duplicate.json`: Cross-posted duplicate postings across multiple boards.

### 3.2 Core Domain & API Fixtures (`tests/fixtures/domain/`)
* `tests/fixtures/domain/mock_profile_repository.yaml`: Structured candidate skills, work history, and project nodes (`UC-05`).
* `tests/fixtures/domain/mock_api_requests.json`: Sample client request DTO envelopes for FastAPI endpoint tests.

### 3.3 Fixture Recording & Refresh Routine
When upstream dependencies are upgraded, developers refresh fixtures using the isolated recorder (`UC-11`):
```bash
python scripts/capture_fixtures.py --site all --limit 5
```

## 4. Coverage Requirements

| Component | Target Coverage | Current Status |
| :--- | :--- | :--- |
| `src/job_search_dev/storage.py` | $\ge 90\%$ | 100% |
| `src/job_search_dev/use_cases/` | $\ge 90\%$ | Planned |
| `src/job_search_dev/api/` | $\ge 85\%$ | Planned |
| `src/job_search_dev/normalization.py` | $\ge 90\%$ | Planned |
| `src/job_search_dev/attribution.py` | $\ge 85\%$ | Planned |
| `src/job_search_dev/generators.py` | $\ge 90\%$ | Planned |
| `src/job_search_dev/notifications.py` | $\ge 90\%$ | Planned |
| Total Project Minimum | $\ge 85\%$ | Verified Baseline |

---

## 5. Continuous Integration (CI/CD) Workflow

The automated CI pipeline (`.github/workflows/ci.yml`) executes on every push and pull request across three gated stages:

1. **Syntax & Formatting Stage:** Validates trailing whitespace, EOL formatting, JSON/YAML integrity, `black --check`, and `flake8`.
2. **Security & Secret Stage:** Scans all commit diffs using `gitleaks` to block hardcoded API tokens or private keys (`RSK-15`).
3. **Hermetic Test & Coverage Stage:** Runs the full `pytest` suite and asserts that code coverage meets the $\ge 85\%$ threshold. Releases or merges are blocked if any stage fails.
