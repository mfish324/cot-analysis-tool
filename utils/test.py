"""
Quick test script to verify downloader is working
"""

from cot_downloader import COTDownloader

def test_download():
    print("Testing COT Downloader...")
    print("=" * 60)

    downloader = COTDownloader()

    # Test downloading just 2024 data for one report type
    print("\n1. Testing single year download (2024)...")
    df = downloader.download_year('disaggregated_fut', 2024)

    if df is not None:
        print(f"SUCCESS! Downloaded {len(df)} records")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Date range: {df.iloc[0]['Report_Date_as_YYYY-MM-DD']} to {df.iloc[-1]['Report_Date_as_YYYY-MM-DD']}")
    else:
        print("FAILED to download")

    # Check what's available
    print("\n2. Checking available reports...")
    available = downloader.get_available_reports()

    if available:
        print("Found downloaded reports:")
        for report_type, files in available.items():
            print(f"  {report_type}: {len(files)} files")
    else:
        print("No reports found")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    test_download()
