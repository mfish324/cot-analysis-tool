# COT Analysis Tool - Complete Guide

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Understanding COT Data](#understanding-cot-data)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)

## Installation

### Requirements
- Python 3.8 or higher
- Internet connection (for initial data download)

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python utils/verify.py

# 3. Start analyzing (data already downloaded)
python analyze.py GOLD
```

## Quick Start

### Analyze a Commodity

```bash
python analyze.py GOLD
```

Output shows:
- Latest positions for speculators and hedgers
- COT Index (0-100 scale)
- Trading signal (Overbought/Oversold/Neutral)
- Interpretation

### List All Commodities

```bash
python analyze.py
```

Shows all available commodities organized by category.

### Find Extreme Positions

```bash
python analyze.py --extremes
```

Lists commodities at overbought (>80) or oversold (<20) levels.

## Understanding COT Data

### What is COT?

The Commitment of Traders (COT) report is published weekly by the CFTC showing positions of different trader groups in futures markets.

### Trader Categories

**Speculators (Non-Commercial)**
- Hedge funds, large traders, CTAs
- Trade for profit, not hedging
- Often wrong at market extremes
- When very bullish → potential top
- When very bearish → potential bottom

**Hedgers (Commercial)**
- Producers, processors, merchants
- Trade to hedge business risk
- Often right at major turning points
- Contrarian to speculators at extremes

### COT Index

The COT Index normalizes current positioning to a 0-100 scale:

```
Index = ((Current - Min) / (Max - Min)) * 100
```

Based on 156-week (3-year) lookback period.

**Interpretation:**
- **>80**: Extreme bullish positioning (contrarian bearish signal)
- **60-80**: Moderately bullish
- **40-60**: Neutral
- **20-40**: Moderately bearish
- **<20**: Extreme bearish positioning (contrarian bullish signal)

### Trading Signals

**Overbought (Index > 80)**
- Speculators at maximum bullish positioning
- Often marks market tops
- Watch for reversal down
- Contrarian bearish opportunity

**Oversold (Index < 20)**
- Speculators at maximum bearish positioning
- Often marks market bottoms
- Watch for reversal up
- Contrarian bullish opportunity

**Neutral (40-60)**
- Normal positioning range
- No extreme signal
- Trend may continue

## Usage Examples

### Example 1: Identify Market Extreme

```bash
python analyze.py GOLD
```

Output shows COT Index of 85 → Overbought
- Speculators very bullish
- Potential market top
- Consider contrarian short position

### Example 2: Find Trading Opportunities

```bash
python analyze.py --extremes
```

Output:
```
Overbought (>80):
  GOLD          Index: 85.2
  SILVER        Index: 81.7

Oversold (<20):
  NATURAL_GAS   Index: 15.3
  WHEAT         Index: 18.9
```

→ Consider: Long natural gas/wheat, short gold/silver

### Example 3: Track Specific Commodity

```bash
# Check weekly
python analyze.py CRUDE_OIL

# Monitor index changes
# Index 45 → 55 → 65 → 75 → Watch for reversal at 80+
```

### Example 4: Sector Analysis

```bash
# Check all precious metals
python analyze.py GOLD
python analyze.py SILVER
python analyze.py PLATINUM

# Compare positioning
# If all >75 → Sector overbought
```

## Advanced Features

### Custom Analysis

Use Python directly for custom analysis:

```python
import pandas as pd
from pathlib import Path

# Load data
df = pd.read_parquet('data/legacy_fut/all_years.parquet')

# Filter for GOLD
gold = df[df['Market and Exchange Names'].str.contains('GOLD', na=False)]

# Your custom analysis
# ...
```

### Batch Processing

```bash
# Loop through commodities
for commodity in GOLD SILVER COPPER PLATINUM
do
    echo "=== $commodity ==="
    python analyze.py $commodity | grep "COT INDEX"
done
```

### Export Data

```python
import pandas as pd

# Load
df = pd.read_parquet('data/legacy_fut/all_years.parquet')

# Export to CSV
df.to_csv('cot_data_export.csv', index=False)

# Export to Excel
df.to_excel('cot_data_export.xlsx', index=False)
```

## Tips and Best Practices

### 1. Focus on Extremes
COT analysis works best at historical extremes (>80 or <20). Mid-range signals (40-60) are less reliable.

### 2. Combine with Technical Analysis
- Use COT for market sentiment
- Use technical analysis for timing entries
- COT shows *what*, TA shows *when*

### 3. Watch Divergences
Best signals when commercials and speculators are opposite:
- Specs very bullish + Commercials very bearish = Potential top
- Specs very bearish + Commercials very bullish = Potential bottom

### 4. Be Patient
COT extremes can persist for weeks. Don't rush entries just because index is >80.

### 5. Use Multiple Timeframes
- Short-term: 52 weeks (1 year)
- Medium-term: 156 weeks (3 years) - DEFAULT
- Long-term: 260 weeks (5 years)

### 6. Consider Open Interest
Rising open interest + extreme positioning = stronger signal

### 7. Weekly Updates
COT data released every Friday (for previous Tuesday). Check weekly, not daily.

### 8. Sector Confirmation
If all commodities in a sector show same signal (e.g., all metals >80), stronger conviction.

## Common Commodities

### Energies
```bash
python analyze.py "CRUDE OIL"
python analyze.py "NATURAL GAS"
python analyze.py GASOLINE
python analyze.py "HEATING OIL"
```

### Metals
```bash
python analyze.py GOLD
python analyze.py SILVER
python analyze.py COPPER
python analyze.py PLATINUM
python analyze.py PALLADIUM
```

### Agriculture
```bash
python analyze.py CORN
python analyze.py WHEAT
python analyze.py SOYBEANS
python analyze.py "SOYBEAN OIL"
python analyze.py "LIVE CATTLE"
python analyze.py "LEAN HOGS"
```

### Softs
```bash
python analyze.py COFFEE
python analyze.py SUGAR
python analyze.py COCOA
python analyze.py COTTON
```

## Data Information

### Source
All data from CFTC: https://www.cftc.gov/MarketReports/CommitmentsofTraders/

### Update Schedule
- Published: Every Friday ~3:30 PM ET
- Covers: Previous Tuesday's positions
- Lag: 3 days

### Current Data
- **72,790 records** (2020-2024)
- All major futures contracts
- Legacy Futures Only reports

### Data Format
- Stored as Parquet files (efficient)
- Located in `data/legacy_fut/`
- Combined file: `all_years.parquet`

## Utilities

### Fix Data Issues
```bash
python utils/fix_data.py
```

Combines individual year files if `all_years.parquet` is missing.

### Test Downloads
```bash
python utils/test.py
```

Verifies download functionality.

### Verify Installation
```bash
python utils/verify.py
```

Checks all required packages installed.

## Troubleshooting

See **docs/TROUBLESHOOTING.md** for detailed solutions.

Quick fixes:
- **"Data file not found"**: Run `python utils/fix_data.py`
- **"Commodity not found"**: Run `python analyze.py` to list all
- **Import errors**: Run `pip install -r requirements.txt`

## Disclaimer

This tool is for educational and research purposes. COT analysis does not guarantee trading profits. Always:
- Do your own research
- Practice proper risk management
- Never risk more than you can afford to lose
- Consider COT as ONE input among many

Past performance does not indicate future results.

---

**Happy analyzing!** Remember: The best opportunities often appear when sentiment reaches extremes.
