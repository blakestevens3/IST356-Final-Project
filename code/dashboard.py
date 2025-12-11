"""
stocks_dashboard.py

Streamlit dashboard for exploring an equity portfolio.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import geopandas as gpd
import streamlit_folium as sf

st.set_page_config(layout="wide")

ENRICHED_FILE = "./cache/stocks_enriched.csv"
SECTOR_FILE = "./cache/sector_summary.csv"
COUNTRY_FILE = "./cache/country_summary.csv"


@st.cache_data
def load_data():
    enriched = pd.read_csv(ENRICHED_FILE)
    sector = pd.read_csv(SECTOR_FILE)
    country = pd.read_csv(COUNTRY_FILE)
    return enriched, sector, country


enriched_df, sector_df, country_df = load_data()

st.title("Equity Portfolio Explorer")
st.caption(
    "Explore an equity portfolio using the ETL pipeline output. "
    "Use the controls to change the graphs, filter the data, and "
    "view the top cities with geocoded locations on a map."
)


total_companies = enriched_df["Symbol"].nunique()
total_sectors = enriched_df["Sector"].nunique()
total_countries = enriched_df["Country"].nunique()
total_weight = enriched_df["Weight"].sum()

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Companies", f"{total_companies}")
col_b.metric("Sectors", f"{total_sectors}")
col_c.metric("Countries", f"{total_countries}")
col_d.metric("Total Portfolio Weight", f"{total_weight:.2f}")

st.write("")


st.header("Sector and Country Allocation")

st.subheader("Sector Allocation Controls")
metric_choice = st.selectbox(
    "Select metric for sector chart",
    (
        "Total Weight",
        "Average Market Cap (Billions)",
        "Number of Companies",
    ),
)

use_ascending = st.button("Sort sectors ascending instead of descending")

if "total_weight" not in sector_df.columns or "avg_marketcap_bil" not in sector_df.columns:
    sector_df = (
        enriched_df.groupby("Sector", dropna=False)
        .agg(
            total_weight=("Weight", "sum"),
            avg_marketcap_bil=("Marketcap", "mean"),
            num_companies=("Symbol", "count"),
        )
        .reset_index()
    )

if metric_choice == "Total Weight":
    y_col = "total_weight"
    y_label = "Total Weight"
elif metric_choice == "Average Market Cap (Billions)":
    y_col = "avg_marketcap_bil"
    y_label = "Average Market Cap (Billions)"
else:
    y_col = "num_companies"
    y_label = "Number of Companies"

sector_plot_df = sector_df.sort_values(
    y_col, ascending=use_ascending
)

st.subheader(f"Sector Allocation ({y_label})")
fig1, ax1 = plt.subplots(figsize=(8, 4))
sns.barplot(
    data=sector_plot_df,
    x="Sector",
    y=y_col,
    ax=ax1,
)
ax1.set_xlabel("Sector")
ax1.set_ylabel(y_label)
ax1.set_title(f"{y_label} by Sector")
ax1.tick_params(axis="x", rotation=45, labelright=True)
st.pyplot(fig1)

st.write("")

st.subheader("Country Allocation (Total Weight)")
if "total_weight" not in country_df.columns:
    country_df = (
        enriched_df.groupby("Country", dropna=False)["Weight"]
        .sum()
        .reset_index(name="total_weight")
    )

country_plot_df = country_df.sort_values("total_weight", ascending=False)

fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(
    data=country_plot_df,
    x="Country",
    y="total_weight",
    ax=ax2,
)
ax2.set_xlabel("Country")
ax2.set_ylabel("Total Weight")
ax2.set_title("Total Portfolio Weight by Country")
ax2.tick_params(axis="x", rotation=45)
st.pyplot(fig2)

st.write("")


st.header("Company Drilldown")

country_options = ["All Countries"] + sorted(
    enriched_df["Country"].dropna().unique().tolist()
)
selected_country = st.selectbox("Filter by country", country_options)

if selected_country == "All Countries":
    drilldown_df = enriched_df.copy()
else:
    drilldown_df = enriched_df[enriched_df["Country"] == selected_country]

sector_options = sorted(drilldown_df["Sector"].dropna().unique().tolist())
selected_sector = st.selectbox("Select a sector", sector_options)

sector_subset = drilldown_df[drilldown_df["Sector"] == selected_sector]

symbol_options = sorted(sector_subset["Symbol"].unique().tolist())
selected_symbol = st.selectbox("Select a company (symbol)", symbol_options)

company_row = sector_subset[sector_subset["Symbol"] == selected_symbol].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Weight", f"{company_row['Weight']:.2f}")
if "MarketcapBillions" in company_row:
    c2.metric("Market Cap (B)", f"{company_row['MarketcapBillions']:.2f}")
else:
    c2.metric("Market Cap", f"{company_row['Marketcap']:.2e}")
if "Revenuegrowth" in company_row:
    c3.metric("Revenue Growth", f"{company_row['Revenuegrowth']:.2%}")

st.write(
    f"**{company_row.get('Longname', selected_symbol)}** "
    f"({company_row['Symbol']})"
)
st.write(
    f"Sector: {company_row['Sector']} | Industry: {company_row['Industry']}"
)
st.write(
    f"Headquarters: {company_row.get('City', '')}, "
    f"{company_row.get('State', '')}, "
    f"{company_row.get('Country', '')}"
)

st.subheader("Business Summary")
st.write(company_row.get("Longbusinesssummary", "No summary available."))

st.write("")


st.header("Top Cities Map (Geocoded Data)")

st.caption(
    "This map uses the latitude and longitude values from the ETL step. "
    "Only cities that were geocoded and saved in the cache are shown. "
    "Hover over a point to see the city."
)

map_sector_options = ["All Sectors"] + sorted(
    enriched_df["Sector"].dropna().unique().tolist()
)
selected_map_sector = st.selectbox(
    "Filter map by sector", map_sector_options
)

if selected_map_sector == "All Sectors":
    map_base = enriched_df.copy()
else:
    map_base = enriched_df[enriched_df["Sector"] == selected_map_sector]

map_base = map_base.dropna(subset=["lat", "lon"]).copy()

city_group = (
    map_base.groupby(
        ["City", "State", "Country", "lat", "lon"], dropna=False
    )
    .agg(
        total_marketcap=("Marketcap", "sum"),
        total_weight=("Weight", "sum"),
        num_companies=("Symbol", "count"),
    )
    .reset_index()
)

# keep top 20 cities by total market cap, like in your ETL
city_group = city_group.sort_values("total_marketcap", ascending=False).head(20)

if not city_group.empty:
    # Create a GeoDataFrame like in map_dashboard.py
    gdf = gpd.GeoDataFrame(
        city_group,
        geometry=gpd.points_from_xy(city_group["lon"], city_group["lat"]),
        crs="EPSG:4326",
    )

    # Center the map around the average of the points
    center_lat = gdf["lat"].mean()
    center_lon = gdf["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

    # Use GeoDataFrame.explore like Unit 8, but add a tooltip for hover
    portfolio_map = gdf.explore(
        column="total_marketcap",
        m=m,
        cmap="magma",
        legend=True,
        legend_kwds={"caption": "Total Market Cap"},
        marker_type="circle",
        marker_kwds={"radius": 50, "fill": True},
        tooltip=["City", "Country", "num_companies", "total_weight"],
    )

    sf.folium_static(portfolio_map, width=800, height=500)

    st.subheader("City Details")
    st.dataframe(
        city_group[
            [
                "City",
                "State",
                "Country",
                "total_marketcap",
                "total_weight",
                "num_companies",
            ]
        ]
    )
else:
    st.warning("No geocoded cities available to show on the map.")
