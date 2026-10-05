---
title: "How-To: Capture and Refresh Hermetic Scraper Fixtures"
created_at: 2026-09-17T14:04:56-04:00
updated_at: 2026-09-17T14:04:56-04:00
tags:
  - testing
  - fixtures
  - scrapers
  - how-to
desc: Step-by-step operational guide for recording, sanitizing, and committing offline scraper mock payloads
---

# How to Capture and Refresh Hermetic Scraper Fixtures

This guide describes how to capture and update static test fixtures from scraper libraries (e.g. `JobSpy`) to maintain hermetic test isolation without executing live network calls in CI.

---

## 1. Prerequisites

* Developer workstation with active internet access.
* Python virtual environment activated:
  ```bash
  source .venv/bin/activate
  ```
* Upgraded scraper dependency (if executing a dependency upgrade workflow).

---

## 2. Capture Procedure

### Step 1: Run the Fixture Capture Utility
Execute the fixture capture runner for the target job board:

```bash
# Capture single board (e.g. Indeed)
python scripts/capture_fixtures.py --site indeed --limit 5

# Capture all supported job boards
python scripts/capture_fixtures.py --site all --limit 5
```

The script:
1. Calls `JobSpy.scrape_jobs()` with controlled query parameters.
2. Intercepts the raw DataFrame/dictionary outputs.
3. Automatically sanitizes dynamic timestamps, session cookies, and private tokens.
4. Serializes the JSON payload into `tests/fixtures/scrapers/mock_<site>_jobspy_raw.json`.

---

### Step 2: Verify Hermetic Test Suite
Run the test suite offline to confirm that existing domain models parse the new fixture payloads successfully:

```bash
pytest tests/unit/ tests/integration/
```

If tests fail due to upstream schema changes:
1. Update field aliases in `src/job_search_dev/models/job_post.py` (Tolerant Reader pattern).
2. Re-run `pytest` until 100% passing.

---

### Step 3: Commit Fixtures to Version Control
Commit the updated JSON mock payloads alongside any model/adapter changes:

```bash
git add tests/fixtures/scrapers/*.json
git commit -m "test: refresh hermetic scraper fixtures for python-jobspy vX.Y.Z"
```
