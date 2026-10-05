---
title: How to Configure JobSpy Scraping Parameters
created_at: 2026-09-17T01:10:36-04:00
updated_at: 2026-09-17T01:10:36-04:00
tags:
  - how-to
  - jobspy
  - scraping
  - configuration
desc: Practical guide for configuring search filters, handling rate limits, and configuring proxy pools
---

# How to Configure JobSpy Scraping Parameters

This guide describes how to customize search queries, bypass rate limits, and configure site-specific parameters in `JobSpy`.

## Configuring Query Search Terms

Use Boolean logic for targeted matching on Indeed and Glassdoor:

```python
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "glassdoor"],
    search_term='"Site Reliability Engineer" (Kubernetes OR Terraform) -senior',
    location="Remote",
    results_wanted=25,
    hours_old=48,
    country_indeed="USA",
)
```

## Configuring Proxies to Prevent HTTP 429

Rotate HTTP/SOCKS5 proxies when querying LinkedIn or submitting frequent requests:

```python
proxies = [
    "user:password@proxy1.example.com:8080",
    "user:password@proxy2.example.com:8080",
]

jobs = scrape_jobs(
    site_name=["linkedin", "indeed"],
    search_term="Backend Engineer",
    location="San Francisco, CA",
    proxies=proxies,
    results_wanted=50,
)
```

## Handling Parameter Conflicts

- **Indeed:** Avoid combining `hours_old` with `is_remote` or `job_type` in the same API call.
- **LinkedIn:** Do not enable `easy_apply=True` as upstream support has been deprecated.
