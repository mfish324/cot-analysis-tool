"""
Ticker Symbol Mapping for COT Analysis
Maps common ticker symbols to full commodity names
"""

# Ticker to commodity name mapping
TICKER_MAP = {
    # Energies
    'CL': 'CRUDE OIL',
    'WTI': 'CRUDE OIL',
    'NG': 'NATURAL GAS',
    'HO': 'HEATING OIL',
    'RB': 'RBOB',
    'BZ': 'BRENT',

    # Precious Metals
    'GC': 'GOLD',
    'SI': 'SILVER',
    'PL': 'PLATINUM',
    'PA': 'PALLADIUM',
    'HG': 'COPPER',

    # Base Metals
    'COPPER': 'COPPER',
    'ALI': 'ALUMINUM',

    # Grains
    'C': 'CORN',
    'ZC': 'CORN',
    'W': 'WHEAT',
    'ZW': 'WHEAT',
    'S': 'SOYBEAN',
    'ZS': 'SOYBEAN',
    'SM': 'SOYBEAN MEAL',
    'BO': 'SOYBEAN OIL',
    'O': 'OATS',
    'ZO': 'OATS',
    'RR': 'ROUGH RICE',

    # Livestock
    'LC': 'LIVE CATTLE',
    'FC': 'FEEDER CATTLE',
    'LH': 'LEAN HOGS',
    'HE': 'LEAN HOGS',

    # Softs
    'KC': 'COFFEE',
    'SB': 'SUGAR',
    'CC': 'COCOA',
    'CT': 'COTTON',
    'OJ': 'ORANGE JUICE',
    'LB': 'LUMBER',

    # Financials
    'ES': 'S&P',
    'NQ': 'NASDAQ',
    'YM': 'DOW',
    'RTY': 'RUSSELL',
    'VIX': 'VIX',

    # Bonds/Rates
    'ZB': 'TREASURY BOND',
    'ZN': '10-YEAR',
    'ZF': '5-YEAR',
    'ZT': '2-YEAR',
    'GE': 'EURODOLLAR',
    'ZQ': 'FED FUNDS',

    # Currencies
    'DX': 'DOLLAR INDEX',
    '6E': 'EURO',
    '6J': 'YEN',
    '6B': 'POUND',
    '6C': 'CANADIAN DOLLAR',
    '6A': 'AUSTRALIAN DOLLAR',
    '6S': 'SWISS FRANC',
    '6M': 'MEXICAN PESO',
    'BTC': 'BITCOIN',
    'ETH': 'ETHER',

    # Other
    'DXY': 'DOLLAR INDEX',
}

# Reverse mapping: commodity keywords to tickers (for display)
COMMODITY_TO_TICKER = {}
for ticker, commodity in TICKER_MAP.items():
    # Store the shortest ticker for each commodity
    if commodity not in COMMODITY_TO_TICKER or len(ticker) < len(COMMODITY_TO_TICKER[commodity]):
        COMMODITY_TO_TICKER[commodity] = ticker


def resolve_ticker(symbol):
    """
    Resolve a ticker symbol to a commodity name
    Returns the commodity name if ticker is found, otherwise returns the original input
    """
    symbol_upper = symbol.upper().strip()

    # Check if it's a known ticker
    if symbol_upper in TICKER_MAP:
        return TICKER_MAP[symbol_upper]

    # Otherwise return as-is (might be full commodity name)
    return symbol


def get_ticker(commodity_name):
    """
    Get ticker symbol for a commodity name
    Returns the ticker if found, otherwise None
    """
    commodity_upper = commodity_name.upper().strip()
    return COMMODITY_TO_TICKER.get(commodity_upper)


def list_tickers():
    """Print all available ticker symbols"""
    print("=" * 70)
    print("AVAILABLE TICKER SYMBOLS")
    print("=" * 70)

    categories = {
        'Energies': ['CL', 'WTI', 'NG', 'HO', 'RB', 'BZ'],
        'Precious Metals': ['GC', 'SI', 'PL', 'PA', 'HG'],
        'Grains': ['C', 'ZC', 'W', 'ZW', 'S', 'ZS', 'SM', 'BO', 'O', 'RR'],
        'Livestock': ['LC', 'FC', 'LH', 'HE'],
        'Softs': ['KC', 'SB', 'CC', 'CT', 'OJ', 'LB'],
        'Indices': ['ES', 'NQ', 'YM', 'RTY', 'VIX'],
        'Bonds': ['ZB', 'ZN', 'ZF', 'ZT', 'GE', 'ZQ'],
        'Currencies': ['DX', '6E', '6J', '6B', '6C', '6A', '6S', '6M', 'BTC', 'ETH'],
    }

    for category, tickers in categories.items():
        print(f"\n{category}:")
        print("-" * 70)
        for ticker in tickers:
            commodity = TICKER_MAP.get(ticker, 'Unknown')
            print(f"  {ticker:<6} -> {commodity}")

    print("\n" + "=" * 70)
    print(f"Total tickers: {len(TICKER_MAP)}")
    print("\nUsage: python analyze.py GC")
    print("       python analyze.py CL --chart")
    print("=" * 70 + "\n")


def main():
    """Test ticker resolution"""
    print("Ticker Resolution Examples:")
    print("-" * 40)

    test_tickers = ['GC', 'CL', 'ES', 'ZB', 'GOLD', 'CRUDE OIL']

    for ticker in test_tickers:
        resolved = resolve_ticker(ticker)
        print(f"{ticker:15} -> {resolved}")


if __name__ == "__main__":
    list_tickers()
