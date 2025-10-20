"""
Verify that all required packages are installed correctly
"""

import sys

def check_installation():
    """Check if all required packages are installed"""

    print("=" * 60)
    print("COT ANALYSIS TOOL - INSTALLATION VERIFICATION")
    print("=" * 60)

    # Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("  WARNING: Python 3.8+ recommended")

    # Check required packages
    packages = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical operations',
        'requests': 'HTTP downloads',
        'matplotlib': 'Static charts',
        'seaborn': 'Enhanced visualizations',
        'plotly': 'Interactive charts',
        'pyarrow': 'Parquet file support',
        'tqdm': 'Progress bars',
    }

    print("\nChecking required packages:")
    print("-" * 60)

    all_installed = True
    missing = []

    for package, description in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            status = "OK"
            print(f"  {status:4s} {package:15s} v{version:10s} - {description}")
        except ImportError:
            all_installed = False
            missing.append(package)
            print(f"  MISS {package:15s} {'':11s} - {description}")

    # Special check for pyarrow (critical for parquet files)
    print("\nSpecial checks:")
    print("-" * 60)

    try:
        import pandas as pd
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        test_df.to_parquet('test_verify.parquet')
        pd.read_parquet('test_verify.parquet')
        import os
        os.remove('test_verify.parquet')
        print("  OK   Parquet read/write working")
    except Exception as e:
        print(f"  FAIL Parquet support: {e}")
        all_installed = False

    # Summary
    print("\n" + "=" * 60)
    if all_installed:
        print("STATUS: All packages installed correctly!")
        print("\nYou're ready to use the COT Analysis Tool.")
        print("\nNext steps:")
        print("  1. python analyze.py --setup")
        print("  2. python analyze.py --analyze GOLD")
    else:
        print("STATUS: Missing packages detected")
        print("\nPlease install missing packages:")
        if missing:
            print(f"\n  pip install {' '.join(missing)}")
        else:
            print("\n  pip install -r requirements.txt")
    print("=" * 60)

    return all_installed


if __name__ == "__main__":
    check_installation()
