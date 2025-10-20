# COT Ticker Symbol Quick Reference

Quick reference for the most commonly used ticker symbols.

## Energies
- **CL** - Crude Oil (WTI)
- **NG** - Natural Gas
- **HO** - Heating Oil
- **RB** - RBOB Gasoline
- **BZ** - Brent Crude

## Precious Metals
- **GC** - Gold
- **SI** - Silver
- **PL** - Platinum
- **PA** - Palladium

## Base Metals
- **HG** - Copper

## Grains
- **C** or **ZC** - Corn
- **W** or **ZW** - Wheat
- **S** or **ZS** - Soybeans
- **SM** - Soybean Meal
- **BO** - Soybean Oil
- **O** - Oats
- **RR** - Rough Rice

## Livestock
- **LC** - Live Cattle
- **FC** - Feeder Cattle
- **LH** or **HE** - Lean Hogs

## Softs
- **KC** - Coffee
- **SB** - Sugar
- **CC** - Cocoa
- **CT** - Cotton
- **OJ** - Orange Juice
- **LB** - Lumber

## Stock Indices
- **ES** - S&P 500
- **NQ** - NASDAQ 100
- **YM** - Dow Jones
- **RTY** - Russell 2000
- **VIX** - VIX Volatility Index

## Bonds & Interest Rates
- **ZB** - 30-Year Treasury Bond
- **ZN** - 10-Year Treasury Note
- **ZF** - 5-Year Treasury Note
- **ZT** - 2-Year Treasury Note
- **GE** - Eurodollar
- **ZQ** - Fed Funds

## Currencies
- **DX** - US Dollar Index
- **6E** - Euro
- **6J** - Japanese Yen
- **6B** - British Pound
- **6C** - Canadian Dollar
- **6A** - Australian Dollar
- **6S** - Swiss Franc

## Crypto
- **BTC** - Bitcoin
- **ETH** - Ethereum

## Usage Examples

```bash
# Quick analysis
python analyze.py GC
python analyze.py CL
python analyze.py ES

# With charts
python analyze.py GC --chart
python analyze.py SI --chart

# List all tickers
python analyze.py --tickers
```

## Notes

- Ticker symbols are case-insensitive (GC, gc, Gc all work)
- You can still use full names: `python analyze.py GOLD`
- Full names with spaces need quotes: `python analyze.py "CRUDE OIL"`
- Tickers don't need quotes: `python analyze.py CL`
