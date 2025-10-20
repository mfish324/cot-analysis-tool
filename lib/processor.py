"""
COT Data Processing Module
Process and standardize COT data for analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path


class COTProcessor:
    """Process and standardize COT data"""

    # Common commodity mappings (CFTC codes to readable names)
    COMMODITY_MAPPING = {
        # Energies
        '067651': 'CRUDE_OIL_WTI',
        '023651': 'NATURAL_GAS',
        '022651': 'HEATING_OIL',
        '026651': 'GASOLINE',

        # Metals
        '088691': 'GOLD',
        '084691': 'SILVER',
        '085692': 'COPPER',
        '076651': 'PLATINUM',
        '075651': 'PALLADIUM',

        # Agricultures
        '002602': 'CORN',
        '005602': 'SOYBEANS',
        '001602': 'WHEAT',
        '004603': 'SOYBEAN_OIL',
        '007602': 'SOYBEAN_MEAL',
        '080732': 'LIVE_CATTLE',
        '054642': 'LEAN_HOGS',
        '033661': 'COFFEE',
        '080651': 'SUGAR',
        '073732': 'COCOA',
        '033874': 'COTTON',

        # Financials
        '13874A': 'EUR',
        '099741': 'JPY',
        '096742': 'GBP',
        '092741': 'CHF',
        '090741': 'CAD',
        '095741': 'AUD',

        # Indices
        '13874+': 'SP500',
        '239742': 'NASDAQ',
        '124603': 'DOW',
        '097741': 'VIX',

        # Bonds
        '020601': 'T_BONDS',
        '042601': 'T_NOTES_10Y',
        '044601': 'T_NOTES_5Y',
        '043602': 'T_NOTES_2Y',
    }

    def __init__(self, data_dir='data'):
        """Initialize processor with data directory"""
        self.data_dir = Path(data_dir)

    def standardize_column_names(self, df, report_type):
        """Standardize column names across different report types"""
        # Common standardizations
        column_map = {
            'Market_and_Exchange_Names': 'market_name',
            'Report_Date_as_YYYY-MM-DD': 'report_date',
            'Report_Date_as_MM_DD_YYYY': 'report_date',
            'CFTC_Contract_Market_Code': 'cftc_code',
            'CFTC_Market_Code': 'cftc_code',
            'Open_Interest_All': 'open_interest',
            'Open Interest (All)': 'open_interest',
        }

        # Legacy report specifics
        if 'legacy' in report_type:
            column_map.update({
                'NonComm_Positions_Long_All': 'noncomm_long',
                'NonComm_Positions_Short_All': 'noncomm_short',
                'Comm_Positions_Long_All': 'comm_long',
                'Comm_Positions_Short_All': 'comm_short',
                'NonRept_Positions_Long_All': 'nonrept_long',
                'NonRept_Positions_Short_All': 'nonrept_short',
            })

        # Disaggregated report specifics
        if 'disaggregated' in report_type:
            column_map.update({
                'Prod_Merc_Positions_Long_All': 'producer_long',
                'Prod_Merc_Positions_Short_All': 'producer_short',
                'Swap_Positions_Long_All': 'swap_long',
                'Swap__Positions_Short_All': 'swap_short',
                'M_Money_Positions_Long_All': 'managed_money_long',
                'M_Money_Positions_Short_All': 'managed_money_short',
                'Other_Rept_Positions_Long_All': 'other_rept_long',
                'Other_Rept_Positions_Short_All': 'other_rept_short',
            })

        # TFF report specifics
        if 'tff' in report_type:
            column_map.update({
                'Dealer_Positions_Long_All': 'dealer_long',
                'Dealer_Positions_Short_All': 'dealer_short',
                'Asset_Mgr_Positions_Long_All': 'asset_mgr_long',
                'Asset_Mgr_Positions_Short_All': 'asset_mgr_short',
                'Lev_Money_Positions_Long_All': 'lev_money_long',
                'Lev_Money_Positions_Short_All': 'lev_money_short',
                'Other_Rept_Positions_Long_All': 'other_rept_long',
                'Other_Rept_Positions_Short_All': 'other_rept_short',
            })

        # Rename columns that exist
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

        return df

    def process_report(self, df, report_type):
        """Process and clean COT report data"""
        # Standardize column names
        df = self.standardize_column_names(df, report_type)

        # Convert report_date to datetime
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])

        # Add readable commodity names
        if 'cftc_code' in df.columns:
            df['commodity'] = df['cftc_code'].astype(str).map(self.COMMODITY_MAPPING)

        # Sort by date
        if 'report_date' in df.columns:
            df = df.sort_values('report_date')

        return df

    def calculate_net_positions(self, df, report_type):
        """Calculate net positions for each trader category"""
        if 'legacy' in report_type:
            if 'noncomm_long' in df.columns:
                df['noncomm_net'] = df['noncomm_long'] - df['noncomm_short']
            if 'comm_long' in df.columns:
                df['comm_net'] = df['comm_long'] - df['comm_short']

        elif 'disaggregated' in report_type:
            if 'managed_money_long' in df.columns:
                df['managed_money_net'] = df['managed_money_long'] - df['managed_money_short']
            if 'producer_long' in df.columns:
                df['producer_net'] = df['producer_long'] - df['producer_short']
            if 'swap_long' in df.columns:
                df['swap_net'] = df['swap_long'] - df['swap_short']

        elif 'tff' in report_type:
            if 'lev_money_long' in df.columns:
                df['lev_money_net'] = df['lev_money_long'] - df['lev_money_short']
            if 'asset_mgr_long' in df.columns:
                df['asset_mgr_net'] = df['asset_mgr_long'] - df['asset_mgr_short']
            if 'dealer_long' in df.columns:
                df['dealer_net'] = df['dealer_long'] - df['dealer_short']

        return df

    def calculate_percentages(self, df, report_type):
        """Calculate positions as percentage of open interest"""
        if 'open_interest' not in df.columns or df['open_interest'].isna().all():
            return df

        # Avoid division by zero
        oi = df['open_interest'].replace(0, np.nan)

        if 'legacy' in report_type:
            if 'noncomm_long' in df.columns:
                df['noncomm_long_pct'] = (df['noncomm_long'] / oi) * 100
                df['noncomm_short_pct'] = (df['noncomm_short'] / oi) * 100
                df['noncomm_net_pct'] = (df['noncomm_net'] / oi) * 100 if 'noncomm_net' in df.columns else None

        elif 'disaggregated' in report_type:
            if 'managed_money_long' in df.columns:
                df['managed_money_long_pct'] = (df['managed_money_long'] / oi) * 100
                df['managed_money_short_pct'] = (df['managed_money_short'] / oi) * 100
                df['managed_money_net_pct'] = (df['managed_money_net'] / oi) * 100 if 'managed_money_net' in df.columns else None

        elif 'tff' in report_type:
            if 'lev_money_long' in df.columns:
                df['lev_money_long_pct'] = (df['lev_money_long'] / oi) * 100
                df['lev_money_short_pct'] = (df['lev_money_short'] / oi) * 100
                df['lev_money_net_pct'] = (df['lev_money_net'] / oi) * 100 if 'lev_money_net' in df.columns else None

        return df

    def calculate_changes(self, df, periods=[1, 4, 13, 26]):
        """Calculate week-over-week changes for specified periods"""
        # Group by commodity and calculate changes
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Filter out columns we don't want to calculate changes for
        cols_to_change = [col for col in numeric_cols if col not in ['cftc_code', 'open_interest']]

        if not cols_to_change:
            return df

        # Determine grouping column
        if 'commodity' in df.columns and df['commodity'].notna().any():
            group_col = 'commodity'
        elif 'cftc_code' in df.columns:
            group_col = 'cftc_code'
        else:
            group_col = None

        # Calculate all changes at once using concat to avoid fragmentation
        change_dfs = []

        for period in periods:
            if group_col:
                # Calculate changes grouped by commodity
                period_changes = df.groupby(group_col)[cols_to_change].diff(period)
            else:
                # Calculate overall diff
                period_changes = df[cols_to_change].diff(period)

            # Rename columns to include period
            period_changes.columns = [f'{col}_chg_{period}w' for col in period_changes.columns]
            change_dfs.append(period_changes)

        # Combine all change columns at once
        if change_dfs:
            all_changes = pd.concat(change_dfs, axis=1)
            df = pd.concat([df, all_changes], axis=1)

        return df

    def get_commodity_data(self, df, commodity_code):
        """Extract data for a specific commodity"""
        if 'commodity' in df.columns:
            return df[df['commodity'] == commodity_code].copy()
        elif 'cftc_code' in df.columns:
            return df[df['cftc_code'] == commodity_code].copy()
        else:
            raise ValueError("No commodity identifier column found")

    def process_full_pipeline(self, report_type):
        """Run full processing pipeline on a report"""
        from cot_downloader import COTDownloader

        downloader = COTDownloader(self.data_dir)
        df = downloader.load_report(report_type)

        print(f"Processing {report_type}...")
        print(f"Initial shape: {df.shape}")

        # Process
        df = self.process_report(df, report_type)
        df = self.calculate_net_positions(df, report_type)
        df = self.calculate_percentages(df, report_type)
        df = self.calculate_changes(df)

        # Save processed data
        output_dir = self.data_dir / 'processed'
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f'{report_type}_processed.parquet'
        df.to_parquet(output_file, index=False)

        print(f"Processed shape: {df.shape}")
        print(f"Saved to: {output_file}")

        return df

    def get_available_commodities(self, report_type):
        """Get list of available commodities in a report"""
        from cot_downloader import COTDownloader

        downloader = COTDownloader(self.data_dir)
        df = downloader.load_report(report_type)
        df = self.process_report(df, report_type)

        if 'commodity' in df.columns:
            commodities = df['commodity'].dropna().unique()
            return sorted(commodities)
        else:
            return []


def main():
    """Example usage"""
    processor = COTProcessor()

    # Process all report types
    report_types = ['legacy_fut', 'disaggregated_fut', 'tff_fut']

    for report_type in report_types:
        try:
            df = processor.process_full_pipeline(report_type)
            print(f"\nAvailable commodities in {report_type}:")
            commodities = processor.get_available_commodities(report_type)
            print(commodities[:10])  # Show first 10
        except Exception as e:
            print(f"Error processing {report_type}: {e}")


if __name__ == "__main__":
    main()
