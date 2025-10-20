"""
COT Visualization Module
Create charts and visualizations for COT data analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class COTVisualizer:
    """Visualize COT data with various chart types"""

    def __init__(self, data_dir='data'):
        """Initialize visualizer"""
        self.data_dir = Path(data_dir)
        self.output_dir = Path('charts')
        self.output_dir.mkdir(exist_ok=True)

        # Set style
        sns.set_style("darkgrid")
        plt.rcParams['figure.figsize'] = (14, 8)

    def plot_net_positions(self, df, commodity, report_type='disaggregated_fut', save=False):
        """
        Plot net positions over time for different trader groups
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        if report_type == 'legacy_fut':
            if 'noncomm_net' in df.columns:
                ax.plot(df['report_date'], df['noncomm_net'],
                       label='Non-Commercial', linewidth=2, color='blue')
            if 'comm_net' in df.columns:
                ax.plot(df['report_date'], df['comm_net'],
                       label='Commercial', linewidth=2, color='red')

        elif report_type == 'disaggregated_fut':
            if 'managed_money_net' in df.columns:
                ax.plot(df['report_date'], df['managed_money_net'],
                       label='Managed Money', linewidth=2, color='blue')
            if 'producer_net' in df.columns:
                ax.plot(df['report_date'], df['producer_net'],
                       label='Producer/Merchant', linewidth=2, color='red')
            if 'swap_net' in df.columns:
                ax.plot(df['report_date'], df['swap_net'],
                       label='Swap Dealers', linewidth=2, color='green')

        elif report_type == 'tff_fut':
            if 'lev_money_net' in df.columns:
                ax.plot(df['report_date'], df['lev_money_net'],
                       label='Leveraged Funds', linewidth=2, color='blue')
            if 'asset_mgr_net' in df.columns:
                ax.plot(df['report_date'], df['asset_mgr_net'],
                       label='Asset Managers', linewidth=2, color='green')

        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Net Positions (Contracts)', fontsize=12)
        ax.set_title(f'{commodity} - Net Positions by Trader Group', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            filename = self.output_dir / f'{commodity}_net_positions.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Chart saved: {filename}")

        return fig

    def plot_long_short_positions(self, df, commodity, trader_type='managed_money', save=False):
        """
        Plot long and short positions separately with area fill
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        long_col = f'{trader_type}_long'
        short_col = f'{trader_type}_short'

        if long_col in df.columns and short_col in df.columns:
            # Long positions
            ax1.fill_between(df['report_date'], 0, df[long_col],
                           color='green', alpha=0.6, label='Long')
            ax1.plot(df['report_date'], df[long_col],
                    color='darkgreen', linewidth=2)
            ax1.set_ylabel('Long Positions', fontsize=12)
            ax1.set_title(f'{commodity} - {trader_type.replace("_", " ").title()} Long Positions',
                         fontsize=14, fontweight='bold')
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)

            # Short positions
            ax2.fill_between(df['report_date'], 0, df[short_col],
                           color='red', alpha=0.6, label='Short')
            ax2.plot(df['report_date'], df[short_col],
                    color='darkred', linewidth=2)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.set_ylabel('Short Positions', fontsize=12)
            ax2.set_title(f'{commodity} - {trader_type.replace("_", " ").title()} Short Positions',
                         fontsize=14, fontweight='bold')
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            filename = self.output_dir / f'{commodity}_{trader_type}_long_short.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Chart saved: {filename}")

        return fig

    def plot_cot_index(self, df, commodity, position_col, lookback=156, save=False):
        """
        Plot COT Index showing position relative to historical range
        """
        index_col = f'{position_col}_index_{lookback}'

        if index_col not in df.columns:
            print(f"Index column {index_col} not found. Calculate it first.")
            return None

        fig, ax = plt.subplots(figsize=(14, 8))

        ax.plot(df['report_date'], df[index_col], linewidth=2, color='blue')
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Overbought (80)')
        ax.axhline(y=20, color='green', linestyle='--', alpha=0.7, label='Oversold (20)')
        ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='Neutral (50)')

        # Fill extreme zones
        ax.fill_between(df['report_date'], 80, 100, color='red', alpha=0.1)
        ax.fill_between(df['report_date'], 0, 20, color='green', alpha=0.1)

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('COT Index (0-100)', fontsize=12)
        ax.set_title(f'{commodity} - COT Index ({lookback} weeks)',
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            filename = self.output_dir / f'{commodity}_cot_index.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Chart saved: {filename}")

        return fig

    def plot_interactive_dashboard(self, df, commodity, report_type='disaggregated_fut'):
        """
        Create interactive Plotly dashboard with multiple subplots
        """
        # Determine which columns to use based on report type
        if report_type == 'disaggregated_fut':
            net_cols = {
                'Managed Money': 'managed_money_net',
                'Producer': 'producer_net',
                'Swap Dealers': 'swap_net'
            }
            main_trader = 'managed_money'
        elif report_type == 'tff_fut':
            net_cols = {
                'Leveraged Funds': 'lev_money_net',
                'Asset Managers': 'asset_mgr_net',
                'Dealers': 'dealer_net'
            }
            main_trader = 'lev_money'
        else:  # legacy
            net_cols = {
                'Non-Commercial': 'noncomm_net',
                'Commercial': 'comm_net'
            }
            main_trader = 'noncomm'

        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                f'{commodity} - Net Positions',
                f'{commodity} - Long vs Short',
                f'{commodity} - Open Interest'
            ),
            vertical_spacing=0.1,
            row_heights=[0.4, 0.3, 0.3]
        )

        # Plot 1: Net positions for all trader groups
        colors = ['blue', 'red', 'green', 'orange']
        for idx, (name, col) in enumerate(net_cols.items()):
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['report_date'],
                        y=df[col],
                        name=name,
                        line=dict(color=colors[idx], width=2),
                        mode='lines'
                    ),
                    row=1, col=1
                )

        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                     opacity=0.5, row=1, col=1)

        # Plot 2: Long vs Short for main trader group
        long_col = f'{main_trader}_long'
        short_col = f'{main_trader}_short'

        if long_col in df.columns and short_col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['report_date'],
                    y=df[long_col],
                    name='Long',
                    fill='tozeroy',
                    line=dict(color='green', width=2),
                    mode='lines'
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=df['report_date'],
                    y=df[short_col],
                    name='Short',
                    fill='tozeroy',
                    line=dict(color='red', width=2),
                    mode='lines'
                ),
                row=2, col=1
            )

        # Plot 3: Open Interest
        if 'open_interest' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['report_date'],
                    y=df['open_interest'],
                    name='Open Interest',
                    line=dict(color='purple', width=2),
                    mode='lines',
                    fill='tozeroy'
                ),
                row=3, col=1
            )

        # Update layout
        fig.update_layout(
            height=1000,
            showlegend=True,
            title_text=f"{commodity} - Commitment of Traders Analysis",
            title_font_size=20,
            hovermode='x unified'
        )

        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Net Positions", row=1, col=1)
        fig.update_yaxes(title_text="Contracts", row=2, col=1)
        fig.update_yaxes(title_text="Open Interest", row=3, col=1)

        # Save as HTML
        filename = self.output_dir / f'{commodity}_dashboard.html'
        fig.write_html(str(filename))
        print(f"Interactive dashboard saved: {filename}")

        return fig

    def plot_comparison_chart(self, df, commodity, save=False):
        """
        Create comparison chart showing all trader groups on normalized scale
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Get net position columns
        net_cols = [col for col in df.columns if col.endswith('_net') and 'pct' not in col]

        colors = plt.cm.Set2(np.linspace(0, 1, len(net_cols)))

        for idx, col in enumerate(net_cols):
            # Normalize to 0-100 scale for comparison
            normalized = ((df[col] - df[col].min()) /
                         (df[col].max() - df[col].min()) * 100)

            label = col.replace('_net', '').replace('_', ' ').title()
            ax.plot(df['report_date'], normalized,
                   label=label, linewidth=2, color=colors[idx])

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Normalized Position (0-100)', fontsize=12)
        ax.set_title(f'{commodity} - Normalized Trader Positions Comparison',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            filename = self.output_dir / f'{commodity}_comparison.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Chart saved: {filename}")

        return fig

    def plot_sentiment_gauge(self, df, commodity):
        """
        Create a gauge chart showing current sentiment
        """
        if 'sentiment_score' not in df.columns:
            print("Sentiment score not calculated. Run analyzer first.")
            return None

        current_sentiment = df['sentiment_score'].iloc[-1]

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_sentiment,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{commodity} - Current Sentiment", 'font': {'size': 24}},
            delta={'reference': 0, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [-100, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-100, -50], 'color': 'darkred'},
                    {'range': [-50, -20], 'color': 'lightcoral'},
                    {'range': [-20, 20], 'color': 'lightgray'},
                    {'range': [20, 50], 'color': 'lightgreen'},
                    {'range': [50, 100], 'color': 'darkgreen'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': current_sentiment
                }
            }
        ))

        fig.update_layout(height=400, font={'color': "darkblue", 'family': "Arial"})

        filename = self.output_dir / f'{commodity}_sentiment_gauge.html'
        fig.write_html(str(filename))
        print(f"Sentiment gauge saved: {filename}")

        return fig


def main():
    """Example usage"""
    from cot_analyzer import COTAnalyzer

    visualizer = COTVisualizer()
    analyzer = COTAnalyzer()

    commodity = 'GOLD'
    report_type = 'disaggregated_fut'

    try:
        # Get analyzed data
        df, summary = analyzer.comprehensive_analysis(commodity, report_type)

        print(f"\nGenerating visualizations for {commodity}...")

        # Create various charts
        visualizer.plot_net_positions(df, commodity, report_type, save=True)
        visualizer.plot_long_short_positions(df, commodity, 'managed_money', save=True)

        if 'managed_money_net_index_156' in df.columns:
            visualizer.plot_cot_index(df, commodity, 'managed_money_net', 156, save=True)

        visualizer.plot_interactive_dashboard(df, commodity, report_type)
        visualizer.plot_comparison_chart(df, commodity, save=True)

        if 'sentiment_score' in df.columns:
            visualizer.plot_sentiment_gauge(df, commodity)

        print("\nAll charts generated successfully!")
        print(f"Charts saved in: {visualizer.output_dir}")

    except Exception as e:
        print(f"Error generating visualizations: {e}")


if __name__ == "__main__":
    main()
