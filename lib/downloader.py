"""
COT Data Downloader Module
Downloads historical Commitment of Traders data from CFTC
"""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path
import zipfile
import io
from tqdm import tqdm


class COTDownloader:
    """Download and manage CFTC Commitment of Traders data"""

    # CFTC data URLs - Updated for 2025
    BASE_URL = "https://www.cftc.gov/files/dea/history/"

    # Alternative base URL (sometimes CFTC switches between these)
    ALT_BASE_URL = "https://www.cftc.gov/sites/default/files/files/dea/history/"

    REPORT_TYPES = {
        'legacy_fut': {
            'name': 'Legacy Futures Only',
            'url_pattern': 'deacot{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/deacot_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/deacot_current.zip',
            'file_pattern': 'annual.txt',
            'start_year': 1986
        },
        'legacy_combined': {
            'name': 'Legacy Futures and Options Combined',
            'url_pattern': 'deahistfo{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/deahistfo_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/deahistfo_current.zip',
            'file_pattern': 'annualof.txt',
            'start_year': 1995
        },
        'disaggregated_fut': {
            'name': 'Disaggregated Futures Only',
            'url_pattern': 'fut_disagg_txt_{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/fut_disagg_txt_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/fut_disagg_txt_current.zip',
            'file_pattern': 'f_year.txt',
            'start_year': 2006
        },
        'disaggregated_combined': {
            'name': 'Disaggregated Futures and Options Combined',
            'url_pattern': 'com_disagg_txt_{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/com_disagg_txt_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/com_disagg_txt_current.zip',
            'file_pattern': 'c_year.txt',
            'start_year': 2006
        },
        'tff_fut': {
            'name': 'Traders in Financial Futures - Futures Only',
            'url_pattern': 'fut_fin_txt_{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/fut_fin_txt_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/fut_fin_txt_current.zip',
            'file_pattern': 'f_year.txt',
            'start_year': 2006
        },
        'tff_combined': {
            'name': 'Traders in Financial Futures - Combined',
            'url_pattern': 'com_fin_txt_{year}.zip',
            'current_url': 'https://www.cftc.gov/files/dea/cotarchives/com_fin_txt_current.zip',
            'alt_current_url': 'https://www.cftc.gov/sites/default/files/files/dea/cotarchives/com_fin_txt_current.zip',
            'file_pattern': 'c_year.txt',
            'start_year': 2006
        }
    }

    def __init__(self, data_dir='data'):
        """Initialize downloader with data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Create subdirectories for each report type
        for report_type in self.REPORT_TYPES.keys():
            (self.data_dir / report_type).mkdir(exist_ok=True)

    def download_year(self, report_type, year):
        """Download COT data for a specific year and report type"""
        if report_type not in self.REPORT_TYPES:
            raise ValueError(f"Invalid report type: {report_type}")

        report_config = self.REPORT_TYPES[report_type]

        # Check if year is valid
        if year < report_config['start_year']:
            # Silently skip years before data availability
            return None

        # Check if file already exists
        output_file = self.data_dir / report_type / f"{year}.parquet"
        if output_file.exists():
            print(f"Loading cached {report_config['name']} for {year}...")
            return pd.read_parquet(output_file)

        # Construct URL - try current year URLs first, then historical
        urls_to_try = []

        if year == datetime.now().year:
            # Try current URLs with fallbacks
            urls_to_try.extend([
                report_config['current_url'],
                report_config.get('alt_current_url'),
                self.BASE_URL + report_config['url_pattern'].format(year=year),
                self.ALT_BASE_URL + report_config['url_pattern'].format(year=year)
            ])
        else:
            # Try historical URLs
            urls_to_try.extend([
                self.BASE_URL + report_config['url_pattern'].format(year=year),
                self.ALT_BASE_URL + report_config['url_pattern'].format(year=year)
            ])

        # Remove None values
        urls_to_try = [url for url in urls_to_try if url]

        # Try each URL until one works
        for url_index, url in enumerate(urls_to_try):
            try:
                if url_index == 0:
                    print(f"Downloading {report_config['name']} for {year}...")

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Extract zip file
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    # Find the data file
                    txt_files = [f for f in zip_file.namelist() if f.endswith('.txt')]

                    if not txt_files:
                        print(f"No data files found in archive for {year}")
                        continue

                    # Read the first text file
                    with zip_file.open(txt_files[0]) as f:
                        df = pd.read_csv(f, low_memory=False)

                    # Save to parquet for efficient storage
                    df.to_parquet(output_file, index=False)

                    print(f"Saved {len(df)} records to {output_file}")
                    return df

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # 404 errors are expected for current year sometimes
                    if url_index == len(urls_to_try) - 1:
                        # Only show warning on last attempt
                        if year == datetime.now().year:
                            print(f"Note: {year} data not yet available (will use latest complete year)")
                        else:
                            print(f"Warning: {year} data not found at any URL")
                    continue
                else:
                    if url_index == len(urls_to_try) - 1:
                        print(f"HTTP Error downloading {year}: {e}")
                    continue
            except requests.exceptions.RequestException as e:
                if url_index == len(urls_to_try) - 1:
                    print(f"Network error downloading {year}: {e}")
                continue
            except Exception as e:
                if url_index == len(urls_to_try) - 1:
                    print(f"Error processing {year}: {e}")
                continue

        return None

    def download_all_years(self, report_type, start_year=None, end_year=None):
        """Download all available years for a report type"""
        if report_type not in self.REPORT_TYPES:
            raise ValueError(f"Invalid report type: {report_type}")

        report_config = self.REPORT_TYPES[report_type]

        if start_year is None:
            start_year = report_config['start_year']
        if end_year is None:
            end_year = datetime.now().year

        print(f"\nDownloading {report_config['name']}")
        print(f"Years: {start_year} to {end_year}")
        print("-" * 60)

        all_data = []
        for year in tqdm(range(start_year, end_year + 1)):
            df = self.download_year(report_type, year)
            if df is not None:
                all_data.append(df)

        if all_data:
            # Combine all years
            combined_df = pd.concat(all_data, ignore_index=True)

            # Save combined file
            output_file = self.data_dir / report_type / "all_years.parquet"
            combined_df.to_parquet(output_file, index=False)
            print(f"\nCombined file saved: {output_file}")
            print(f"Total records: {len(combined_df)}")

            return combined_df

        return None

    def download_all_reports(self, start_year=None, report_types=None):
        """
        Download all report types

        Args:
            start_year: Year to start downloading from (None = from beginning)
            report_types: List of report types to download (None = all main types)
        """
        # Default to the three main report types (one from each category)
        if report_types is None:
            report_types = ['legacy_fut', 'disaggregated_fut', 'tff_fut']

        print("=" * 60)
        print("DOWNLOADING COT REPORTS")
        print("=" * 60)
        print(f"Report types: {', '.join(report_types)}")
        print("=" * 60)

        for report_type in report_types:
            if report_type not in self.REPORT_TYPES:
                print(f"Warning: Unknown report type '{report_type}', skipping...")
                continue

            try:
                self.download_all_years(report_type, start_year=start_year)
            except Exception as e:
                print(f"Error downloading {report_type}: {e}")

        print("\n" + "=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)

    def load_report(self, report_type, year=None):
        """Load a previously downloaded report"""
        if year is None:
            file_path = self.data_dir / report_type / "all_years.parquet"
        else:
            file_path = self.data_dir / report_type / f"{year}.parquet"

        if not file_path.exists():
            raise FileNotFoundError(f"Report not found: {file_path}")

        return pd.read_parquet(file_path)

    def get_available_reports(self):
        """List all downloaded reports"""
        available = {}
        for report_type in self.REPORT_TYPES.keys():
            report_dir = self.data_dir / report_type
            if report_dir.exists():
                files = list(report_dir.glob("*.parquet"))
                if files:
                    available[report_type] = [f.stem for f in files]
        return available


def main():
    """Example usage"""
    downloader = COTDownloader()

    # Download all reports from 2020 onwards (faster for testing)
    # For full historical data, use: downloader.download_all_reports()
    downloader.download_all_reports(start_year=2020)

    # Check what's available
    available = downloader.get_available_reports()
    print("\nAvailable reports:")
    for report_type, files in available.items():
        print(f"  {report_type}: {files}")


if __name__ == "__main__":
    main()
