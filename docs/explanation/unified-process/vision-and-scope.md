---
title: "Vision and Scope: Attributed Lead Generation and Conversion Analytics Platform"
created_at: 2026-09-17T01:36:43-04:00
updated_at: 2026-09-17T01:36:43-04:00
tags:
  - unified-process
  - inception
  - vision
  - explanation
desc: Project vision, product positioning, boundaries, and global system capabilities for the job search platform
---

# Vision and Scope Document

## 1. Product Positioning

* **Problem Statement:** Job seekers face high friction in discovering quality opportunities due to platform-specific algorithmic feed bias, sponsored ad noise, aggressive session tracking, and fragmented data across walled gardens (LinkedIn, Indeed, ZipRecruiter, Glassdoor). Furthermore, job hunters lack attribution data to determine which search terms, parameters, and boards yield the highest interview conversion rates.
* **Target User:** Software engineers, technical job seekers, and career operators seeking automated, programmatic job discovery and empirical conversion yield analytics.
* **Value Proposition:** An unauthenticated, local-first ELT pipeline that aggregates job postings, normalizes compensation and requirements, maintains query parameter attribution, and measures the conversion variance of job search strategies.

## 2. Project Scope & Boundaries

### 2.1 In-Scope
* **Multi-Board Unauthenticated Ingestion:** Scraping LinkedIn, Indeed, Glassdoor, ZipRecruiter, and Google Jobs using `JobSpy` and `tls-client`.
* **ELT Data Ingestion & Storage:** Immutable raw JSONL partitioning under `data/raw/` and consolidated relational storage in SQLite (`data/processed/jobs.db`).
* **Cross-Board Deduplication & Normalization:** Composite hashing (`company` + `title` + `location`) and wage-to-annual USD conversion.
* **Human-in-the-Loop (HITL) Lifecycle Tracking:** Explicit staging, manual application progression, external submission tracking, and post-application status updates (`Staged` $\rightarrow$ `Applying` $\rightarrow$ `Applied` $\rightarrow$ `Screen` $\rightarrow$ `Interview` $\rightarrow$ `Offer` / `Rejected`).
* **Follow-Up Automation & Scheduling:** Due-date tracking, milestone cadences ($T+7$ status inquiries, $T+1$ interview follow-ups), and proactive notifications.
* **Modular Artifact Generation Engine:** Deterministic assembly of tailored resumes and cover letters from structured profile repositories (skills, work history, projects) aligned to posting requirements.
* **Parameter & Variant Attribution Analytics:** Multidimensional conversion telemetry comparing query profiles, search terms, resume templates, and application efficiency/velocity metrics.
* **API-First Headless Architecture:** Core application encapsulated behind typed Pydantic contracts and exposed via local REST/UDS daemon endpoints (`FastAPI`) supporting thin clients.
* **Scheduled Automation:** Headless scheduled executions via systemd timers or cron daemon workers calling the local API.
* **Structured Logging & Telemetry:** JSON-formatted audit logs capturing scraping latencies, HTTP status codes, and deduplication yield.

### 2.2 Out-of-Scope (Deferred / Excluded)
* **Automated Headless Form Submission Bots:** Direct headless browser automation for injecting data into external ATS forms or bypassing CAPTCHAs is strictly excluded; application submissions remain Human-in-the-Loop (HITL).
* **Enterprise ATS Integrations:** Direct API integrations with enterprise ATS backends (Workday, Greenhouse, Lever) are deferred to future phases.
* **Cloud Multi-Tenant SaaS Hosting:** The architecture is local-first and self-hosted.

## 3. Global System Features

```text
+---------------------------------------------------------------------------------+
|                       Attributed Lead Gen & Analytics                           |
+---------------------------------------------------------------------------------+
|  [FEAT-01] Multi-Source Ingestion Engine (JobSpy / TLS Fingerprint Worker)      |
|  [FEAT-02] ELT Normalization & Deduplication Pipeline (SQLite / Hashes)         |
|  [FEAT-03] Parameterized Query Control Plane (Profile Management API / CLI)     |
|  [FEAT-04] Scheduled Batch Orchestrator (Cron / Systemd Timers)                 |
|  [FEAT-05] Operational Logging & Telemetry Monitor (JSON Log Emitters)          |
|  [FEAT-06] Funnel Conversion & Variant Variance Analytics (Sankey / Reports)    |
|  [FEAT-07] HITL Application Lifecycle & Follow-up Scheduler (Task Engine)       |
|  [FEAT-08] Dynamic Resume & Artifact Generation Engine (Profile Compiler)       |
|  [FEAT-09] Headless API Daemon & Thin-Client Control Plane (FastAPI / jobctl)   |
+---------------------------------------------------------------------------------+
```

## 4. Key Constraints

* **Local Environment:** Must run seamlessly on Linux environments without external cloud database dependencies.
* **Unauthenticated Access:** Must not require user login credentials, cookies, or paid API keys.
* **Rate-Limit Resilience:** Must handle HTTP 429 backoff gracefully with optional proxy rotation.
* **Deterministic Generation:** Resume generation must rely strictly on verified candidate profile nodes without ungrounded hallucinations.
* **API-First Decoupling:** Client interfaces (CLI, Web UI, Cron) must interact with the application core through formal Pydantic/OpenAPI contracts without embedding business logic.
