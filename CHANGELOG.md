---
title: Changelog
created_at: 2026-09-17T01:10:36-04:00
updated_at: 2026-09-17T02:20:48-04:00
tags:
  - changelog
  - releases
desc: Project version history and release notes
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-17

### Added
- Initial project workspace scaffolding adhering to HSL/SDP standards.
- Core CLI scrape runner script `scripts/run_scrape.py` with multi-board execution.
- Storage utility module `src/job_search_dev/storage.py` implementing slugification, partitioned raw JSONL persistence, and ADR 0001 compliant path generation.
- Architecture Decision Record `docs/explanation/adr/0001-data-pipeline-storage-and-naming-conventions.md` (ADR 0001).
- Unified Process documentation suite including Vision and Scope, Software Architecture Document (SAD), Use Cases specification, Risk Register, and Verification Test Plan under `docs/`.
- Expanded test suite in `tests/test_basic.py` covering Pydantic v2 schemas, slugification, pathing, and multi-source raw partitioning.
- Application tracking pipeline in `data/reports/applications_tracker.json` and `docs/reference/application-log.md`.
- Resume generation templates and compiled single-page PDFs under `/home/michael/docs/reference/resumes/`.
