"""
Data pipeline storage layout and path generation utilities (ADR 0001).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import pandas as pd


def slugify(text: str) -> str:
    """
    Convert text into an alphanumeric hyphen-separated slug.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-") or "default"


def get_raw_scrape_path(
    base_dir: Path | str,
    source: str,
    term: str,
    location: str,
    timestamp: datetime | None = None,
    ext: str = "jsonl",
) -> Path:
    """
    Generate ADR 0001 compliant path for raw scrape payloads:
    data/raw/<source>/YYYY-MM-DD/YYYYMMDDTHHMMSSZ_<source>_<query-slug>_<location-slug>.<ext>
    """
    base_path = Path(base_dir)
    ts = timestamp or datetime.now(timezone.utc)
    date_partition = ts.strftime("%Y-%m-%d")
    ts_str = ts.strftime("%Y%m%dT%H%M%SZ")

    source_slug = slugify(source)
    term_slug = slugify(term)
    location_slug = slugify(location)

    filename = f"{ts_str}_{source_slug}_{term_slug}_{location_slug}.{ext.lstrip('.')}"
    return base_path / "data" / "raw" / source_slug / date_partition / filename


def get_report_path(
    base_dir: Path | str,
    report_name: str,
    filter_slug: str,
    timestamp: datetime | None = None,
    ext: str = "csv",
) -> Path:
    """
    Generate ADR 0001 compliant path for report exports:
    data/reports/exports/YYYY-MM-DD_<report-name>_<filter-slug>.<ext>
    """
    base_path = Path(base_dir)
    ts = timestamp or datetime.now(timezone.utc)
    date_str = ts.strftime("%Y-%m-%d")

    rep_slug = slugify(report_name)
    filt_slug = slugify(filter_slug)

    filename = f"{date_str}_{rep_slug}_{filt_slug}.{ext.lstrip('.')}"
    return base_path / "data" / "reports" / "exports" / filename


def save_raw_scrapes(
    df: pd.DataFrame,
    base_dir: Path | str,
    term: str,
    location: str,
    timestamp: datetime | None = None,
) -> List[Path]:
    """
    Partition dataframe by 'site' column and save raw JSONL files per ADR 0001.
    """
    if df.empty:
        return []

    ts = timestamp or datetime.now(timezone.utc)
    saved_paths: List[Path] = []

    for site, site_df in df.groupby("site"):
        target_path = get_raw_scrape_path(
            base_dir=base_dir,
            source=str(site),
            term=term,
            location=location,
            timestamp=ts,
            ext="jsonl",
        )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        site_df.to_json(target_path, orient="records", lines=True, date_format="iso")
        saved_paths.append(target_path)

    return saved_paths
