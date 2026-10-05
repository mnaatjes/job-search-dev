---
title: Job Search Pipeline Architecture
created_at: 2026-09-17T01:10:36-04:00
updated_at: 2026-09-17T01:10:36-04:00
tags:
  - explanation
  - architecture
  - anti-bot
  - design
desc: Architectural overview of scraping engines, rate mitigation, TLS fingerprinting, and intake ingestion
---

# Job Search Pipeline Architecture

This document explains the architectural principles governing the automated job discovery, extraction, and ingestion pipeline.

## System Workflow

```text
+-------------------+      +-------------------+      +-------------------+
|  Target Boards    | ---> | TLS Client Worker | ---> | DataFrame Filter  |
| LinkedIn / Indeed |      | (Unauthenticated) |      | & Deduplication   |
+-------------------+      +-------------------+      +-------------------+
                                                        |
                                                        v
                                              +-------------------+
                                              | Storage / SQLite  |
                                              | & Funnel Analytics|
                                              +-------------------+
```

## Unauthenticated Scraping & TLS Fingerprinting

Commercial job boards employ Cloudflare and proprietary Web Application Firewalls (WAFs) to detect automated HTTP clients. Standard Python `requests` implementations broadcast distinct TLS Client Hello cipher suites and JA3/JA4 fingerprints that are instantly flagged and blocked.

To circumvent fingerprint-based mitigation without requiring authenticated user sessions, the engine utilizes `tls-client` to impersonate authentic browser TLS handshakes and HTTP/2 settings.

## Data Deduplication Strategies

Job aggregators frequently duplicate postings across multiple networks. Downstream deduplication computes deterministic SHA256 hashes based on normalized strings:

$$\text{hash} = \text{SHA256}(\text{lower}(\text{company}) + \text{lower}(\text{title}) + \text{lower}(\text{location}))$$
