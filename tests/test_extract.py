import os
import sys
import pandas as pd

# allow importing from /code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from code.extract_stocks import extract_stocks, geocode_locations 
import code.extract_stocks as module 


def test_extract_stocks_reads_csv_and_writes_cache(tmp_path):
    source = tmp_path / "stocks.csv"
    pd.DataFrame({"Ticker": ["AAA", "BBB"], "Marketcap": [10, 20]}).to_csv(source, index=False)

    cache_out = tmp_path / "stocks_raw.csv"
    module.CACHE_STOCKS_FILE = str(cache_out)  # redirect output

    df = extract_stocks(source_file=str(source))
    assert len(df) == 2
    assert cache_out.exists()


def test_geocode_locations_uses_cache_and_skips_api(tmp_path):
    cache_file = tmp_path / "locations.csv"

    pd.DataFrame([{
        "City": "Boston", "State": "MA", "Country": "USA",
        "full_location": "Boston, MA, USA", "lat": 42.36, "lon": -71.05
    }]).to_csv(cache_file, index=False)

    top = pd.DataFrame([{
        "City": "Boston", "State": "MA", "Country": "USA",
        "total_marketcap": 1,
        "full_location": "Boston, MA, USA"
    }])

