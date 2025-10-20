"""
COT Analysis Module
Comprehensive analysis tools for Commitment of Traders data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta


class COTAnalyzer:
    """Analyze COT data for trading signals and market sentiment"""

    def __init__(self, data_dir='data'):
        """Initialize analyzer"""
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / 'processed'

    def load_processed_data(self, report_type):
        """Load processed COT data"""
        file_path = self.processed_dir / f'{report_type}_processed.parquet'
        if not file_path.exists():
            raise FileNotFoundError(
                f"Processed data not found: {file_path}\n"
                "Run cot_processor.py first to process the data."
            )
        return pd.read_parquet(file_path)

    def get_commodity_data(self, commodity, report_type='disaggregated_fut'):
        """Get data for a specific commodity"""
        df = self.load_processed_data(report_type)

        if 'commodity' in df.columns:
            data = df[df['commodity'] == commodity].copy()
        else:
            data = df[df['cftc_code'] == commodity].copy()

        if data.empty:
            raise ValueError(f"No data found for commodity: {commodity}")

        return data.sort_values('report_date').reset_index(drop=True)

    def calculate_cot_index(self, df, position_col, lookback_period=156):
        """
        Calculate COT Index (0-100 scale)
        Shows current position relative to historical range
        100 = most bullish, 0 = most bearish
        """
        def calc_index(series, window):
            min_val = series.rolling(window=window, min_periods=window).min()
            max_val = series.rolling(window=window, min_periods=window).max()
            current = series

            # Calculate index (0-100)
            index = ((current - min_val) / (max_val - min_val)) * 100
            return index

        df[f'{position_col}_index_{lookback_period}'] = calc_index(
            df[position_col], lookback_period
        )
        return df

    def calculate_extremes(self, df, position_col, lookback_period=156, threshold=90):
        """
        Identify extreme positions
        Returns signals when positions reach historical extremes
        """
        df = self.calculate_cot_index(df, position_col, lookback_period)

        index_col = f'{position_col}_index_{lookback_period}'

        # Create signals
        df[f'{position_col}_extreme_bullish'] = df[index_col] >= threshold
        df[f'{position_col}_extreme_bearish'] = df[index_col] <= (100 - threshold)

        return df

    def calculate_sentiment_score(self, df, report_type='disaggregated_fut'):
        """
        Calculate overall sentiment score based on trader positioning
        Returns -100 to +100 (bearish to bullish)
        """
        if report_type == 'legacy_fut':
            if 'noncomm_net_pct' in df.columns:
                # For legacy, use spec net position as percentage
                df['sentiment_score'] = df['noncomm_net_pct']

        elif report_type == 'disaggregated_fut':
            if 'managed_money_net_pct' in df.columns:
                # For disaggregated, focus on managed money
                df['sentiment_score'] = df['managed_money_net_pct']

        elif report_type == 'tff_fut':
            if 'lev_money_net_pct' in df.columns:
                # For TFF, use leveraged money
                df['sentiment_score'] = df['lev_money_net_pct']

        return df

    def calculate_commitment_index(self, df, report_type='disaggregated_fut'):
        """
        Calculate commitment index showing strength of positioning
        Higher values indicate stronger commitment (regardless of direction)
        """
        if report_type == 'legacy_fut':
            if 'noncomm_long_pct' in df.columns and 'noncomm_short_pct' in df.columns:
                df['commitment_index'] = (
                    df['noncomm_long_pct'] + df['noncomm_short_pct']
                )

        elif report_type == 'disaggregated_fut':
            if 'managed_money_long_pct' in df.columns and 'managed_money_short_pct' in df.columns:
                df['commitment_index'] = (
                    df['managed_money_long_pct'] + df['managed_money_short_pct']
                )

        return df

    def detect_position_reversals(self, df, position_col, threshold=0):
        """
        Detect when net position crosses from long to short or vice versa
        """
        df[f'{position_col}_reversal'] = False

        # Detect sign changes
        shifted = df[position_col].shift(1)
        df[f'{position_col}_reversal'] = (
            (df[position_col] > threshold) & (shifted <= threshold) |
            (df[position_col] < -threshold) & (shifted >= -threshold)
        )

        return df

    def calculate_willco_indicator(self, df, position_col, price_col=None):
        """
        Williams COT (WillCo) indicator
        Measures the relationship between price and positioning
        """
        if price_col and price_col in df.columns:
            # Calculate correlation between position and price
            window = 52  # One year of weekly data

            df['willco'] = (
                df[position_col]
                .rolling(window=window)
                .corr(df[price_col])
            )

        return df

    def analyze_commercial_hedger_activity(self, df, report_type='disaggregated_fut'):
        """
        Analyze commercial/hedger positioning
        Commercials are typically contrarian indicators
        """
        if report_type == 'legacy_fut':
            if 'comm_net' in df.columns:
                df = self.calculate_cot_index(df, 'comm_net', 156)
                df['commercial_signal'] = np.where(
                    df['comm_net_index_156'] > 70, 'BULLISH',
                    np.where(df['comm_net_index_156'] < 30, 'BEARISH', 'NEUTRAL')
                )

        elif report_type == 'disaggregated_fut':
            if 'producer_net' in df.columns:
                df = self.calculate_cot_index(df, 'producer_net', 156)
                df['producer_signal'] = np.where(
                    df['producer_net_index_156'] > 70, 'BULLISH',
                    np.where(df['producer_net_index_156'] < 30, 'BEARISH', 'NEUTRAL')
                )

        return df

    def analyze_spec_activity(self, df, report_type='disaggregated_fut'):
        """
        Analyze speculator positioning
        Large spec positions often mark extremes
        """
        if report_type == 'legacy_fut':
            if 'noncomm_net' in df.columns:
                df = self.calculate_extremes(df, 'noncomm_net', 156, 85)

        elif report_type == 'disaggregated_fut':
            if 'managed_money_net' in df.columns:
                df = self.calculate_extremes(df, 'managed_money_net', 156, 85)

        elif report_type == 'tff_fut':
            if 'lev_money_net' in df.columns:
                df = self.calculate_extremes(df, 'lev_money_net', 156, 85)

        return df

    def get_latest_positions(self, commodity, report_type='disaggregated_fut'):
        """Get the most recent COT positions for a commodity"""
        df = self.get_commodity_data(commodity, report_type)

        if df.empty:
            return None

        latest = df.iloc[-1]

        result = {
            'commodity': commodity,
            'report_date': latest.get('report_date'),
            'open_interest': latest.get('open_interest'),
        }

        if report_type == 'legacy_fut':
            result.update({
                'noncomm_long': latest.get('noncomm_long'),
                'noncomm_short': latest.get('noncomm_short'),
                'noncomm_net': latest.get('noncomm_net'),
                'comm_long': latest.get('comm_long'),
                'comm_short': latest.get('comm_short'),
                'comm_net': latest.get('comm_net'),
            })

        elif report_type == 'disaggregated_fut':
            result.update({
                'managed_money_long': latest.get('managed_money_long'),
                'managed_money_short': latest.get('managed_money_short'),
                'managed_money_net': latest.get('managed_money_net'),
                'producer_long': latest.get('producer_long'),
                'producer_short': latest.get('producer_short'),
                'producer_net': latest.get('producer_net'),
                'swap_long': latest.get('swap_long'),
                'swap_short': latest.get('swap_short'),
                'swap_net': latest.get('swap_net'),
            })

        elif report_type == 'tff_fut':
            result.update({
                'lev_money_long': latest.get('lev_money_long'),
                'lev_money_short': latest.get('lev_money_short'),
                'lev_money_net': latest.get('lev_money_net'),
                'asset_mgr_long': latest.get('asset_mgr_long'),
                'asset_mgr_short': latest.get('asset_mgr_short'),
                'asset_mgr_net': latest.get('asset_mgr_net'),
            })

        return result

    def comprehensive_analysis(self, commodity, report_type='disaggregated_fut'):
        """
        Perform comprehensive COT analysis on a commodity
        Returns analyzed dataframe and summary statistics
        """
        df = self.get_commodity_data(commodity, report_type)

        # Apply all analysis functions
        df = self.calculate_sentiment_score(df, report_type)
        df = self.calculate_commitment_index(df, report_type)
        df = self.analyze_commercial_hedger_activity(df, report_type)
        df = self.analyze_spec_activity(df, report_type)

        # Additional calculations based on report type
        if report_type == 'disaggregated_fut' and 'managed_money_net' in df.columns:
            df = self.detect_position_reversals(df, 'managed_money_net')

        # Get summary statistics
        latest = df.iloc[-1]
        summary = {
            'commodity': commodity,
            'report_type': report_type,
            'latest_date': latest.get('report_date'),
            'data_points': len(df),
            'date_range': f"{df['report_date'].min()} to {df['report_date'].max()}",
        }

        # Add latest values
        if 'sentiment_score' in df.columns:
            summary['latest_sentiment'] = latest.get('sentiment_score')

        if 'commitment_index' in df.columns:
            summary['latest_commitment'] = latest.get('commitment_index')

        return df, summary

    def compare_trader_groups(self, commodity, report_type='disaggregated_fut'):
        """
        Compare positioning across different trader groups
        """
        df = self.get_commodity_data(commodity, report_type)
        latest = df.iloc[-1]

        comparison = {'commodity': commodity, 'date': latest.get('report_date')}

        if report_type == 'disaggregated_fut':
            comparison.update({
                'managed_money_net': latest.get('managed_money_net'),
                'producer_net': latest.get('producer_net'),
                'swap_net': latest.get('swap_net'),
                'other_net': latest.get('other_rept_net'),
            })

        elif report_type == 'tff_fut':
            comparison.update({
                'lev_money_net': latest.get('lev_money_net'),
                'asset_mgr_net': latest.get('asset_mgr_net'),
                'dealer_net': latest.get('dealer_net'),
                'other_net': latest.get('other_rept_net'),
            })

        return pd.Series(comparison)


def main():
    """Example usage"""
    analyzer = COTAnalyzer()

    # Analyze gold
    commodity = 'GOLD'
    print(f"\n{'='*60}")
    print(f"COT Analysis for {commodity}")
    print(f"{'='*60}\n")

    try:
        # Get latest positions
        latest = analyzer.get_latest_positions(commodity, 'disaggregated_fut')
        print("Latest Positions:")
        for key, value in latest.items():
            print(f"  {key}: {value}")

        # Comprehensive analysis
        df, summary = analyzer.comprehensive_analysis(commodity, 'disaggregated_fut')
        print("\nAnalysis Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # Compare trader groups
        comparison = analyzer.compare_trader_groups(commodity, 'disaggregated_fut')
        print("\nTrader Group Comparison:")
        print(comparison)

    except Exception as e:
        print(f"Error analyzing {commodity}: {e}")


if __name__ == "__main__":
    main()
