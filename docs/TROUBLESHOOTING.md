# COT Analysis Tool - Troubleshooting Guide

## Download Errors

### "404 Not Found" Errors

**Symptom**: You see errors like:
```
Error downloading 2025: 404 Client Error: Not Found for url: https://...
```

**Why This Happens**:
- The current year's data may not be available yet
- CFTC sometimes changes URL patterns
- The government shutdown (as of Oct 2025) means COT reports aren't being published

**Solution**:
This is normal and can be safely ignored. The tool will:
- Automatically skip unavailable years
- Use the most recent available data instead
- Try alternative URL patterns

**What You Get**:
- All historical data from available years (2020-2024 in quick mode)
- The tool works fine with this data

### Slow Downloads

**Symptom**: Downloads take a long time

**Why**: You're downloading large historical datasets from CFTC servers

**Solutions**:
1. Use quick mode (default): `tool.setup(start_year=2020, quick_mode=True)`
2. Download only specific report types you need
3. Use cached data - second run will be much faster

### Network Errors

**Symptom**: Connection timeouts or network errors

**Solutions**:
1. Check your internet connection
2. The CFTC website might be down temporarily - try again later
3. If behind a firewall/proxy, ensure access to cftc.gov

## Data Processing Errors

### "No data found for commodity: GOLD"

**Cause**: You haven't run setup or the data isn't processed yet

**Solution**:
```python
from cot_analysis import COTAnalysisTool

tool = COTAnalysisTool()
tool.setup(start_year=2020, quick_mode=True)  # This processes the data

# Now you can analyze
tool.analyze('GOLD')
```

### "File not found: processed data"

**Cause**: Data was downloaded but not processed

**Solution**:
```python
from cot_processor import COTProcessor

processor = COTProcessor()
processor.process_full_pipeline('disaggregated_fut')
processor.process_full_pipeline('legacy_fut')
processor.process_full_pipeline('tff_fut')
```

### "Commodity name not recognized"

**Cause**: Typo or unsupported commodity

**Solution**:
```python
# List all available commodities
tool = COTAnalysisTool()
commodities = tool.list_commodities()
print(commodities)

# Use exact names from the list
tool.analyze('CRUDE_OIL_WTI')  # Note the underscore format
```

## Visualization Errors

### Charts Not Generating

**Symptom**: No charts created in `charts/` directory

**Possible Causes**:
1. Missing dependencies
2. Permission issues
3. Display backend issues

**Solutions**:

1. Install all dependencies:
```bash
pip install -r requirements.txt
```

2. Check matplotlib backend:
```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

3. Verify write permissions:
```bash
# On Windows
icacls charts /grant Users:F

# On Linux/Mac
chmod 755 charts
```

### "No module named 'plotly'"

**Solution**:
```bash
pip install plotly
```

## Performance Issues

### Setup Takes Too Long

**Solutions**:
1. Use quick mode (downloads from 2020 only):
```python
tool.setup(start_year=2020, quick_mode=True)
```

2. Download specific report type only:
```python
from cot_downloader import COTDownloader

downloader = COTDownloader()
downloader.download_all_years('disaggregated_fut', start_year=2020)
```

### Memory Issues

**Symptom**: Python crashes or runs out of memory

**Solutions**:
1. Process one report type at a time
2. Don't load all years at once
3. Use specific year ranges
4. Close other applications

## Common Usage Mistakes

### Mistake 1: Wrong Report Type

```python
# Wrong - EUR is in TFF reports, not disaggregated
tool.analyze('EUR', report_type='disaggregated_fut')

# Correct
tool.analyze('EUR', report_type='tff_fut')
```

### Mistake 2: Not Running Setup

```python
tool = COTAnalysisTool()
tool.analyze('GOLD')  # Error! No data downloaded yet

# Should be:
tool = COTAnalysisTool()
tool.setup()  # Download and process first
tool.analyze('GOLD')  # Now works
```

### Mistake 3: Looking for Non-Futures Commodities

COT data is only available for:
- Futures contracts traded on U.S. exchanges
- Not available for stocks, ETFs, or spot markets

## Checking System Status

### Verify Installation

```python
# test_installation.py
import sys
import pandas as pd
import numpy as np
import matplotlib
import plotly
import seaborn
import requests

print("Python version:", sys.version)
print("Pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("Matplotlib:", matplotlib.__version__)
print("Plotly:", plotly.__version__)
print("All packages installed successfully!")
```

### Verify Data Downloaded

```python
from pathlib import Path

data_dir = Path('data')
if data_dir.exists():
    for report_type in ['legacy_fut', 'disaggregated_fut', 'tff_fut']:
        report_dir = data_dir / report_type
        if report_dir.exists():
            files = list(report_dir.glob('*.parquet'))
            print(f"{report_type}: {len(files)} files")
        else:
            print(f"{report_type}: directory not found")
else:
    print("Data directory not found - run setup first!")
```

### Verify Processed Data

```python
from pathlib import Path

processed_dir = Path('data/processed')
if processed_dir.exists():
    files = list(processed_dir.glob('*.parquet'))
    print(f"Processed files: {len(files)}")
    for f in files:
        print(f"  - {f.name}")
else:
    print("No processed data found - run tool.setup()")
```

## CFTC Website Issues

### Government Shutdown

As noted in the CFTC documentation, during government shutdowns:
- COT reports are not published
- Historical data remains available
- New data will resume when government operations return

**Impact**: Your tool will work with all historical data, but won't have the very latest week's data.

### Website Maintenance

CFTC occasionally performs maintenance on their servers.

**Solution**:
- Wait a few hours and try again
- Use cached data if available
- Check https://www.cftc.gov for status updates

## Getting Help

### Enable Verbose Error Messages

```python
import traceback

try:
    tool.analyze('GOLD')
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()  # Show full error
```

### Check Log Files

The tool prints detailed progress. To save to a file:

```bash
python cot_analysis.py --setup > setup_log.txt 2>&1
```

### Minimal Working Example

If you're having issues, try this minimal example:

```python
from cot_downloader import COTDownloader

# Test basic download
downloader = COTDownloader()
df = downloader.download_year('disaggregated_fut', 2024)

if df is not None:
    print(f"Success! Downloaded {len(df)} records")
    print(f"Columns: {list(df.columns[:5])}...")
else:
    print("Download failed - check internet connection")
```

## Still Having Issues?

If none of these solutions work:

1. Check your Python version (need 3.8+):
```bash
python --version
```

2. Reinstall dependencies:
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

3. Delete data directory and start fresh:
```bash
# Backup first if you have important data
rm -rf data/
python cot_analysis.py --setup
```

4. Try the test script:
```bash
python test_download.py
```

5. Check file permissions in your project directory

6. Make sure you're not behind a restrictive firewall blocking cftc.gov

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| 404 errors | Normal for current year - ignore |
| No data found | Run `tool.setup()` first |
| Slow downloads | Use `start_year=2020` |
| Wrong commodity | Use `tool.list_commodities()` |
| No charts | Check `pip install -r requirements.txt` |
| Memory issues | Process one report type at a time |
| Import errors | `pip install -r requirements.txt` |

## Contact & Support

For persistent issues:
- Check the README.md for correct usage
- Review USAGE_GUIDE.md for detailed examples
- Run examples.py to see working code
- Verify your Python and package versions match requirements
