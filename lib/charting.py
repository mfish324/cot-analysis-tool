"""
COT Charting Module
Create visualizations for Commitment of Traders data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime


class COTCharter:
    """Create charts for COT analysis"""

    def __init__(self, output_dir='charts'):
        """Initialize charter with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set default style
        plt.style.use('seaborn-v0_8-darkgrid')

    def create_cot_index_chart(self, market_data, market_name, lookback=156):
        """
        Create COT Index time series chart
        Shows the 0-100 index with overbought/oversold zones
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        # Calculate COT Index
        market_data = market_data.copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data = market_data.sort_values('date')

        # Calculate rolling index
        indices = []
        dates = []

        for i in range(lookback, len(market_data)):
            window_data = market_data.iloc[i-lookback:i+1]
            net_positions = window_data['noncomm_net']

            min_val = net_positions.min()
            max_val = net_positions.max()
            current = net_positions.iloc[-1]

            if max_val != min_val:
                index = ((current - min_val) / (max_val - min_val)) * 100
                indices.append(index)
                dates.append(window_data['date'].iloc[-1])

        # Plot COT Index
        ax.plot(dates, indices, linewidth=2, color='#2E86AB', label='COT Index')

        # Add overbought/oversold zones
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Overbought (80)')
        ax.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='Oversold (20)')
        ax.axhline(y=50, color='gray', linestyle=':', alpha=0.3, label='Neutral (50)')

        # Fill zones
        ax.fill_between(dates, 80, 100, alpha=0.1, color='red')
        ax.fill_between(dates, 0, 20, alpha=0.1, color='green')

        # Formatting
        ax.set_title(f'COT Index - {market_name}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('COT Index (0-100)', fontsize=12)
        ax.set_ylim(-5, 105)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        # Add current value annotation
        if indices:
            latest_date = dates[-1]
            latest_index = indices[-1]
            ax.annotate(f'{latest_index:.1f}',
                       xy=(latest_date, latest_index),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                       fontsize=10, fontweight='bold')

        plt.tight_layout()

        # Save chart
        filename = self.output_dir / f'{market_name.replace(" ", "_").replace("/", "-")}_cot_index.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {filename}")

        return fig, filename

    def create_net_positions_chart(self, market_data, market_name):
        """
        Create net positions chart showing specs vs commercials
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        market_data = market_data.copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data = market_data.sort_values('date')

        dates = market_data['date']

        # Top panel: Net Positions
        ax1.plot(dates, market_data['noncomm_net'], linewidth=2,
                color='#E63946', label='Speculators (Non-Commercial) Net')
        ax1.plot(dates, market_data['comm_net'], linewidth=2,
                color='#06A77D', label='Hedgers (Commercial) Net')

        # Add zero line
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)

        # Formatting
        ax1.set_title(f'Net Positions - {market_name}', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Net Positions (Contracts)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Format y-axis with thousands separator
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        # Bottom panel: Open Interest
        if 'open_interest' in market_data.columns:
            oi_col = 'open_interest'
        else:
            # Try to find OI column
            for col in market_data.columns:
                if 'open interest' in col.lower():
                    market_data['open_interest'] = pd.to_numeric(market_data[col], errors='coerce')
                    break

        if 'open_interest' in market_data.columns:
            ax2.fill_between(dates, market_data['open_interest'],
                           alpha=0.3, color='#457B9D', label='Open Interest')
            ax2.plot(dates, market_data['open_interest'], linewidth=1.5,
                    color='#1D3557', label='Open Interest')

            ax2.set_ylabel('Open Interest (Contracts)', fontsize=12)
            ax2.legend(loc='upper left')
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)

        # Format x-axis dates
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Save chart
        filename = self.output_dir / f'{market_name.replace(" ", "_").replace("/", "-")}_net_positions.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {filename}")

        return fig, filename

    def create_long_short_chart(self, market_data, market_name):
        """
        Create stacked area chart showing long and short positions
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        market_data = market_data.copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data = market_data.sort_values('date')

        dates = market_data['date']

        # Plot specs
        ax.fill_between(dates, 0, market_data['noncomm_long'],
                       alpha=0.6, color='#06A77D', label='Specs Long')
        ax.fill_between(dates, 0, -market_data['noncomm_short'],
                       alpha=0.6, color='#E63946', label='Specs Short')

        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)

        # Formatting
        ax.set_title(f'Speculator Positions - {market_name}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Contracts (Long above, Short below)', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Save chart
        filename = self.output_dir / f'{market_name.replace(" ", "_").replace("/", "-")}_long_short.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {filename}")

        return fig, filename

    def create_comprehensive_chart(self, market_data, market_name, lookback=156):
        """
        Create comprehensive 3-panel chart with all key metrics
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 1, hspace=0.3)

        market_data = market_data.copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data = market_data.sort_values('date')

        dates = market_data['date']

        # Panel 1: COT Index
        ax1 = fig.add_subplot(gs[0])

        # Calculate rolling index
        indices = []
        index_dates = []

        for i in range(lookback, len(market_data)):
            window_data = market_data.iloc[i-lookback:i+1]
            net_positions = window_data['noncomm_net']

            min_val = net_positions.min()
            max_val = net_positions.max()
            current = net_positions.iloc[-1]

            if max_val != min_val:
                index = ((current - min_val) / (max_val - min_val)) * 100
                indices.append(index)
                index_dates.append(window_data['date'].iloc[-1])

        ax1.plot(index_dates, indices, linewidth=2, color='#2E86AB')
        ax1.axhline(y=80, color='red', linestyle='--', alpha=0.5)
        ax1.axhline(y=20, color='green', linestyle='--', alpha=0.5)
        ax1.fill_between(index_dates, 80, 100, alpha=0.1, color='red')
        ax1.fill_between(index_dates, 0, 20, alpha=0.1, color='green')
        ax1.set_title(f'COT Analysis - {market_name}', fontsize=16, fontweight='bold')
        ax1.set_ylabel('COT Index (0-100)', fontsize=11)
        ax1.set_ylim(-5, 105)
        ax1.grid(True, alpha=0.3)

        # Panel 2: Net Positions
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        ax2.plot(dates, market_data['noncomm_net'], linewidth=2,
                color='#E63946', label='Speculators Net', alpha=0.8)
        ax2.plot(dates, market_data['comm_net'], linewidth=2,
                color='#06A77D', label='Commercials Net', alpha=0.8)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_ylabel('Net Positions', fontsize=11)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        # Panel 3: Open Interest
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        # Find OI column
        if 'open_interest' not in market_data.columns:
            for col in market_data.columns:
                if 'open interest' in col.lower():
                    market_data['open_interest'] = pd.to_numeric(market_data[col], errors='coerce')
                    break

        if 'open_interest' in market_data.columns:
            ax3.fill_between(dates, market_data['open_interest'],
                           alpha=0.3, color='#457B9D')
            ax3.plot(dates, market_data['open_interest'], linewidth=1.5, color='#1D3557')
            ax3.set_ylabel('Open Interest', fontsize=11)
            ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        ax3.set_xlabel('Date', fontsize=12)
        ax3.grid(True, alpha=0.3)

        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # Save chart
        filename = self.output_dir / f'{market_name.replace(" ", "_").replace("/", "-")}_comprehensive.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {filename}")

        return fig, filename

    def close_all(self):
        """Close all open figures"""
        plt.close('all')


def main():
    """Example usage"""
    print("COT Charting Module")
    print("This module is used by analyze.py to create charts")
    print("\nUsage: python analyze.py GOLD --chart")


if __name__ == "__main__":
    main()
