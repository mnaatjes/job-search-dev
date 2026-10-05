---
title: "ADR 0002: Environment Baseline, Packaging, CI/CD, and Code Quality Standards"
tags: ["adr", "architecture", "ci-cd", "quality", "packaging", "explanation"]
created_at: "2026-09-17"
last_updated_at: "2026-09-17"
desc: "Formalize project packaging (pyproject.toml), semantic versioning (bump-my-version), code formatting, secret protection, and automated CI quality gates"
---

# ADR 0002: Environment Baseline, Packaging, CI/CD, and Code Quality Standards

## 1. Status
Accepted

---

## 2. Context
Developing a robust, production-grade ELT and analytics platform requires standardizing developer environments, dependency management, semantic versioning, and code quality guardrails from the outset. Without explicit, automated enforcement:
* **Code Formatting Drift:** Inconsistent Python styling, EOL trailing spaces, and untidy JSON/YAML structures pollute commit histories and merge reviews.
* **Security & Secret Leakage (`RSK-15`):** Developers risk accidentally committing `.env` configuration files, local tokens, or private credentials to public version control.
* **Uncoordinated Version Bumping:** Manual version updates across `pyproject.toml`, `CHANGELOG.md`, and Python package `__init__.py` files lead to desynchronization and broken release tracking.
* **Broken Regression Gates:** Regressions or failing tests may enter the main branch if test suites and coverage thresholds ($\ge 85\%$) are not strictly gated by an automated CI runner.

---

## 3. Decision

We establish an immutable **Environment Baseline & Quality Standard** consisting of the following architectural choices:

### 3.1 Packaging, Entry Points, Dependency Stratification & Drift Prevention
* Adopt **`pyproject.toml` (PEP 517 / PEP 621)** as the sole, authoritative source of truth for project metadata, dependencies, build backends, entry points, and tool configurations.
* **Executable Entry Points (`[project.scripts]` & `__main__.py`):**
  * Register `jobctl = "job_search_dev.cli:main"` under `[project.scripts]` in `pyproject.toml` to automatically install the unified CLI binary to `$PATH` during `pip install .`.
  * Implement `src/job_search_dev/__main__.py` to support direct module execution via `python -m job_search_dev`.
* **Runtime Configuration Decoupling (`.env` vs `pyproject.toml`):**
  * In compliance with Twelve-Factor Factor III, `.env` and `.env.dev` files are **never** declared or packaged in `pyproject.toml`.
  * Runtime settings are resolved dynamically at startup via `pydantic-settings` (`SettingsConfigDict(env_file=(".env.dev", ".env"))`), reading from the execution environment. A public, sanitized `.env.example` is maintained in version control as a schema template.
* **Production Dependencies (`[project.dependencies]`):** Minimal runtime set required for daemonized operation (`python-jobspy`, `pydantic`, `fastapi`, `uvicorn`, `httpx`, `pandas`, `pydantic-settings`, `pyyaml`).
* **Development & Test Dependencies (`[project.optional-dependencies].dev`):** Developer-only tooling (`pytest`, `pytest-cov`, `black`, `flake8`, `isort`, `pre-commit`, `bump-my-version`).
* **Drift Elimination:** Eliminate manual, redundant `requirements.txt` files. Developers install via `pip install -e ".[dev]"`; production installations execute `pip install .`. If legacy tools require a `requirements.txt`, it will contain strictly `-e .` or `-e ".[dev]"` pointers to prevent desynchronization.
* Package dependencies are isolated via Python 3.12+ virtual environments (`.venv`).

### 3.2 Semantic Versioning & Release Tooling
* Enforce **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).
* Adopt **`bump-my-version`** to atomically increment version numbers simultaneously across `pyproject.toml`, `src/job_search_dev/__init__.py`, and update `CHANGELOG.md` following the Keep a Changelog standard.

### 3.3 Static Analysis, Formatting & Secret Protection
* **Code Formatter:** `black` (PEP 8 compliant, line length 88).
* **Import Sorter:** `isort` configured with `black` profile compatibility.
* **Linter & Style Checker:** `flake8` checking for syntax errors, undefined variables, and cyclomatic complexity.
* **Secret Leak Prevention:** `gitleaks` configured to block hardcoded API keys, private keys, and `.env` credentials.
* **Hook Orchestration:** `pre-commit` running all formatters, whitespace trimmers, YAML/JSON linters, and secret scanners locally prior to Git commit creation.

### 3.4 Continuous Integration (CI) Workflow
* Implement **GitHub Actions (`.github/workflows/ci.yml`)** triggered on every pull request and push to `main`.
* The CI pipeline strictly enforces:
  1. Pre-commit syntax, formatting, and secret scan verification.
  2. Hermetic test suite execution (`pytest`) strictly using static mock fixtures (`tests/fixtures/`) with **zero live network calls**.
  3. Minimum code coverage benchmark ($\ge 85\%$ total) via `pytest-cov`.

---

## 4. Consequences

### Positive
* **Zero Cognitive Overhead:** Automated linters and formatters eliminate styling debates during code reviews.
* **Hermetic Protection:** Gated CI guarantees that no broken scrapers, failing tests, or credential leaks can merge to `main`.
* **Single Source of Truth:** `pyproject.toml` centralizes packaging, test runner settings, and tool configurations into one file.
* **Clean Release Automation:** `bump-my-version` ensures synchronized version tags and changelog tracking.

### Negative / Trade-Offs
* **Pre-Commit Latency:** Running `black`, `flake8`, and `gitleaks` adds a minor 1–2 second overhead on local Git commits.
* **Strict CI Gates:** Merges are blocked if test coverage drops below 85% or if linting errors exist.

### Neutral
* Developers must execute `pre-commit install` upon initial repository setup.

---

## 5. Procedure & Implementation

- [ ] **Step 1: Configure `pyproject.toml`:** Centralize project metadata, build backend, `black`, `isort`, `flake8`, and `bump-my-version` configurations.
- [ ] **Step 2: Configure `.pre-commit-config.yaml`:** Add hooks for `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-json`, `black`, `isort`, `flake8`, and `gitleaks`.
- [ ] **Step 3: Harden `.gitignore`:** Ensure `.env`, `.venv`, `.pytest_cache`, `data/raw/`, `data/processed/`, and sensitive files are strictly excluded from version control.
- [ ] **Step 4: Update CI Workflow (`.github/workflows/ci.yml`):** Configure multi-step GitHub Action executing pre-commit linting, secret scanning, and hermetic `pytest` with coverage gating.
- [ ] **Step 5: Install & Verify:** Run `pre-commit run --all-files` and `pytest` to establish the validated baseline.
