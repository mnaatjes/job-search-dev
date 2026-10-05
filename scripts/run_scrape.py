#!/usr/bin/env python3
"""
CLI runner script to execute multi-board job scrapes via JobSpy adhering to ADR 0001.
"""

from __future__ import annotations

import argparse
import sys
import csv
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from jobspy import scrape_jobs

from job_search_dev.storage import (
    get_report_path,
    save_raw_scrapes,
    slugify,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape jobs across platforms using JobSpy.")
    parser.add_argument(
        "--term", "-t", type=str, default="Software Engineer", help="Job search query"
    )
    parser.add_argument(
        "--location", "-l", type=str, default="Remote", help="Location or 'Remote'"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=10, help="Number of results per board"
    )
    parser.add_argument(
        "--hours", type=int, default=72, help="Max age of posting in hours"
    )
    parser.add_argument(
        "--sites",
        nargs="+",
        default=["indeed", "zip_recruiter", "linkedin"],
        help="List of sites to scrape (indeed, zip_recruiter, linkedin, glassdoor, google)",
    )
    parser.add_argument(
        "--is-remote", action="store_true", default=False, help="Filter for remote positions"
    )
    parser.add_argument(
        "--job-type",
        type=str,
        default=None,
        choices=["fulltime", "parttime", "contract", "internship"],
        help="Filter by employment type",
    )
    parser.add_argument(
        "--out", "-o", type=str, default=None, help="Custom export output path (optional)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    ts = datetime.now(timezone.utc)

    print(
        f"[*] Starting scrape for '{args.term}' in '{args.location}' "
        f"(remote={args.is_remote}, job_type={args.job_type}) across: {args.sites}..."
    )

    try:
        jobs: pd.DataFrame = scrape_jobs(
            site_name=args.sites,
            search_term=args.term,
            location=args.location,
            is_remote=args.is_remote,
            job_type=args.job_type,
            results_wanted=args.limit,
            hours_old=args.hours,
            country_indeed="USA",
            verbose=1,
        )
    except Exception as exc:
        print(f"[!] Scrape execution failed: {exc}", file=sys.stderr)
        return 1

    if jobs.empty:
        print("[!] No jobs found matching criteria.")
        return 0

    print(f"[+] Successfully scraped {len(jobs)} postings.")

    # 1. Persist raw partitioned payloads per ADR 0001 (data/raw/<site>/YYYY-MM-DD/)
    saved_raw_paths = save_raw_scrapes(
        df=jobs,
        base_dir=project_root,
        term=args.term,
        location=args.location,
        timestamp=ts,
    )
    for raw_path in saved_raw_paths:
        print(f"[+] Raw payload stored: {raw_path.relative_to(project_root)}")

    # 2. Persist consolidated export report (data/reports/exports/)
    if args.out:
        report_path = Path(args.out)
    else:
        filter_slug = f"{slugify(args.term)}-{slugify(args.location)}"
        report_path = get_report_path(
            base_dir=project_root,
            report_name="scraped-jobs",
            filter_slug=filter_slug,
            timestamp=ts,
            ext="csv",
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.suffix.lower() == ".json":
        jobs.to_json(report_path, orient="records", indent=2)
    else:
        jobs.to_csv(
            report_path,
            quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\",
            index=False,
        )

    print(f"[+] Consolidated report written: {report_path.relative_to(project_root) if report_path.is_relative_to(project_root) else report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
