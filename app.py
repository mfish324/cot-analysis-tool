"""
COT Analysis Web App
Interactive Streamlit interface for analyzing Commitment of Traders data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Import local modules
from lib.tickers import resolve_ticker, TICKER_MAP, COMMODITY_TO_TICKER

# Page configuration
st.set_page_config(
    page_title="COT Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .overbought {
        color: #d32f2f;
        font-weight: bold;
    }
    .oversold {
        color: #388e3c;
        font-weight: bold;
    }
    .neutral {
        color: #1976d2;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Load COT data from parquet file"""
    data_file = Path('data/legacy_fut/all_years.parquet')
    if not data_file.exists():
        return None
    return pd.read_parquet(data_file)


@st.cache_data(ttl=3600)
def get_market_list(df):
    """Get list of unique markets"""
    if df is None:
        return []
    return sorted(df['Market and Exchange Names'].unique())


def analyze_commodity(df, commodity_name):
    """Analyze a specific commodity"""
    # Find matching markets
    commodity_name = resolve_ticker(commodity_name)
    mask = df['Market and Exchange Names'].str.contains(commodity_name, case=False, na=False)
    market_data = df[mask].copy()

    if market_data.empty:
        return None, None, None

    # Get first matching market
    markets = market_data['Market and Exchange Names'].unique()
    market_name = markets[0]
    market_data = market_data[market_data['Market and Exchange Names'] == market_name].copy()

    # Convert date
    market_data['date'] = pd.to_datetime(market_data['As of Date in Form YYYY-MM-DD'])
    market_data = market_data.sort_values('date')

    # Get column names
    col_variants = {
        'noncomm_long': ['Noncommercial Long (All)', 'Noncommercial Positions-Long (All)', 'NonComm_Positions_Long_All'],
        'noncomm_short': ['Noncommercial Short (All)', 'Noncommercial Positions-Short (All)', 'NonComm_Positions_Short_All'],
        'comm_long': ['Commercial Long (All)', 'Commercial Positions-Long (All)', 'Comm_Positions_Long_All'],
        'comm_short': ['Commercial Short (All)', 'Commercial Positions-Short (All)', 'Comm_Positions_Short_All'],
        'open_interest': ['Open Interest (All)', 'Open Interest', 'Open_Interest_All']
    }

    for key, variants in col_variants.items():
        for variant in variants:
            if variant in market_data.columns:
                market_data[key] = pd.to_numeric(market_data[variant], errors='coerce')
                break

    # Calculate net positions
    market_data['noncomm_net'] = market_data['noncomm_long'] - market_data['noncomm_short']
    market_data['comm_net'] = market_data['comm_long'] - market_data['comm_short']

    # Calculate COT Index
    lookback = min(156, len(market_data))
    indices = []
    dates = []

    # Need at least 10 data points for meaningful index
    if lookback < 10:
        # Return empty index_df but still return market_data
        index_df = pd.DataFrame({'date': [], 'cot_index': []})
        return market_data, market_name, index_df

    # Calculate rolling COT Index
    for i in range(lookback - 1, len(market_data)):
        start_idx = max(0, i - lookback + 1)
        window = market_data.iloc[start_idx:i+1]
        net = window['noncomm_net'].dropna()

        if len(net) < 10:  # Skip if not enough valid data
            continue

        min_val, max_val = net.min(), net.max()

        if max_val != min_val and not pd.isna(net.iloc[-1]):
            idx = ((net.iloc[-1] - min_val) / (max_val - min_val)) * 100
            indices.append(idx)
            dates.append(market_data['date'].iloc[i])

    # Create index dataframe
    index_df = pd.DataFrame({'date': dates, 'cot_index': indices})

    return market_data, market_name, index_df


def create_cot_index_chart(index_df):
    """Create interactive COT Index chart"""
    fig = go.Figure()

    # Add index line
    fig.add_trace(go.Scatter(
        x=index_df['date'],
        y=index_df['cot_index'],
        mode='lines',
        name='COT Index',
        line=dict(color='#2E86AB', width=3)
    ))

    # Add threshold lines
    fig.add_hline(y=80, line_dash="dash", line_color="red",
                  annotation_text="Overbought (80)")
    fig.add_hline(y=20, line_dash="dash", line_color="green",
                  annotation_text="Oversold (20)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray",
                  annotation_text="Neutral (50)")

    # Add zones
    fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_hrect(y0=0, y1=20, fillcolor="green", opacity=0.1, line_width=0)

    fig.update_layout(
        title="COT Index (0-100)",
        xaxis_title="Date",
        yaxis_title="COT Index",
        height=400,
        hovermode='x unified',
        yaxis=dict(range=[-5, 105])
    )

    return fig


def create_positions_chart(market_data):
    """Create net positions chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['noncomm_net'],
        mode='lines',
        name='Speculators (Non-Commercial)',
        line=dict(color='#E63946', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['comm_net'],
        mode='lines',
        name='Hedgers (Commercial)',
        line=dict(color='#06A77D', width=2)
    ))

    fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)

    fig.update_layout(
        title="Net Positions",
        xaxis_title="Date",
        yaxis_title="Net Positions (Contracts)",
        height=400,
        hovermode='x unified'
    )

    return fig


def create_open_interest_chart(market_data):
    """Create open interest chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['open_interest'],
        mode='lines',
        name='Open Interest',
        fill='tozeroy',
        line=dict(color='#1D3557', width=2),
        fillcolor='rgba(69, 123, 157, 0.3)'
    ))

    fig.update_layout(
        title="Open Interest",
        xaxis_title="Date",
        yaxis_title="Open Interest (Contracts)",
        height=300,
        hovermode='x unified'
    )

    return fig


def scan_extremes(df, threshold_high=80, threshold_low=20, top20_only=False):
    """Scan all markets for extremes"""
    markets = df['Market and Exchange Names'].unique()

    # Filter to top 20 by open interest if requested
    if top20_only:
        df['date'] = pd.to_datetime(df['As of Date in Form YYYY-MM-DD'])
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date].copy()

        for col in ['Open Interest (All)', 'Open Interest', 'Open_Interest_All']:
            if col in latest_df.columns:
                latest_df['oi'] = pd.to_numeric(latest_df[col], errors='coerce')
                markets = latest_df.nlargest(20, 'oi')['Market and Exchange Names'].unique()
                break

    results = []

    for market_name in markets:
        try:
            market_data, name, index_df = analyze_commodity(df, market_name)
            if index_df is not None and not index_df.empty:
                latest_index = index_df['cot_index'].iloc[-1]
                latest_date = index_df['date'].iloc[-1]

                oi = market_data['open_interest'].iloc[-1] if 'open_interest' in market_data.columns else 0

                if latest_index >= threshold_high or latest_index <= threshold_low:
                    signal = "OVERBOUGHT" if latest_index >= threshold_high else "OVERSOLD"
                    results.append({
                        'Market': market_name[:50],
                        'COT Index': round(latest_index, 1),
                        'Signal': signal,
                        'Open Interest': int(oi) if oi > 0 else None,
                        'Date': latest_date.date()
                    })
        except:
            continue

    return pd.DataFrame(results)


# ========================================
# MAIN APP
# ========================================

def main():
    # Header
    st.markdown('<div class="main-header">📊 COT Analysis Tool</div>', unsafe_allow_html=True)
    st.markdown("### Analyze Commitment of Traders Data")

    # Load data
    with st.spinner("Loading data..."):
        df = load_data()

    if df is None:
        st.error("⚠️ Data not found! Please run `python update_data.py` first.")
        st.info("After downloading data, refresh this page.")
        return

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["📈 Analyze Commodity", "🔍 Scan Extremes", "📚 Ticker Reference"])

    # ========================================
    # PAGE 1: ANALYZE COMMODITY
    # ========================================
    if page == "📈 Analyze Commodity":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Search Options")

        # Search method
        search_method = st.sidebar.radio("Search by:", ["Ticker Symbol", "Full Name"])

        if search_method == "Ticker Symbol":
            # Group tickers by category
            categories = {
                'Energies': ['CL', 'NG', 'HO', 'RB', 'BZ'],
                'Metals': ['GC', 'SI', 'HG', 'PL', 'PA'],
                'Grains': ['C', 'W', 'S', 'SM', 'BO'],
                'Livestock': ['LC', 'FC', 'LH'],
                'Softs': ['KC', 'SB', 'CC', 'CT'],
                'Indices': ['ES', 'NQ', 'YM', 'VIX'],
                'Bonds': ['ZB', 'ZN', 'ZF', 'ZT']
            }

            category = st.sidebar.selectbox("Category", list(categories.keys()))
            ticker = st.sidebar.selectbox("Ticker", categories[category])
            commodity = TICKER_MAP.get(ticker, ticker)

            st.sidebar.info(f"**{ticker}** = {commodity}")
        else:
            markets = get_market_list(df)
            commodity = st.sidebar.selectbox("Select Market", markets, index=0)

        # Analyze button
        if st.sidebar.button("🔍 Analyze", type="primary"):
            with st.spinner(f"Analyzing {commodity}..."):
                market_data, market_name, index_df = analyze_commodity(df, commodity)

            if market_data is None:
                st.error(f"❌ No data found for {commodity}")
                return

            # Get latest data
            latest = market_data.iloc[-1]
            latest_index = index_df['cot_index'].iloc[-1] if not index_df.empty else 50

            # Display market name
            st.markdown(f"## {market_name}")
            st.markdown(f"**Latest Report:** {latest['date'].date()}")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("COT Index", f"{latest_index:.1f}")

            with col2:
                if latest_index >= 80:
                    st.markdown('<p class="overbought">OVERBOUGHT ⚠️</p>', unsafe_allow_html=True)
                elif latest_index <= 20:
                    st.markdown('<p class="oversold">OVERSOLD 🟢</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="neutral">NEUTRAL</p>', unsafe_allow_html=True)

            with col3:
                st.metric("Open Interest", f"{latest['open_interest']:,.0f}")

            with col4:
                st.metric("Spec Net", f"{latest['noncomm_net']:,.0f}")

            # Detailed positions
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📈 Speculators (Non-Commercial)")
                st.metric("Long Positions", f"{latest['noncomm_long']:,.0f}")
                st.metric("Short Positions", f"{latest['noncomm_short']:,.0f}")
                st.metric("Net Positions", f"{latest['noncomm_net']:,.0f}")

            with col2:
                st.markdown("### 🏢 Hedgers (Commercial)")
                st.metric("Long Positions", f"{latest['comm_long']:,.0f}")
                st.metric("Short Positions", f"{latest['comm_short']:,.0f}")
                st.metric("Net Positions", f"{latest['comm_net']:,.0f}")

            # Interpretation
            st.markdown("---")
            st.markdown("### 💡 Interpretation")
            if latest_index >= 80:
                st.warning("**Overbought Signal:** Speculators are at near-maximum bullish positioning. This often marks market tops. Watch for potential reversal.")
            elif latest_index <= 20:
                st.success("**Oversold Signal:** Speculators are at near-maximum bearish positioning. This often marks market bottoms. Watch for potential bounce.")
            else:
                st.info("**Neutral:** Positioning is in the middle of the recent range.")

            # Charts
            st.markdown("---")
            st.markdown("### 📊 Charts")

            tab1, tab2, tab3 = st.tabs(["COT Index", "Net Positions", "Open Interest"])

            with tab1:
                if not index_df.empty:
                    st.plotly_chart(create_cot_index_chart(index_df), use_container_width=True)
                else:
                    st.warning("⚠️ Not enough historical data to calculate COT Index (need at least 10 data points)")

            with tab2:
                st.plotly_chart(create_positions_chart(market_data), use_container_width=True)

            with tab3:
                st.plotly_chart(create_open_interest_chart(market_data), use_container_width=True)

    # ========================================
    # PAGE 2: SCAN EXTREMES
    # ========================================
    elif page == "🔍 Scan Extremes":
        st.markdown("## Find Markets at Extremes")

        col1, col2, col3 = st.columns(3)
        with col1:
            threshold_high = st.slider("Overbought Threshold", 70, 95, 80)
        with col2:
            threshold_low = st.slider("Oversold Threshold", 5, 30, 20)
        with col3:
            top20_only = st.checkbox("Top 20 by Volume Only", value=False)

        if st.button("🔍 Scan Markets", type="primary"):
            with st.spinner("Scanning all markets..."):
                results = scan_extremes(df, threshold_high, threshold_low, top20_only)

            if results.empty:
                st.info("No extremes found with current thresholds.")
            else:
                # Split into overbought and oversold
                overbought = results[results['Signal'] == 'OVERBOUGHT'].sort_values('COT Index', ascending=False)
                oversold = results[results['Signal'] == 'OVERSOLD'].sort_values('COT Index')

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"### 🔴 Overbought ({len(overbought)})")
                    if not overbought.empty:
                        st.dataframe(
                            overbought[['Market', 'COT Index', 'Open Interest']],
                            use_container_width=True,
                            hide_index=True
                        )

                with col2:
                    st.markdown(f"### 🟢 Oversold ({len(oversold)})")
                    if not oversold.empty:
                        st.dataframe(
                            oversold[['Market', 'COT Index', 'Open Interest']],
                            use_container_width=True,
                            hide_index=True
                        )

    # ========================================
    # PAGE 3: TICKER REFERENCE
    # ========================================
    else:
        st.markdown("## 📚 Ticker Symbol Reference")

        st.markdown("""
        Use these ticker symbols for quick analysis instead of typing full commodity names.
        """)

        # Create ticker reference table
        categories = {
            '⚡ Energies': {'CL': 'Crude Oil', 'NG': 'Natural Gas', 'HO': 'Heating Oil', 'RB': 'RBOB Gasoline'},
            '🥇 Metals': {'GC': 'Gold', 'SI': 'Silver', 'HG': 'Copper', 'PL': 'Platinum'},
            '🌾 Grains': {'C': 'Corn', 'W': 'Wheat', 'S': 'Soybeans', 'SM': 'Soybean Meal'},
            '🐄 Livestock': {'LC': 'Live Cattle', 'FC': 'Feeder Cattle', 'LH': 'Lean Hogs'},
            '☕ Softs': {'KC': 'Coffee', 'SB': 'Sugar', 'CC': 'Cocoa', 'CT': 'Cotton'},
            '📈 Indices': {'ES': 'S&P 500', 'NQ': 'NASDAQ 100', 'YM': 'Dow Jones', 'VIX': 'VIX'},
            '💰 Bonds': {'ZB': '30Y Treasury', 'ZN': '10Y Note', 'ZF': '5Y Note', 'ZT': '2Y Note'}
        }

        for category, tickers in categories.items():
            st.markdown(f"### {category}")
            ticker_df = pd.DataFrame([
                {"Ticker": ticker, "Commodity": name}
                for ticker, name in tickers.items()
            ])
            st.dataframe(ticker_df, use_container_width=True, hide_index=True)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    **COT Analysis Tool**

    Analyze CFTC Commitment of Traders data to identify market extremes.

    Data updates: Weekly (Fridays)
    """)


if __name__ == "__main__":
    main()
