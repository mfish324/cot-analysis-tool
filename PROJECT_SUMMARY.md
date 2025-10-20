# COT Analysis Tool - Project Summary

## Overview
A comprehensive Python-based tool for analyzing CFTC Commitment of Traders (COT) data to identify market extremes and trading opportunities.

## Key Features Implemented

### 1. Core Analysis
- **COT Index Calculation** - Normalized 0-100 scale showing current positioning relative to 3-year history
- **Extremes Detection** - Identifies markets at overbought (>80) or oversold (<20) levels
- **Multi-Report Support** - Legacy, Disaggregated, and TFF report types
- **Real-time Analysis** - Analyze 600+ markets instantly

### 2. Ticker Symbol Support
- **56+ Ticker Symbols** - Easy shorthand for commodities (GC for Gold, CL for Crude Oil, ES for S&P 500)
- **No Quotes Needed** - Simple usage: `python analyze.py GC`
- **Case Insensitive** - Works with any case (gc, GC, Gc)
- **Full Name Fallback** - Still supports full commodity names

### 3. Visual Charts
- **COT Index Chart** - Time series with overbought/oversold zones
- **Net Positions Chart** - Speculators vs Commercials positioning
- **Comprehensive Chart** - 3-panel view with all key metrics
- **High-Quality Output** - 150 DPI PNG files suitable for reports

### 4. Extremes Scanner
- **Full Market Scan** - Scan all 600+ markets for extremes
- **Top 20 Filter** - Focus on highest volume/liquidity markets
- **Open Interest Display** - See market size alongside COT Index
- **Sorted Results** - Markets sorted by extreme level

### 5. Data Management
- **Automated Downloads** - Download historical data from CFTC
- **Weekly Updates** - Easy update script for latest data
- **Data Validation** - Automatic fixing and combining of data files
- **Efficient Storage** - Parquet format for fast loading

## Project Structure

```
COT/
├── analyze.py              # Main analysis tool
├── update_data.py          # Weekly data updater
├── requirements.txt        # Python dependencies
├── README.md              # Quick start guide
├── TICKERS.md             # Ticker symbol reference
├── LICENSE                # MIT License
│
├── lib/                   # Core modules
│   ├── downloader.py      # Data download from CFTC
│   ├── processor.py       # Data processing & cleaning
│   ├── analyzer.py        # COT analysis calculations
│   ├── charting.py        # Chart generation
│   ├── tickers.py         # Ticker symbol mapping
│   └── visualizer.py      # Additional visualizations
│
├── utils/                 # Utility scripts
│   ├── verify.py          # Installation verification
│   ├── test.py            # Download testing
│   └── fix_data.py        # Data file repairs
│
├── docs/                  # Documentation
│   ├── GUIDE.md           # Complete usage guide
│   ├── UPDATE_GUIDE.md    # Weekly update instructions
│   ├── TROUBLESHOOTING.md # Problem solving
│   └── STATUS.md          # Project status
│
├── charts/                # Generated charts
│   └── README.md          # Chart interpretation guide
│
└── data/                  # COT data (not in git)
    ├── legacy_fut/
    ├── disaggregated_fut/
    └── tff_fut/
```

## Usage Examples

### Basic Analysis
```bash
# Using ticker symbols (easiest)
python analyze.py GC              # Gold
python analyze.py CL              # Crude Oil
python analyze.py ES              # S&P 500

# Using full names
python analyze.py GOLD
python analyze.py "CRUDE OIL"
```

### With Charts
```bash
python analyze.py GC --chart
python analyze.py SI --chart
```

### Finding Extremes
```bash
# All markets
python analyze.py --extremes

# Top 20 by volume
python analyze.py --extremes --top20
```

### Help & Information
```bash
python analyze.py --help         # Show help
python analyze.py --tickers      # List all tickers
python analyze.py               # List all commodities
```

## Technical Details

### Data Source
- CFTC (Commodity Futures Trading Commission)
- Published every Friday ~3:30 PM ET
- Historical data from 2020-present
- 70,000+ records across 600+ markets

### Calculations
- **COT Index**: `((Current - Min) / (Max - Min)) * 100`
- **Lookback Period**: 156 weeks (3 years)
- **Thresholds**: >80 overbought, <20 oversold

### Dependencies
- pandas - Data manipulation
- numpy - Numerical calculations
- matplotlib - Chart generation
- requests - Data downloads
- pyarrow - Efficient data storage

## Key Files

| File | Purpose |
|------|---------|
| `analyze.py` | Main tool - analyze commodities |
| `update_data.py` | Update data weekly |
| `lib/tickers.py` | Ticker symbol mapping |
| `lib/charting.py` | Chart generation |
| `lib/downloader.py` | Download COT data |
| `utils/fix_data.py` | Repair data files |

## Documentation

- **README.md** - Quick start and examples
- **TICKERS.md** - Complete ticker reference
- **docs/GUIDE.md** - Comprehensive usage guide
- **docs/UPDATE_GUIDE.md** - Weekly update process
- **docs/TROUBLESHOOTING.md** - Common issues
- **charts/README.md** - Chart interpretation

## Installation

```bash
# Clone repository
git clone <repo-url>
cd COT

# Install dependencies
pip install -r requirements.txt

# Verify installation
python utils/verify.py

# Download data (first time only)
python update_data.py

# Start analyzing
python analyze.py GC
```

## Development Timeline

1. **Initial Setup** - Data download and storage
2. **Core Analysis** - COT Index calculation and interpretation
3. **Bug Fixes** - Performance warnings, missing files, encoding issues
4. **Codebase Cleanup** - Organized structure, removed redundant files
5. **Extremes Scanner** - Added --extremes functionality
6. **Chart Generation** - Visual analysis with matplotlib
7. **Ticker Symbols** - Easy-to-use shorthand symbols
8. **Top 20 Filter** - Focus on liquid markets
9. **Documentation** - Complete guides and references

## Features Summary

✅ 56+ ticker symbols
✅ 600+ commodities supported
✅ COT Index (0-100 scale)
✅ Visual charts (3 types)
✅ Extremes scanner
✅ Top 20 filter
✅ Weekly updates
✅ Complete documentation
✅ Tested and working

## Next Steps for Users

1. Install dependencies: `pip install -r requirements.txt`
2. Download data: `python update_data.py`
3. Analyze: `python analyze.py GC --chart`
4. Update weekly: `python update_data.py`

## License

MIT License - See LICENSE file

## Disclaimer

This tool is for educational and research purposes only. Not financial advice.

---

**Created:** October 2025
**Version:** 1.0.0
**Status:** Complete and Production Ready
