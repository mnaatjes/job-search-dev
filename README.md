---
title: Job Search Development Toolkit
created_at: 2026-09-17T01:10:36-04:00
updated_at: 2026-09-17T01:10:36-04:00
tags:
  - job-search
  - scraping
  - automation
  - python
desc: Programmatic job intake, aggregation, and search analytics pipeline
---

# Job Search Dev Toolkit

Programmatic job search intake, multi-board aggregation, and analytics pipeline built on top of `python-jobspy`.

## Project Layout

```text
job-search-dev/
├── .github/
│   └── workflows/
│       └── ci.yml               # Continuous integration workflow
├── docs/                        # Diátaxis framework documentation
│   ├── tutorials/               # Learning-oriented guides
│   ├── how-to/                  # Problem-oriented guides
│   ├── reference/               # Information-oriented technical descriptions
│   └── explanation/             # Understanding-oriented discussions
├── scripts/                     # Executable CLI runners and intake scripts
├── src/                         # Core Python package source
│   └── job_search_dev/
├── tests/                       # Automated test suite
├── CHANGELOG.md                 # Semantic version changelog
├── pyproject.toml               # Build system and metadata
├── requirements.txt             # Dependency definitions
└── README.md                    # Project landing page
```

## Quick Start

### 1. Setup Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2. Run Test Scrape

```bash
python scripts/run_scrape.py --term "Python Developer" --location "Remote" --limit 5
```

### 3. Run Test Suite

```bash
pytest
```

## Documentation Index (Diátaxis)

- **Tutorials:** [Getting Started](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/tutorials/getting-started.md)
- **How-To Guides:** [Configure JobSpy Scrapes](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/how-to/configure-jobspy-scrape.md)
- **Reference:** [Job Post Schema & Types](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/reference/job-schema.md)
- **Explanation:** [Pipeline Architecture & Anti-Bot Strategy](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/explanation/pipeline-architecture.md)
