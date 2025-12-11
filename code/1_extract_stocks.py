import os
import pandas as pd
from requests.exceptions import HTTPError
from apicalls import geocode   # from hw 6

SOURCE_FILE = "cache/stocks_data.csv"
CACHE_STOCKS_FILE = "cache/stocks_raw.csv"
CACHE_LOCATIONS_FILE = "cache/locations_geocoded.csv"

def extract_stocks(source_file: str = SOURCE_FILE) -> pd.DataFrame:
    #Load the raw holdings file and cache it.
    df = pd.read_csv(source_file)
    df.to_csv(CACHE_STOCKS_FILE, index=False)
    return df


def load_location_cache(cache_file: str = CACHE_LOCATIONS_FILE) -> pd.DataFrame:
    #Load existing geocode cache if it exists, otherwise return empty DF.
    if os.path.exists(cache_file):
        return pd.read_csv(cache_file)
    return pd.DataFrame(
        columns=["City", "State", "Country", "full_location", "lat", "lon"]
    )


def save_location_cache(cache_df: pd.DataFrame, cache_file: str = CACHE_LOCATIONS_FILE) -> None:
    cache_df.to_csv(cache_file, index=False)


def select_top_cities(stocks_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    '''
    Use pandas to find the top N city/state/country combos by TOTAL market cap.

    Returns a DataFrame with columns:
    City, State, Country, total_marketcap, full_location
    '''
    df = stocks_df.copy()

    # Make sure Marketcap is numeric
    df["Marketcap"] = pd.to_numeric(df["Marketcap"], errors="coerce")

    # Group by location and sum market cap
    grouped = (
        df.dropna(subset=["Marketcap"])
          .groupby(["City", "State", "Country"], dropna=False)["Marketcap"]
          .sum()
          .reset_index(name="total_marketcap")
          .sort_values("total_marketcap", ascending=False)
          .head(n)
    )

    grouped["full_location"] = (
        grouped["City"].fillna("") + ", " +
        grouped["State"].fillna("") + ", " +
        grouped["Country"].fillna("")
    )

    return grouped


def geocode_locations(
    top_cities_df: pd.DataFrame,
    cache_file: str = CACHE_LOCATIONS_FILE,
    max_new_requests: int = 50  # safe upper bound; only 20 needed anyway
) -> pd.DataFrame:
    """
    Geocode ONLY the top cities DataFrame, using a CSV cache so we don't
    re-hit the API. This will typically be <= 20 locations.
    """
    # 1. Load existing cache
    cache_df = load_location_cache(cache_file)
    cache_dict = {
        row["full_location"]: (row["lat"], row["lon"])
        for _, row in cache_df.iterrows()
    }

    new_rows = []
    new_calls = 0

    for _, row in top_cities_df.iterrows():
        full_loc = row["full_location"].strip()

        if not full_loc:
            continue

        # Already cached → skip API call
        if full_loc in cache_dict:
            continue

        if new_calls >= max_new_requests:
            print(f"[INFO] Reached max_new_requests={max_new_requests}, stopping.")
            break

        try:
            # cent geocode: sends ?location=<full_loc> under the hood
            geo = geocode(full_loc)
            new_calls += 1

            results = geo.get("results", [])
            if not results:
                print(f"[WARN] No geocode results for '{full_loc}'")
                continue

            loc_obj = results[0]["geometry"]["location"]
            lat = loc_obj["lat"]
            lon = loc_obj["lng"]

            new_rows.append({
                "City": row["City"],
                "State": row["State"],
                "Country": row["Country"],
                "full_location": full_loc,
                "lat": lat,
                "lon": lon
            })

        except HTTPError as e:
            print(f"[ERROR] Geocode failed for '{full_loc}': {e}")
            continue

    # 2. Append new rows and save updated cache
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        cache_df = pd.concat([cache_df, new_df], ignore_index=True)

    save_location_cache(cache_df, cache_file)
    print(f"[INFO] Cache now has {len(cache_df)} locations (added {len(new_rows)} this run).")

    return cache_df


if __name__ == "__main__":
    stocks = extract_stocks()
    top_cities = select_top_cities(stocks, n=20)
    print("Top 20 cities by total market cap:")
    print(top_cities[["City", "State", "Country", "total_marketcap"]])

    locations = geocode_locations(top_cities)
    print(f"Geocoded locations (cached): {len(locations)} rows.")