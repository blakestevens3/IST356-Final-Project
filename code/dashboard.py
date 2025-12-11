# stocks_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium

CACHE_STOCKS_ENRICHED = "cache/stocks_enriched.csv"
CACHE_SECTOR_SUMMARY = "cache/sector_summary.csv"
CACHE_COUNTRY_SUMMARY = "cache/country_summary.csv"

@st.cache_data
def load_data():
    enriched = pd.read_csv(CACHE_STOCKS_ENRICHED)
    sector = pd.read_csv(CACHE_SECTOR_SUMMARY)
    country = pd.read_csv(CACHE_COUNTRY_SUMMARY)
    return enriched, sector, country

enriched_df, sector_df, country_df = load_data()

st.title("Equity Portfolio Explorer")

tab_overview, tab_map, tab_companies = st.tabs(["Overview", "Map", "Companies"])

with tab_overview:
    st.subheader("Sector allocation")
    fig_sector = px.bar(sector_df.sort_values('total_weight', ascending=False),
                        x='Sector', y='total_weight',
                        labels={'total_weight': 'Total Weight'})
    st.plotly_chart(fig_sector, use_container_width=True)

    st.subheader("Country allocation")
    fig_country = px.pie(country_df, names='Country', values='total_weight')
    st.plotly_chart(fig_country, use_container_width=True)

with tab_map:
    st.subheader("Company Headquarters Map")
    locs = (enriched_df
            .dropna(subset=['lat', 'lon'])
            .groupby(['City', 'State', 'Country', 'lat', 'lon'])
            .agg(total_weight=('Weight', 'sum'),
                 num_companies=('Symbol', 'count'))
            .reset_index())
    gdf = gpd.GeoDataFrame(
        locs,
        geometry=gpd.points_from_xy(locs['lon'], locs['lat']),
        crs="EPSG:4326"
    )
    m = folium.Map(location=[40, -95], zoom_start=3)
    for _, row in gdf.iterrows():
        popup = f"{row['City']}, {row['Country']}<br>"
        popup += f"Companies: {row['num_companies']}<br>"
        popup += f"Total Weight: {row['total_weight']:.2%}"
        folium.CircleMarker(
            location=(row['lat'], row['lon']),
            radius=5,
            popup=popup
        ).add_to(m)
    st_folium(m, width=700, height=500)

with tab_companies:
    st.subheader("Company drilldown")
    sector_choice = st.selectbox("Sector", sorted(enriched_df['Sector'].dropna().unique()))
    subset = enriched_df[enriched_df['Sector'] == sector_choice]
    symbol_choice = st.selectbox("Symbol", sorted(subset['Symbol'].unique()))
    row = subset[subset['Symbol'] == symbol_choice].iloc[0]

    st.write(f"**{row['Longname']}** ({row['Symbol']})")
    st.write(f"Sector: {row['Sector']} | Industry: {row['Industry']}")
    st.write(f"Weight: {row['Weight']:.2%}")
    st.write(f"Market Cap: {row['MarketcapBillions']:.2f} B")
    st.write(f"Revenue Growth: {row['Revenuegrowth']:.2%}")
    st.write("### Business summary")
    st.write(row['Longbusinesssummary'])
