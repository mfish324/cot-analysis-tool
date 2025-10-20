# COT Data Update Guide

## How to Update Data Every Week

COT data is published by the CFTC every **Friday afternoon** (around 3:30 PM ET) with positions from the **previous Tuesday**.

## Quick Update

### Simple Method (Recommended)

```bash
# Run this every Friday after 4 PM ET
python update_data.py
```

That's it! The script will:
1. Download the latest week's data
2. Update all combined files
3. Make new data available for analysis

### Manual Method

If you prefer manual control:

```bash
# 1. Download latest data
python -c "from lib.downloader import COTDownloader; d = COTDownloader(); d.download_year('legacy_fut', 2025)"

# 2. Recombine files
python utils/fix_data.py

# 3. Analyze
python analyze.py GOLD
```

## Weekly Update Schedule

### When Data is Released

**CFTC Release Schedule:**
- **Day**: Every Friday
- **Time**: ~3:30 PM Eastern Time
- **Covers**: Previous Tuesday's positions
- **Lag**: 3 business days

### Recommended Update Time

**Best time to update:** Friday evening or Saturday morning
- Data is guaranteed to be available
- Markets are closed (less rush)
- You have weekend to analyze

### Update Frequency

**Minimum:** Once per week (Friday/Saturday)
- COT data only updates weekly
- No benefit to updating more often

**Optional:** Check midweek if you missed Friday
- Data won't change until next Friday
- But you can catch up if you missed the update

## Step-by-Step Update Process

### Step 1: Run Update Script

```bash
python update_data.py
```

### Step 2: Verify Update

```bash
# Check latest date in data
python -c "import pandas as pd; df = pd.read_parquet('data/legacy_fut/all_years.parquet'); print(f'Latest data: {df[\"As of Date in Form YYYY-MM-DD\"].max()}')"
```

Should show the most recent Tuesday's date.

### Step 3: Analyze Fresh Data

```bash
python analyze.py GOLD
python analyze.py --extremes
```

## Automated Updates (Advanced)

### Windows Task Scheduler

Create a scheduled task to run every Saturday:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Saturday, 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `c:\Users\matto\projects\COT\update_data.py`
   - Start in: `c:\Users\matto\projects\COT`

### Linux/Mac Cron Job

Add to crontab (`crontab -e`):

```bash
# Run every Saturday at 9 AM
0 9 * * 6 cd /path/to/COT && python update_data.py
```

### Python Scheduler (Cross-Platform)

Create `scheduler.py`:

```python
import schedule
import time
from update_data import update_cot_data

# Schedule update every Saturday at 9 AM
schedule.every().saturday.at("09:00").do(update_cot_data)

print("COT Data Scheduler Running...")
print("Will update every Saturday at 9 AM")

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

Run: `python scheduler.py` (keep running in background)

## What Gets Updated

### Data Files Updated

```
data/
├── legacy_fut/
│   ├── 2025.parquet          ← Updated with latest week
│   └── all_years.parquet     ← Recombined with new data
├── disaggregated_fut/
│   ├── 2025.parquet          ← Updated
│   └── all_years.parquet     ← Recombined
└── tff_fut/
    ├── 2025.parquet          ← Updated
    └── all_years.parquet     ← Recombined
```

### What Stays the Same

- Historical data (2020-2024)
- Your analysis scripts
- Configuration files

## Troubleshooting Updates

### "No new data available yet"

**Causes:**
- Ran update before Friday 4 PM ET
- CFTC website maintenance
- Government holiday (no report)

**Solution:**
- Wait until Saturday and try again
- Check CFTC website: https://www.cftc.gov/MarketReports/CommitmentsofTraders/

### "404 Not Found"

**Normal if:**
- Running update for future year (e.g., running in December 2024 for 2025 data)
- CFTC hasn't published current year file yet

**Solution:**
- Download will automatically get latest available data
- Check previous year's data if current year unavailable

### "Data hasn't changed"

**Check if:**
- Already ran update this week
- Comparing same dates

**Verify:**
```bash
# Check latest record date
python -c "import pandas as pd; df = pd.read_parquet('data/legacy_fut/all_years.parquet'); print(df['As of Date in Form YYYY-MM-DD'].max())"
```

Should match the most recent Tuesday.

## Update Best Practices

### 1. Consistent Schedule

Update same time each week:
- **Good**: Every Saturday 9 AM
- **Bad**: Random times throughout week

### 2. Verify Before Analyzing

Always check latest date after update:
```bash
python analyze.py GOLD | grep "Date:"
```

### 3. Monitor for Gaps

If you miss a week, data will still update correctly. But for continuous monitoring, try not to miss updates.

### 4. Backup (Optional)

Before major updates, backup your data:
```bash
# Create backup
cp -r data data_backup_2025-01-04
```

### 5. Log Updates (Optional)

Keep a log of updates:
```bash
python update_data.py >> update_log.txt 2>&1
```

## Example Update Workflow

### My Weekly Routine

**Friday Evening (after market close):**
1. Run update: `python update_data.py`
2. Check for extremes: `python analyze.py --extremes`
3. Analyze key commodities:
   ```bash
   python analyze.py GOLD
   python analyze.py CRUDE_OIL
   python analyze.py S&P
   ```

**Weekend:**
4. Review positions that changed significantly
5. Look for new extremes (>80 or <20)
6. Plan trades for coming week

**Monday:**
7. Final check before markets open
8. Compare with price action

## Quick Reference

### Update Commands

```bash
# Full update (recommended)
python update_data.py

# Quick check latest date
python -c "import pandas as pd; print(pd.read_parquet('data/legacy_fut/all_years.parquet')['As of Date in Form YYYY-MM-DD'].max())"

# Manual update
python utils/fix_data.py

# Verify installation still good
python utils/verify.py
```

### Update Schedule Reminder

```
Monday:    ❌ No new data
Tuesday:   ❌ No new data (this is reporting day)
Wednesday: ❌ No new data
Thursday:  ❌ No new data
Friday:    ✅ NEW DATA RELEASED (~3:30 PM ET)
Saturday:  ✅ BEST TIME TO UPDATE
Sunday:    ✅ Can update if missed Saturday
```

## Historical Data vs New Data

### Current Setup

You have historical data from **2020-2024**.

### As You Update

- **2025 data** accumulates week by week
- **Historical data** remains unchanged
- **Combined file** includes both

### Long-Term

After a year of updates:
- **2020-2025**: Full historical range
- **2026 data**: Will accumulate next year
- Continue weekly updates to maintain current data

## Data Retention

### What to Keep

- **All yearly files**: Keep indefinitely
- **Combined files**: Auto-regenerated each update
- **Backup files**: Optional, delete after verified update

### What to Clean Up (Optional)

- Old backup files (>3 months)
- Update logs (>6 months)
- Temporary download files

## FAQ

### Q: Do I need to update if I'm only analyzing old data?
**A:** No, historical data doesn't change. Only update if you want current positions.

### Q: What if I miss several weeks?
**A:** No problem! Next update will include all missing weeks automatically.

### Q: Can I update daily?
**A:** You can, but data only changes once per week (Friday). Daily updates are unnecessary.

### Q: What if CFTC website is down?
**A:** Wait a few hours and retry. CFTC occasionally has maintenance.

### Q: Do updates cost anything?
**A:** No, CFTC data is free and public.

### Q: How much data will I accumulate?
**A:** ~2,600 records per year per commodity. Size is minimal (few MB per year).

---

## Summary

**Simple Weekly Update:**
```bash
python update_data.py
```

**Best Time:** Friday evening or Saturday morning

**Frequency:** Once per week

**Takes:** ~2-5 minutes

That's it! Your data stays current with minimal effort.
