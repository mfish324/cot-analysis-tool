# COT Analysis Tool

Analyze CFTC Commitment of Traders data to identify market extremes and trading opportunities.

## 🚀 Web App (Recommended!)

**Interactive web interface** - Easy point-and-click analysis:

```bash
# Install dependencies
pip install -r requirements.txt

# Run web app
streamlit run app.py
# or on Windows: run_app.bat
```

Opens in your browser at `http://localhost:8501`

**Features:**
- 📈 Interactive charts with zoom/pan
- 🔍 Extremes scanner with filters
- 🎯 Ticker symbol search
- 📊 Real-time COT Index
- 📱 Mobile-friendly

See [WEB_APP.md](WEB_APP.md) for full documentation.

## 💻 Command Line

```bash
# Analyze using ticker symbols
python analyze.py GC        # Gold
python analyze.py CL        # Crude Oil
python analyze.py ES        # S&P 500

# With charts
python analyze.py GC --chart

# Find extremes
python analyze.py --extremes
python analyze.py --extremes --top20
```

## Example Output

```
GOLD - COMMODITY EXCHANGE INC.
Date: 2024-12-31
------------------------------------------------------------
Open Interest:             458,584

Speculators:
  Long:                    282,907
  Short:                    35,628
  Net:                     247,279

Hedgers:
  Long:                     60,399
  Short:                   331,695
  Net:                    -271,296

COT INDEX:                    74.1
SIGNAL:                   NEUTRAL
```

## What is COT Analysis?

The COT report shows how different traders are positioned:
- **Speculators**: Often wrong at extremes
- **Hedgers**: Often right at turning points
- **COT Index (0-100)**: Current position vs history
  - **>80**: Overbought (potential top)
  - **<20**: Oversold (potential bottom)

## Installation

```bash
pip install -r requirements.txt
python utils/verify.py  # Verify installation
```

## Available Commodities

**Energies**: Crude Oil, Natural Gas, Gasoline
**Metals**: Gold, Silver, Copper, Platinum  
**Agriculture**: Corn, Wheat, Soybeans, Cattle
**Softs**: Coffee, Sugar, Cocoa, Cotton

Run `python analyze.py` for complete list.

## Data

✅ **72,790 records** (2020-2024)
✅ **All major commodities**
✅ **Ready for analysis**

### Update Data Weekly

```bash
# Run every Friday/Saturday to get latest data
python update_data.py
```

Data is published by CFTC every Friday (~3:30 PM ET). See **[docs/UPDATE_GUIDE.md](docs/UPDATE_GUIDE.md)** for complete update instructions.

## Documentation

- **[docs/GUIDE.md](docs/GUIDE.md)** - Complete usage guide
- **[docs/UPDATE_GUIDE.md](docs/UPDATE_GUIDE.md)** - How to update data weekly
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Problem solving
- **[docs/STATUS.md](docs/STATUS.md)** - Project status

## Project Structure

```
COT/
├── analyze.py          # Main tool - USE THIS
├── requirements.txt    # Dependencies
├── lib/               # Core modules
├── utils/             # Utility scripts
├── docs/              # Documentation
└── data/              # COT data (72K records)
```

## Utilities

```bash
python utils/verify.py     # Check installation
python utils/test.py       # Test downloads
python utils/fix_data.py   # Fix data files
```

## Examples

```bash
# Use ticker symbols (no quotes needed!)
python analyze.py GC         # Gold
python analyze.py CL         # Crude Oil
python analyze.py SI         # Silver
python analyze.py ES         # S&P 500
python analyze.py NG         # Natural Gas

# With charts
python analyze.py GC --chart
python analyze.py CL --chart

# Find extremes
python analyze.py --extremes
python analyze.py --extremes --top20

# List all tickers
python analyze.py --tickers
```

## Features

- **Ticker Symbols** - Use GC, CL, ES instead of long names
- **COT Index Analysis** - 0-100 scale showing positioning extremes
- **Visual Charts** - COT Index, Net Positions, Open Interest charts
- **Extremes Scanner** - Find all markets at overbought/oversold levels
- **Top 20 Filter** - Focus on highest volume markets
- **Weekly Updates** - Easy data refresh from CFTC

## Popular Tickers

| Ticker | Commodity | Ticker | Commodity |
|--------|-----------|--------|-----------|
| **GC** | Gold | **CL** | Crude Oil |
| **SI** | Silver | **NG** | Natural Gas |
| **HG** | Copper | **ES** | S&P 500 |
| **ZC** | Corn | **ZW** | Wheat |
| **ZS** | Soybeans | **LC** | Live Cattle |
| **KC** | Coffee | **SB** | Sugar |

Full list: `python analyze.py --tickers`

## Requirements

- Python 3.8+
- pandas, numpy, pyarrow, matplotlib

## License

MIT License

## Disclaimer

For educational purposes only. Not financial advice.

---

**Get started:** `python analyze.py GOLD`

For detailed documentation, see **[docs/GUIDE.md](docs/GUIDE.md)**
