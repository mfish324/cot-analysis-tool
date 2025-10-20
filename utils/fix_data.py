"""
Quick fix: Combine downloaded year files into all_years.parquet
"""

import pandas as pd
from pathlib import Path

def combine_year_files(report_type):
    """Combine individual year files into all_years.parquet"""

    data_dir = Path('data') / report_type

    if not data_dir.exists():
        print(f"Directory not found: {data_dir}")
        return

    # Find all year files (exclude all_years.parquet)
    year_files = sorted([f for f in data_dir.glob('*.parquet')
                        if f.name != 'all_years.parquet'])

    if not year_files:
        print(f"No year files found in {data_dir}")
        return

    print(f"\nCombining {report_type}...")
    print(f"Found {len(year_files)} year files")

    # Load and combine all years
    all_data = []
    for file in year_files:
        print(f"  Loading {file.name}...")
        df = pd.read_parquet(file)
        all_data.append(df)

    # Combine
    combined_df = pd.concat(all_data, ignore_index=True)

    # Clean numeric columns that might have string values
    # Convert columns that should be numeric
    for col in combined_df.columns:
        if combined_df[col].dtype == 'object':
            try:
                # Try to convert to numeric (coerce errors to NaN)
                cleaned_col = pd.to_numeric(
                    combined_df[col].astype(str).str.strip(),
                    errors='coerce'
                )
                # Only replace if conversion was successful (not all NaN)
                if not cleaned_col.isna().all():
                    combined_df[col] = cleaned_col
            except Exception:
                pass  # Keep as string if conversion fails

    # Save
    output_file = data_dir / 'all_years.parquet'
    combined_df.to_parquet(output_file, index=False)

    print(f"SAVED {len(combined_df):,} records to {output_file}")
    return combined_df


def main():
    print("=" * 60)
    print("FIXING DATA FILES")
    print("=" * 60)

    # Check which report types have data
    data_dir = Path('data')
    report_types = ['legacy_fut', 'legacy_combined', 'disaggregated_fut',
                   'disaggregated_combined', 'tff_fut', 'tff_combined']

    fixed = []
    for report_type in report_types:
        report_dir = data_dir / report_type
        if report_dir.exists():
            year_files = list(report_dir.glob('[0-9]*.parquet'))
            all_years = report_dir / 'all_years.parquet'

            if year_files and not all_years.exists():
                print(f"\nNeed to combine: {report_type}")
                combine_year_files(report_type)
                fixed.append(report_type)
            elif all_years.exists():
                print(f"OK {report_type}: all_years.parquet already exists")

    print("\n" + "=" * 60)
    if fixed:
        print(f"FIXED {len(fixed)} report types")
        print("\nYou can now run:")
        print("  python cot_analysis.py --list")
    else:
        print("All data files look good!")
    print("=" * 60)


if __name__ == "__main__":
    main()
