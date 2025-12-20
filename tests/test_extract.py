import importlib.util
from pathlib import Path

import pandas as pd
import pytest


# Load "1_extract_stocks.py" WITHOUT using a normal import
def load_extract_module():
    project_root = Path(__file__).resolve().parents[1]   # goes from /tests to project folder
    module_path = project_root / "1_extract_stocks.py"

    spec = importlib.util.spec_from_file_location("extract_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_stocks_writes_cache_file(tmp_path, monkeypatch):
    m = load_extract_module()

    # Make a fake source CSV
    source = tmp_path / "stocks_data.csv"
    pd.DataFrame({"Ticker": ["AAA"], "Marketcap": [10]}).to_csv(source, index=False)

    # Redirect the cache output to a temp file
    cache_out = tmp_path / "stocks_raw.csv"
    monkeypatch.setattr(m, "CACHE_STOCKS_FILE", str(cache_out))

    # Run + check
    m.extract_stocks(source_file=str(source))
    assert cache_out.exists()


def test_geocode_locations_does_not_call_api_if_cached(tmp_path, monkeypatch):
    m = load_extract_module()

    cache_file = tmp_path / "locations_geocoded.csv"

    # Pre-fill cache with Boston
    pd.DataFrame([{
        "City": "Boston", "State": "MA", "Country": "USA",
        "full_location": "Boston, MA, USA", "lat": 42.36, "lon": -71.05
    }]).to_csv(cache_file, index=False)

    top = pd.DataFrame([{
        "City": "Boston", "State": "MA", "Country": "USA",
        "total_marketcap": 1,
        "full_location": "Boston, MA, USA"
    }])

    calls = {"n": 0}

    def fake_geocode(_):
        calls["n"] += 1
        return {"results": [{"geometry": {"location": {"lat": 0, "lng": 0}}}]}

    monkeypatch.setattr(m, "geocode", fake_geocode)

    m.geocode_locations(top, cache_file=str(cache_file))

    assert calls["n"] == 0
