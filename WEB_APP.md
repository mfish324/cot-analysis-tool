# COT Analysis Web App

Interactive web interface for analyzing Commitment of Traders data.

## Features

### 📈 Analyze Commodity
- Search by ticker symbol (GC, CL, ES) or full name
- Real-time COT Index calculation (0-100 scale)
- Interactive charts with Plotly
- Detailed position breakdowns
- Automatic signal interpretation

### 🔍 Scan Extremes
- Scan all 600+ markets for extremes
- Adjustable overbought/oversold thresholds
- Filter to top 20 by volume
- Sortable results table
- Split view: overbought vs oversold

### 📚 Ticker Reference
- Complete ticker symbol guide
- Organized by category
- Easy reference while analyzing

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Data (First Time Only)
```bash
python update_data.py
```

### 3. Run Web App

**Windows:**
```bash
run_app.bat
```

**Mac/Linux:**
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Usage

### Analyze a Commodity

1. Select "📈 Analyze Commodity" from the sidebar
2. Choose search method:
   - **Ticker Symbol**: Select category and ticker (e.g., Metals > GC)
   - **Full Name**: Select from dropdown list
3. Click "🔍 Analyze"
4. View results:
   - COT Index and signal
   - Position details
   - Interactive charts

### Scan for Extremes

1. Select "🔍 Scan Extremes" from the sidebar
2. Adjust thresholds:
   - **Overbought**: Default 80 (adjustable 70-95)
   - **Oversold**: Default 20 (adjustable 5-30)
3. Optionally check "Top 20 by Volume Only"
4. Click "🔍 Scan Markets"
5. View results in split view:
   - Left: Overbought markets
   - Right: Oversold markets

### View Ticker Reference

1. Select "📚 Ticker Reference" from the sidebar
2. Browse ticker symbols by category
3. Use tickers for quick analysis

## Screenshots

### Main Analysis Screen
- Large metrics display
- COT Index with signal
- Detailed positions
- Interactive charts

### Extremes Scanner
- Threshold sliders
- Real-time scanning
- Sortable results
- Volume filtering

### Charts
- **COT Index**: Time series with zones
- **Net Positions**: Specs vs Commercials
- **Open Interest**: Market volume
- All charts are interactive (zoom, pan, hover)

## Advanced Features

### Interactive Charts
- **Zoom**: Click and drag
- **Pan**: Shift + drag
- **Reset**: Double click
- **Hover**: See exact values
- **Download**: Click camera icon

### Caching
- Data loaded once and cached
- Fast subsequent analyses
- Automatic refresh every hour
- Manual refresh: Ctrl+R

### Responsive Design
- Works on desktop and tablet
- Wide layout for charts
- Collapsible sidebar
- Mobile-friendly

## Customization

### Change Port
```bash
streamlit run app.py --server.port 8502
```

### Disable Auto-Open Browser
```bash
streamlit run app.py --server.headless true
```

### Run on Network
```bash
streamlit run app.py --server.address 0.0.0.0
```

## Troubleshooting

### App Won't Start
```bash
# Check if Streamlit is installed
pip install streamlit

# Try running directly
python -m streamlit run app.py
```

### Data Not Found Error
```bash
# Download data first
python update_data.py

# Verify data exists
ls data/legacy_fut/all_years.parquet
```

### Charts Not Displaying
```bash
# Install plotly
pip install plotly

# Clear cache and restart
# In browser: Settings > Clear Cache
```

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

## Keyboard Shortcuts

- **R**: Rerun app
- **C**: Clear cache
- **Q**: Close sidebar
- **E**: Open settings
- **?**: Show shortcuts

## Tips

1. **Use Ticker Symbols**: Much faster than typing full names
2. **Bookmark Favorites**: Browser bookmarks for quick access
3. **Adjust Thresholds**: Fine-tune extremes scanner
4. **Export Charts**: Click camera icon on charts
5. **Check Regularly**: Update data weekly for latest positions

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Deploy!

Your app will be live at: `https://your-app.streamlit.app`

### Deploy to Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT --server.headless true
   ```

2. Deploy:
   ```bash
   heroku create
   git push heroku main
   ```

## Performance

- Initial load: ~2 seconds
- Analysis: <1 second (cached)
- Extremes scan: 5-10 seconds (600+ markets)
- Chart rendering: <1 second

## Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ❌ Internet Explorer (not supported)

## Updates

To get the latest data:
```bash
python update_data.py
```

App will automatically use new data on next analysis.

---

**Need Help?** Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) or open an issue.
