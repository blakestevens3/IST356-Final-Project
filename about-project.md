# About My Project

Student Name:  Blake Stevens & Blake McClintic
Student Email:  pbsteven@syr.edu & bcmcclin@syr.edu

# What it does
This project builds an end-to-end ETL pipeline and interactive dashboard to explore a global equity portfolio.

# The pipeline:
- Extracts stock holdings from a CSV and caches the raw data.
- Enriches each company with numeric metrics (market cap in billions, weight %, etc.) and merges in geocoded HQ locations from a cached locations file.
- Aggregates the enriched data into sector- and country-level summaries for quick analysis.

On top of that, a Streamlit app (stocks_dashboard.py) lets the user:
- See headline metrics (number of companies, sectors, countries, total portfolio weight).
- Interactively explore sector and country allocation with switchable metrics (total weight, average market cap, number of companies).
- Drill down to individual companies to view their fundamentals and long business summary.
- View a map of the top 20 cities by total market cap, using pre-computed lat/lon and Folium/GeoPandas so each point shows a tooltip with city details on hover.

The project also integrates with the CENT APIs via apicalls.py (Google geocode, Azure sentiment / key phrases, weather), but in the final design the end user does not need to call geocode at runtime because locations are cached ahead of time to stay within daily API limits.

# How you run my project

1. Install dependencies (requirements.txt) In terminal, write "uv pip install --system -r requirements.txt

2. Prepare the data and cache folders -Make sure cache/ exists in the project root. -Place the original stock data CSV in the expected location (for example cache/stocks_data.csv or whatever path is configured in extract_stocks.py). -Make sure cache/locations_geocoded.csv exists and contains the top 20 cities with City, State, Country, full_location, lat, lon.

3. Run the ETL pipeline From the project root:

Extract + geocode (if needed for your initial run)
code/extract_stocks.py

Transform + create summaries

code/transform_stocks.py This will generate: cache/stocks_raw.csv cache/stocks_enriched.csv cache/sector_summary.csv cache/country_summary.csv

4. Run the Streamlit dashboard from the debugger code/dashboard.py

5. Run tests in VS Code In VS Code: configure Python tests with pytest, point to the tests/ folder, then run from the Testing tab.

The tests verify that extract/transform functions work correctly, that cache files are written, and that the map-style GeoDataFrame logic matches the ETL output.

# Other things you need to know

API keys and usage: The CENT API key is stored in apicalls.py and is used for Google geocoding, Azure text analytics, and weather. Because there is a daily quota, the project is designed so that geocoding only needs to be run once to populate cache/locations_geocoded.csv. After that, the user can run the ETL and dashboard without consuming extra geocode requests.

Caching strategy: All major steps write their results to the cache/ folder. This makes it easy to rerun the dashboard without re-running expensive operations and is also useful for testing, since test files can temporarily redirect cache paths to a tmp_path.

Map behavior: The Folium/GeoPandas map in the dashboard uses the top 20 cities by total market cap (computed in the extract step). Each city is aggregated so that one marker represents multiple companies, and the tooltip shows city name, number of companies, total weight, and total market cap.

Project structure: Core logic is separated into modules (extract_stocks.py, transform_stocks.py, stocks_dashboard.py, apicalls.py, pandaslib.py), and tests live in the tests/ folder. This follows the structure from earlier course units and makes it easier to reuse code and add more features later.