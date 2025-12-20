import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from code.transform_stocks import enrich_stocks, sector_summary, country_summary  
import code.transform_stocks as module  


def test_enrich_and_merges_locations(tmp_path):
    module.CACHE_STOCKS_ENRICHED = str(tmp_path / "stocks_enriched.csv")

    stocks_df = pd.DataFrame([{
        "Symbol": "AAA",
        "Sector": "Tech",
        "City": "Boston",
        "State": "MA",
        "Country": "USA",
        "Currentprice": "10",
        "Marketcap": "1000000000",   
        "Ebitda": "5",
        "Revenuegrowth": "0.10",
        "Fulltimeemployees": "100",
        "Weight": "0.02"
    }])

    loc_df = pd.DataFrame([{
        "City": "Boston",
        "State": "MA",
        "Country": "USA",
        "full_location": "Boston, MA, USA",
        "lat": 42.36,
        "lon": -71.05
    }])

    df = enrich_stocks(stocks_df, loc_df)

    assert "MarketcapBillions" in df.columns
    assert "WeightPercent" in df.columns
    assert "lat" in df.columns and "lon" in df.columns
    assert os.path.exists(module.CACHE_STOCKS_ENRICHED)


def test_sector_and_country_summary(tmp_path):
    # Redirect cache files to temp folder
    module.CACHE_SECTOR_SUMMARY = str(tmp_path / "sector_summary.csv")
    module.CACHE_COUNTRY_SUMMARY = str(tmp_path / "country_summary.csv")

    enriched_df = pd.DataFrame([
        {"Symbol": "AAA", "Sector": "Tech",   "Country": "USA", "Weight": 0.02, "Revenuegrowth": 0.10, "MarketcapBillions": 1.0},
        {"Symbol": "BBB", "Sector": "Tech",   "Country": "USA", "Weight": 0.03, "Revenuegrowth": 0.20, "MarketcapBillions": 2.0},
        {"Symbol": "CCC", "Sector": "Health", "Country": "UK",  "Weight": 0.05, "Revenuegrowth": 0.00, "MarketcapBillions": 3.0},
    ])

    sec = sector_summary(enriched_df)
    ctry = country_summary(enriched_df)

    assert set(sec["Sector"]) == {"Tech", "Health"}
    assert set(ctry["Country"]) == {"USA", "UK"}
    assert os.path.exists(module.CACHE_SECTOR_SUMMARY)
    assert os.path.exists(module.CACHE_COUNTRY_SUMMARY)
