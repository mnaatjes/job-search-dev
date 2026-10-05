---
title: Getting Started with Job Search Dev
created_at: 2026-09-17T01:10:36-04:00
updated_at: 2026-09-17T01:10:36-04:00
tags:
  - tutorial
  - setup
  - quickstart
desc: Step-by-step tutorial for setting up the local environment and running initial job scrapes
---

# Getting Started with Job Search Dev

This tutorial walks through creating a virtual environment, installing dependencies, and running your first multi-board job scrape.

## Prerequisites

- Python 3.10 or higher
- Git

## Step 1: Environment Setup

Create and activate a clean virtual environment:

```bash
cd /home/michael/src/github.com/mnaatjes/job-search-dev
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Step 2: Execute Initial Scrape

Run the baseline scraper targeting remote roles:

```bash
python scripts/run_scrape.py --term "DevOps Engineer" --location "Remote" --limit 5 --out data/initial_scrape.csv
```

## Step 3: Inspect the Output

View the structured output dataset using pandas:

```bash
python -c "import pandas as pd; df = pd.read_csv('data/initial_scrape.csv'); print(df[['site', 'title', 'company', 'location']])"
```
