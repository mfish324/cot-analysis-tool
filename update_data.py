"""
Update COT Data - Run Weekly to Get Latest Data
Downloads the latest week's COT data from CFTC.

Refreshes both current year and prior year (prior-year reports for
late November/December can finalize after the year boundary). Writes
a log file and exits non-zero on errors so a scheduled task surfaces
silent failures.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from lib.downloader import COTDownloader
from utils.fix_data import combine_year_files


REPORT_TYPES = ['legacy_fut', 'disaggregated_fut', 'tff_fut']
STALE_AFTER_DAYS = 14
LOG_FILE = Path(__file__).parent / 'logs' / 'update_data.log'


def setup_logging():
    LOG_FILE.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def latest_report_date(report_type):
    combined = Path('data') / report_type / 'all_years.parquet'
    if not combined.exists():
        return None
    df = pd.read_parquet(combined, columns=None)
    date_col = next((c for c in df.columns if 'YYYY-MM-DD' in c), None)
    if date_col is None:
        return None
    return pd.to_datetime(df[date_col]).max().date()


def update_cot_data():
    setup_logging()
    log = logging.getLogger(__name__)

    log.info("=" * 70)
    log.info("COT DATA UPDATE")
    log.info("=" * 70)

    downloader = COTDownloader()
    current_year = datetime.now().year
    years_to_refresh = [current_year - 1, current_year]
    errors = []

    for year in years_to_refresh:
        log.info(f"Refreshing {year} data...")
        for report_type in REPORT_TYPES:
            try:
                df = downloader.download_year(report_type, year, force=True)
                if df is not None:
                    log.info(f"  {report_type} {year}: {len(df):,} records")
                else:
                    log.info(f"  {report_type} {year}: no data available")
            except Exception as e:
                msg = f"  {report_type} {year}: ERROR {e}"
                log.error(msg)
                errors.append(msg)

    log.info("Combining year files...")
    for report_type in REPORT_TYPES:
        try:
            combine_year_files(report_type)
        except Exception as e:
            msg = f"  combine {report_type}: ERROR {e}"
            log.error(msg)
            errors.append(msg)

    log.info("=" * 70)
    log.info("FRESHNESS CHECK")
    log.info("=" * 70)
    stale = []
    today = datetime.now().date()
    for report_type in REPORT_TYPES:
        latest = latest_report_date(report_type)
        if latest is None:
            log.warning(f"  {report_type}: no combined data found")
            stale.append(report_type)
            continue
        age = (today - latest).days
        marker = "STALE" if age > STALE_AFTER_DAYS else "OK"
        log.info(f"  {report_type}: latest={latest} (age {age}d) {marker}")
        if age > STALE_AFTER_DAYS:
            stale.append(report_type)

    if errors:
        log.error(f"UPDATE FAILED with {len(errors)} error(s)")
        sys.exit(1)
    if stale:
        log.warning(f"UPDATE COMPLETE but data is STALE for: {', '.join(stale)}")
        sys.exit(2)
    log.info("UPDATE COMPLETE — all report types current")


if __name__ == "__main__":
    update_cot_data()
