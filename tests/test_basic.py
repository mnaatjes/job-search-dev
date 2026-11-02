"""
Unit tests for job_search_dev package, JobSpy models, and storage conventions (ADR 0001).
"""

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import pytest
from jobspy.model import JobPost, JobType

import job_search_dev
from job_search_dev.storage import (
    slugify,
    get_raw_scrape_path,
    get_report_path,
    save_raw_scrapes,
)


def test_package_import():
    assert job_search_dev.__version__ == "0.1.0"


def test_jobspy_model_instantiation():
    company_field = "company" if "company" in JobPost.model_fields else "company_name"
    kwargs = {
        "title": "Senior Python Engineer",
        "job_url": "https://example.com/jobs/123",
        "location": None,
        "job_type": [JobType.FULL_TIME],
        "is_remote": True,
        company_field: "Acme Corp",
    }
    post = JobPost(**kwargs)
    assert post.title == "Senior Python Engineer"
    assert getattr(post, company_field) == "Acme Corp"
    assert post.is_remote is True


def test_slugify():
    assert slugify("Senior Software Engineer!") == "senior-software-engineer"
    assert slugify("San Francisco, CA") == "san-francisco-ca"
    assert slugify("   ") == "default"


def test_get_raw_scrape_path_adr0001():
    base_dir = Path("/tmp/job-search-test")
    ts = datetime(2026, 9, 17, 12, 30, 45, tzinfo=timezone.utc)
    path = get_raw_scrape_path(
        base_dir=base_dir,
        source="LinkedIn",
        term="Python Developer",
        location="Remote",
        timestamp=ts,
        ext="jsonl",
    )
    expected = base_dir / "data" / "raw" / "linkedin" / "2026-09-17" / "20260917T123045Z_linkedin_python-developer_remote.jsonl"
    assert path == expected


def test_get_report_path_adr0001():
    base_dir = Path("/tmp/job-search-test")
    ts = datetime(2026, 9, 17, 12, 30, 45, tzinfo=timezone.utc)
    path = get_report_path(
        base_dir=base_dir,
        report_name="Daily Digest",
        filter_slug="senior-remote",
        timestamp=ts,
        ext="csv",
    )
    expected = base_dir / "data" / "reports" / "exports" / "2026-09-17_daily-digest_senior-remote.csv"
    assert path == expected


def test_save_raw_scrapes_partitioning(tmp_path: Path):
    ts = datetime(2026, 9, 17, 10, 0, 0, tzinfo=timezone.utc)
    df = pd.DataFrame(
        [
            {"site": "linkedin", "title": "DevOps Engineer", "company": "Alpha Corp"},
            {"site": "indeed", "title": "SRE", "company": "Beta Inc"},
            {"site": "linkedin", "title": "Cloud Architect", "company": "Gamma LLC"},
        ]
    )
    saved = save_raw_scrapes(
        df=df,
        base_dir=tmp_path,
        term="DevOps",
        location="Remote",
        timestamp=ts,
    )
    assert len(saved) == 2
    for p in saved:
        assert p.exists()
        assert p.suffix == ".jsonl"
