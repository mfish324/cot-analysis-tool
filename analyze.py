"""
Simple Quick Start - Analyze COT Data Without Full Processing
This bypasses the complex processing and gets you analyzing data immediately
"""

import pandas as pd
from pathlib import Path
import sys
from lib.tickers import resolve_ticker

def simple_analyze(commodity_name='GOLD', create_charts=False):
    """Simple analysis without complex processing"""

    # Resolve ticker symbol to commodity name
    original_input = commodity_name
    commodity_name = resolve_ticker(commodity_name)

    print("=" * 60)
    print(f"SIMPLE COT ANALYSIS - {commodity_name}")
    if original_input.upper() != commodity_name.upper():
        print(f"(Ticker: {original_input.upper()})")
    print("=" * 60)

    # Load legacy data (it's already downloaded)
    data_file = Path('data/legacy_fut/all_years.parquet')

    if not data_file.exists():
        print(f"\nData file not found: {data_file}")
        print("Run: python fix_data.py first")
        return

    print(f"\nLoading data from {data_file}...")
    df = pd.read_parquet(data_file)

    print(f"Loaded {len(df):,} records")
    print(f"Date range: {df['As of Date in Form YYYY-MM-DD'].min()} to {df['As of Date in Form YYYY-MM-DD'].max()}")

    # Find commodities with GOLD in the name
    gold_mask = df['Market and Exchange Names'].str.contains(commodity_name, case=False, na=False)
    gold_data = df[gold_mask].copy()

    if gold_data.empty:
        print(f"\n{commodity_name} not found. Available markets:")
        print(df['Market and Exchange Names'].unique()[:20])
        return

    # Show what we found
    markets = gold_data['Market and Exchange Names'].unique()
    print(f"\nFound {len(markets)} market(s) matching '{commodity_name}':")
    for m in markets:
        print(f"  - {m}")

    # Use the first one
    market_name = markets[0]
    market_data = gold_data[gold_data['Market and Exchange Names'] == market_name].copy()

    # Convert date
    market_data['date'] = pd.to_datetime(market_data['As of Date in Form YYYY-MM-DD'])
    market_data = market_data.sort_values('date')

    # Get key columns (handling different column name formats)
    # Try multiple column name variations
    col_variants = {
        'noncomm_long': ['Noncommercial Long (All)', 'Noncommercial Positions-Long (All)', 'NonComm_Positions_Long_All'],
        'noncomm_short': ['Noncommercial Short (All)', 'Noncommercial Positions-Short (All)', 'NonComm_Positions_Short_All'],
        'comm_long': ['Commercial Long (All)', 'Commercial Positions-Long (All)', 'Comm_Positions_Long_All'],
        'comm_short': ['Commercial Short (All)', 'Commercial Positions-Short (All)', 'Comm_Positions_Short_All'],
        'open_interest': ['Open Interest (All)', 'Open Interest', 'Open_Interest_All']
    }

    for key, variants in col_variants.items():
        found = False
        for variant in variants:
            if variant in market_data.columns:
                market_data[key] = pd.to_numeric(market_data[variant], errors='coerce')
                found = True
                break
        if not found:
            print(f"\nCouldn't find column for {key}")
            print("Available columns:")
            print([c for c in market_data.columns if 'Long' in c or 'Short' in c or 'Interest' in c][:15])
            return

    # Calculate net positions
    market_data['noncomm_net'] = market_data['noncomm_long'] - market_data['noncomm_short']
    market_data['comm_net'] = market_data['comm_long'] - market_data['comm_short']

    # Get latest
    latest = market_data.iloc[-1]

    print(f"\n{'-'*60}")
    print(f"LATEST POSITIONS FOR {market_name}")
    print(f"Date: {latest['date'].date()}")
    print(f"{'-'*60}")
    print(f"Open Interest:        {latest['open_interest']:>12,.0f}")
    print(f"\nNon-Commercial (Speculators):")
    print(f"  Long:               {latest['noncomm_long']:>12,.0f}")
    print(f"  Short:              {latest['noncomm_short']:>12,.0f}")
    print(f"  Net:                {latest['noncomm_net']:>12,.0f}")
    print(f"\nCommercial (Hedgers):")
    print(f"  Long:               {latest['comm_long']:>12,.0f}")
    print(f"  Short:              {latest['comm_short']:>12,.0f}")
    print(f"  Net:                {latest['comm_net']:>12,.0f}")

    # Calculate COT Index (simple version)
    lookback = min(156, len(market_data))  # 3 years or available data
    recent_data = market_data.tail(lookback)

    noncomm_net_recent = recent_data['noncomm_net'].dropna()

    # Check if we have enough valid data
    if len(noncomm_net_recent) < 10:
        cot_index = None  # Not enough data
    else:
        min_val = noncomm_net_recent.min()
        max_val = noncomm_net_recent.max()

        if max_val != min_val and not pd.isna(latest['noncomm_net']):
            cot_index = ((latest['noncomm_net'] - min_val) / (max_val - min_val)) * 100
        else:
            cot_index = 50

    print(f"\n{'-'*60}")
    print(f"COT INDEX (0-100)")
    print(f"{'-'*60}")

    if cot_index is None:
        print(f"Current Index:        NOT AVAILABLE")
        print(f"Signal:               N/A - Insufficient historical data (<10 data points)")
        print(f"\nInterpretation:")
        print(f"  This market does not have enough historical data to calculate")
        print(f"  a meaningful COT Index. At least 10 weekly reports are needed.")
    else:
        print(f"Current Index:        {cot_index:>12.1f}")

        if cot_index >= 80:
            print(f"Signal:               OVERBOUGHT (contrarian bearish)")
        elif cot_index <= 20:
            print(f"Signal:               OVERSOLD (contrarian bullish)")
        else:
            print(f"Signal:               NEUTRAL")

        print(f"\nInterpretation:")
        if cot_index >= 80:
            print(f"  Speculators are at near-maximum bullish positioning.")
            print(f"  This often marks market tops. Watch for reversal.")
        elif cot_index <= 20:
            print(f"  Speculators are at near-maximum bearish positioning.")
            print(f"  This often marks market bottoms. Watch for bounce.")
        else:
            print(f"  Positioning is in the middle of the recent range.")

    print(f"\n{'='*60}")

    # Create charts if requested
    if create_charts:
        try:
            from lib.charting import COTCharter

            print(f"\nCreating charts...")
            charter = COTCharter()

            # Create comprehensive chart
            charter.create_comprehensive_chart(market_data, market_name, lookback=lookback)

            # Create individual charts
            charter.create_cot_index_chart(market_data, market_name, lookback=lookback)
            charter.create_net_positions_chart(market_data, market_name)

            print(f"\nAll charts saved to 'charts/' directory")
            charter.close_all()

        except Exception as e:
            print(f"\nError creating charts: {e}")
            print("Make sure matplotlib is installed: pip install matplotlib")

    return market_data


def find_extremes(overbought_threshold=80, oversold_threshold=20, top20_only=False):
    """Find all commodities at extreme COT Index levels"""

    print("=" * 60)
    print("SCANNING FOR EXTREME COT POSITIONS")
    if top20_only:
        print("(Restricted to Top 20 Markets by Open Interest)")
    print("=" * 60)

    data_file = Path('data/legacy_fut/all_years.parquet')

    if not data_file.exists():
        print(f"\nData file not found: {data_file}")
        print("Run: python utils/fix_data.py first")
        return

    print(f"\nLoading data from {data_file}...")
    df = pd.read_parquet(data_file)

    # Get unique markets
    markets = df['Market and Exchange Names'].unique()

    # If top20_only, filter to top 20 by latest open interest
    if top20_only:
        print(f"Identifying top 20 markets by open interest...")

        # Find open interest column
        oi_col = None
        for col in ['Open Interest (All)', 'Open Interest', 'Open_Interest_All']:
            if col in df.columns:
                oi_col = col
                break

        if oi_col:
            # Get latest date
            df['date'] = pd.to_datetime(df['As of Date in Form YYYY-MM-DD'])
            latest_date = df['date'].max()

            # Get latest data
            latest_df = df[df['date'] == latest_date].copy()
            latest_df['open_interest'] = pd.to_numeric(latest_df[oi_col], errors='coerce')

            # Get top 20 by open interest
            top_markets = latest_df.nlargest(20, 'open_interest')['Market and Exchange Names'].unique()
            markets = top_markets
            print(f"Analyzing top 20 markets...")
        else:
            print("Warning: Could not find open interest column. Analyzing all markets.")
            print(f"Analyzing {len(markets)} markets...")
    else:
        print(f"Analyzing {len(markets)} markets...")

    # Column variants for legacy data
    col_variants = {
        'noncomm_long': ['Noncommercial Long (All)', 'Noncommercial Positions-Long (All)', 'NonComm_Positions_Long_All'],
        'noncomm_short': ['Noncommercial Short (All)', 'Noncommercial Positions-Short (All)', 'NonComm_Positions_Short_All'],
    }

    overbought_markets = []
    oversold_markets = []
    all_markets_data = []

    for market_name in markets:
        try:
            # Get data for this market
            market_data = df[df['Market and Exchange Names'] == market_name].copy()

            if len(market_data) < 10:  # Skip if too little data
                continue

            # Convert date
            market_data['date'] = pd.to_datetime(market_data['As of Date in Form YYYY-MM-DD'])
            market_data = market_data.sort_values('date')

            # Find columns
            noncomm_long_col = None
            noncomm_short_col = None

            for variant in col_variants['noncomm_long']:
                if variant in market_data.columns:
                    noncomm_long_col = variant
                    break

            for variant in col_variants['noncomm_short']:
                if variant in market_data.columns:
                    noncomm_short_col = variant
                    break

            if not noncomm_long_col or not noncomm_short_col:
                continue

            # Calculate net position
            market_data['noncomm_long'] = pd.to_numeric(market_data[noncomm_long_col], errors='coerce')
            market_data['noncomm_short'] = pd.to_numeric(market_data[noncomm_short_col], errors='coerce')
            market_data['noncomm_net'] = market_data['noncomm_long'] - market_data['noncomm_short']

            # Get open interest
            oi_col = None
            for col in ['Open Interest (All)', 'Open Interest', 'Open_Interest_All']:
                if col in market_data.columns:
                    oi_col = col
                    break

            # Get latest
            latest = market_data.iloc[-1]

            open_interest = 0
            if oi_col:
                open_interest = pd.to_numeric(latest[oi_col], errors='coerce')
                if pd.isna(open_interest):
                    open_interest = 0

            # Calculate COT Index
            lookback = min(156, len(market_data))
            recent_data = market_data.tail(lookback)

            noncomm_net_recent = recent_data['noncomm_net']
            min_val = noncomm_net_recent.min()
            max_val = noncomm_net_recent.max()

            if max_val != min_val and not pd.isna(latest['noncomm_net']):
                cot_index = ((latest['noncomm_net'] - min_val) / (max_val - min_val)) * 100

                market_info = {
                    'market': market_name,
                    'index': cot_index,
                    'date': latest['date'],
                    'open_interest': open_interest
                }

                all_markets_data.append(market_info)

                # Check for extremes
                if cot_index >= overbought_threshold:
                    overbought_markets.append(market_info)
                elif cot_index <= oversold_threshold:
                    oversold_markets.append(market_info)

        except Exception as e:
            # Skip markets with errors
            continue

    # Sort by index
    overbought_markets.sort(key=lambda x: x['index'], reverse=True)
    oversold_markets.sort(key=lambda x: x['index'])

    # Display results
    print(f"\n{'='*60}")
    print(f"EXTREME POSITIONS FOUND")
    print(f"{'='*60}")

    if overbought_markets:
        print(f"\nOVERBOUGHT (Index >= {overbought_threshold}) - Contrarian Bearish Signal:")
        print("-" * 60)
        for item in overbought_markets:
            oi_str = f"{item['open_interest']:>12,.0f}" if item['open_interest'] > 0 else "            "
            print(f"  {item['market'][:40]:<40} Index: {item['index']:5.1f}  OI: {oi_str}")
        print(f"\n  Total overbought: {len(overbought_markets)}")
    else:
        print(f"\nNo overbought markets found (threshold: {overbought_threshold})")

    if oversold_markets:
        print(f"\nOVERSOLD (Index <= {oversold_threshold}) - Contrarian Bullish Signal:")
        print("-" * 60)
        for item in oversold_markets:
            oi_str = f"{item['open_interest']:>12,.0f}" if item['open_interest'] > 0 else "            "
            print(f"  {item['market'][:40]:<40} Index: {item['index']:5.1f}  OI: {oi_str}")
        print(f"\n  Total oversold: {len(oversold_markets)}")
    else:
        print(f"\nNo oversold markets found (threshold: {oversold_threshold})")

    print(f"\n{'='*60}")
    print(f"Scan complete. Analyzed {len(markets)} markets.")
    print(f"\nTo analyze specific market: python analyze.py \"MARKET NAME\"")
    print(f"{'='*60}\n")


def list_commodities():
    """List all available commodities"""
    print("=" * 60)
    print("AVAILABLE COMMODITIES")
    print("=" * 60)

    data_file = Path('data/legacy_fut/all_years.parquet')

    if not data_file.exists():
        print(f"\nData file not found: {data_file}")
        print("Run: python fix_data.py first")
        return

    df = pd.read_parquet(data_file)

    # Get unique markets
    markets = df['Market and Exchange Names'].unique()

    # Common keywords to search for
    categories = {
        'Energy': ['CRUDE', 'OIL', 'GAS', 'GASOLINE', 'HEATING'],
        'Metals': ['GOLD', 'SILVER', 'COPPER', 'PLATINUM', 'PALLADIUM'],
        'Grains': ['CORN', 'WHEAT', 'SOYBEAN', 'OATS', 'RICE'],
        'Meats': ['CATTLE', 'HOGS', 'PORK'],
        'Softs': ['COFFEE', 'SUGAR', 'COCOA', 'COTTON', 'ORANGE'],
        'Currencies': ['DOLLAR', 'EURO', 'YEN', 'POUND', 'FRANC'],
        'Indices': ['S&P', 'DOW', 'NASDAQ', 'VIX'],
    }

    for category, keywords in categories.items():
        print(f"\n{category}:")
        print("-" * 40)

        found = set()
        for market in markets:
            for keyword in keywords:
                if keyword in market.upper():
                    found.add(market)

        if found:
            for market in sorted(found):
                print(f"  {market}")
        else:
            print(f"  (none found)")

    print(f"\n{'='*60}")
    print(f"Total markets: {len(markets)}")
    print(f"\nTo analyze: python analyze.py GOLD")


if __name__ == "__main__":
    import sys
    from lib.tickers import list_tickers

    if len(sys.argv) > 1:
        # Check for --extremes flag
        if sys.argv[1] == '--extremes':
            # Check for --top20 flag
            top20_only = '--top20' in sys.argv
            find_extremes(top20_only=top20_only)
        elif sys.argv[1] == '--tickers':
            list_tickers()
        elif sys.argv[1] in ['--help', '-h']:
            print("\nCOT Analysis Tool - Usage:")
            print("=" * 60)
            print("\n1. List all available commodities:")
            print("   python analyze.py")
            print("\n2. List all ticker symbols:")
            print("   python analyze.py --tickers")
            print("\n3. Analyze using ticker symbol:")
            print("   python analyze.py GC")
            print("   python analyze.py CL")
            print("   python analyze.py ES")
            print("\n4. Analyze using full name:")
            print("   python analyze.py GOLD")
            print("   python analyze.py \"CRUDE OIL\"")
            print("\n5. Analyze with charts:")
            print("   python analyze.py GC --chart")
            print("   python analyze.py GOLD --chart")
            print("\n6. Find all markets at extreme positions:")
            print("   python analyze.py --extremes")
            print("\n7. Find extremes in top 20 markets by volume:")
            print("   python analyze.py --extremes --top20")
            print("\n" + "=" * 60 + "\n")
        else:
            # Check for --chart flag
            create_charts = '--chart' in sys.argv

            # Remove --chart from arguments to get commodity name
            args = [arg for arg in sys.argv[1:] if arg != '--chart']
            commodity = ' '.join(args)

            simple_analyze(commodity, create_charts=create_charts)
    else:
        list_commodities()
