"""
Update COT Data - Run Weekly to Get Latest Data
Downloads the latest week's COT data from CFTC
"""

from lib.downloader import COTDownloader
from utils.fix_data import combine_year_files
from datetime import datetime


def update_cot_data():
    """Download latest COT data and update files"""

    print("=" * 70)
    print("COT DATA UPDATE")
    print("=" * 70)
    print(f"Update started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize downloader
    downloader = COTDownloader()

    # Download current year data for all report types
    current_year = datetime.now().year
    report_types = ['legacy_fut', 'disaggregated_fut', 'tff_fut']

    print(f"Downloading {current_year} data...")
    print("-" * 70)

    for report_type in report_types:
        try:
            print(f"\nUpdating {report_type}...")
            df = downloader.download_year(report_type, current_year)

            if df is not None:
                print(f"  SUCCESS: Downloaded {len(df):,} records")
            else:
                print(f"  - No new data available yet")

        except Exception as e:
            print(f"  ERROR: {e}")

    # Recombine all years to include latest data
    print("\n" + "=" * 70)
    print("UPDATING COMBINED FILES")
    print("=" * 70)

    for report_type in report_types:
        try:
            print(f"\nCombining {report_type}...")
            combine_year_files(report_type)
        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)
    print()
    print("Latest data is now available for analysis!")
    print("Try: python analyze.py GOLD")
    print()
    print(f"Update finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    update_cot_data()
