import pandas as pd

CACHE_STOCKS_FILE = "cache/stocks_raw.csv"
CACHE_LOCATIONS_FILE = "cache/locations_geocoded.csv"
CACHE_STOCKS_ENRICHED = "cache/stocks_enriched.csv"
CACHE_SECTOR_SUMMARY = "cache/sector_summary.csv"
CACHE_COUNTRY_SUMMARY = "cache/country_summary.csv"

def load_raw() -> pd.DataFrame:
    return pd.read_csv(CACHE_STOCKS_FILE) # Load raw stocks data from original file

def load_locations() -> pd.DataFrame:
    return pd.read_csv(CACHE_LOCATIONS_FILE) # Load geocoded locations from cache

def enrich_stocks(stocks_df: pd.DataFrame, loc_df: pd.DataFrame) -> pd.DataFrame:
    df = stocks_df.copy() # Create a copy to avoid modifying original
    # Make sure numeric columns are numeric
    numeric_cols = ['Currentprice', 'Marketcap', 'Ebitda',
                    'Revenuegrowth', 'Fulltimeemployees', 'Weight'] # columns to convert
    for col in numeric_cols: # convert each to numeric
        df[col] = pd.to_numeric(df[col], errors='coerce') # coerce errors to NaN

    # Derived metrics
    df['MarketcapBillions'] = df['Marketcap'] / 1e9 # Market cap in billions
    df['WeightPercent'] = df['Weight'] * 100 # Weight as percentage

    # Join geocode info on City, State, Country
    df = df.merge(loc_df, on=['City', 'State', 'Country'], how='left') # left join to keep all stocks

    df.to_csv(CACHE_STOCKS_ENRICHED, index=False) # Cache enriched data
    return df # Return enriched DataFrame

def sector_summary(enriched_df: pd.DataFrame) -> pd.DataFrame: # Sector summary
    sector_df = (enriched_df
                 .groupby('Sector', dropna=False) # group by Sector
                 .agg(
                     total_weight=('Weight', 'sum'),
                     avg_revenue_growth=('Revenuegrowth', 'mean'),
                     avg_marketcap_bil=('MarketcapBillions', 'mean'),
                     num_companies=('Symbol', 'count')
                 ) #aggregate metrics
                 .reset_index()) # reset index to turn groupby object back to DataFrame
    sector_df.to_csv(CACHE_SECTOR_SUMMARY, index=False) # Cache sector summary
    return sector_df # Return sector summary DataFrame
'''
sector_summary and country_summary functions compute aggregate statistics
for stocks grouped by sector and country, respectively. They save the results
to CSV files for later analysis.
'''
def country_summary(enriched_df: pd.DataFrame) -> pd.DataFrame:
    country_df = (enriched_df
                  .groupby('Country', dropna=False)
                  .agg(
                      total_weight=('Weight', 'sum'),
                      num_companies=('Symbol', 'count')
                  )
                  .reset_index()) # reset index to turn groupby object back to DataFrame
    country_df.to_csv(CACHE_COUNTRY_SUMMARY, index=False) # Cache country summary
    return country_df 

if __name__ == "__main__":
    raw = load_raw()
    locs = load_locations()
    enriched = enrich_stocks(raw, locs)
    sector_summary(enriched)
    country_summary(enriched)
