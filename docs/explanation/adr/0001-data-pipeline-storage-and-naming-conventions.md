---
title: "ADR 0001: Data Pipeline Storage Layout and File Naming Conventions"
created_at: 2026-09-17T01:16:11-04:00
updated_at: 2026-09-17T01:16:11-04:00
tags:
  - adr
  - explanation
  - data-pipeline
  - conventions
  - storage
desc: Architecture Decision Record defining storage hierarchy, partition schemes, and naming conventions for job scraper outputs and analytics
---

# ADR 0001: Data Pipeline Storage Layout and File Naming Conventions

## Context

The job search automation toolkit ingests semi-structured job posting data from multiple disparate sources (LinkedIn, Indeed, ZipRecruiter, Glassdoor) across repeated scraping intervals. Without strict storage conventions, files suffer from namespace collisions, untracked mutations, schema drift, and unmanageable repository bloat.

## Decision

We establish a standardized data lifecycle partitioning model, directory hierarchy, and deterministic file naming schema across all development, testing, and production environments.

### 1. Directory Topology

All generated runtime data must reside inside the root `data/` directory (strictly excluded in `.gitignore`), organized into three lifecycle stages:

```text
job-search-dev/
├── data/
│   ├── raw/                       # Immutable raw payloads partitioned by source & date
│   │   ├── indeed/
│   │   │   └── YYYY-MM-DD/
│   │   ├── linkedin/
│   │   │   └── YYYY-MM-DD/
│   │   └── zip_recruiter/
│   │       └── YYYY-MM-DD/
│   ├── processed/                 # Deduplicated, normalized datasets and relational stores
│   │   ├── jobs.db                # Primary SQLite database for deduplication & indexing
│   │   └── parquet/               # Columnar compressed historical partitions
│   └── reports/                   # Derived analytics, funnel metrics, and user exports
│       ├── exports/               # Formatted CSVs for external consumption
│       └── metrics/               # Summary metrics and funnel conversion JSONs
└── tests/
    └── fixtures/                  # Static, version-controlled mock payloads for tests
```

### 2. File Naming Conventions

#### 2.1 Raw Ingestion Payloads (`data/raw/`)
Raw scrape files must follow ISO 8601 UTC timestamp formatting and slugified parameters:

`YYYYMMDDTHHMMSSZ_<source>_<query-slug>_<location-slug>.<ext>`

* **Example:** `20260917T051500Z_linkedin_python-developer_remote.jsonl`
* **Format:** JSON Lines (`.jsonl`) or NDJSON to preserve raw nested structures without schema loss.

#### 2.2 Processed & Relational Data (`data/processed/`)
* **Primary Relational Store:** `data/processed/jobs.db` (SQLite 3 with WAL mode enabled).
* **Partitioned Columnar Store:** `data/processed/parquet/year=YYYY/month=MM/jobs_YYYYMM.parquet`.

#### 2.3 User Reports & Exports (`data/reports/`)
`YYYY-MM-DD_<report-name>_<filter-slug>.<ext>`

* **Example:** `2026-09-17_daily-digest_senior-remote.csv`
* **Example:** `2026-09-17_funnel-conversion-metrics.json`

#### 2.4 Test Fixtures (`tests/fixtures/`)
`mock_<source>_<scenario>.json`

* **Example:** `mock_indeed_standard_results.json`
* **Example:** `mock_linkedin_rate_limit_response.json`

### 3. Serialization and Encoding Standards

1. **Character Encoding:** All text-based files must be strictly encoded in `UTF-8`.
2. **CSV Quoting:** When emitting CSV exports, apply `QUOTE_NONNUMERIC` with explicit escape characters (`\`) to protect multiline descriptions.
3. **Immutability:** Files placed into `data/raw/` are write-once, read-many (WORM). They must never be edited in place.

## Consequences

### Positive
- **Deterministic Archival:** Lexicographical sorting mirrors chronological order, simplifying incremental ingestion.
- **Deduplication Simplicity:** Clear separation between raw board output and canonical unified records in `data/processed/jobs.db`.
- **Reproducibility:** Testing utilizes isolated static fixtures under `tests/fixtures/` without depending on live network calls.

### Negative
- **Storage Growth:** Retaining raw JSONL files requires periodic archival or compression policies.
