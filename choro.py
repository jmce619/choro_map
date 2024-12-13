import streamlit as st
import geopandas as gpd
import plotly.graph_objects as go

# Example: Load or define `map_gdf` here
# map_gdf = gpd.read_file("path_to_your_shapefile_or_geojson")
# For this example, we assume map_gdf is already in memory

# Make sure map_gdf is in EPSG:4326
def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
set_custom_style()
map_gdf = gpd.read_file('./choro.gpkg')
def get_fill_color(row):
    base_colors = {
        'Democrat': (0, 0, 255),    # Blue
        'Republican': (255, 0, 0)   # Red
    }

    r, g, b = base_colors.get(row['winner_party'], (128, 128, 128))
    intensity = row['winner_percentage'] / 100
    intensity = max(0.3, min(intensity, 1.0))
    
    r = int(r * intensity + (1 - intensity) * 255)
    g = int(g * intensity + (1 - intensity) * 255)
    b = int(b * intensity + (1 - intensity) * 255)

    return f"rgba({r},{g},{b},{intensity})"

map_gdf['fill_color'] = map_gdf.apply(get_fill_color, axis=1)

fig = go.Figure()

for _, row in map_gdf.iterrows():
    geom = row['geometry']
    if geom is None:
        continue

    if geom.geom_type == 'MultiPolygon':
        polygons = list(geom)
    else:
        polygons = [geom]

    for polygon in polygons:
        lons, lats = polygon.exterior.xy
        lons = list(lons)
        lats = list(lats)

        fig.add_trace(go.Scattermapbox(
            fill="toself",
            lon=lons,
            lat=lats,
            mode='none',
            fillcolor=row['fill_color'],
            line=dict(color='black', width=1),
            hoverinfo='text',
            text=(
                f"State: {row['state_name']}<br>"
                f"District: {row['district']}<br>"
                f"Party: {row['winner_party']}<br>"
                f"Votes: {row['winner_votes']}<br>"
                f"Percentage: {row['winner_percentage']}%"
            )
        ))

# Update layout to remove legend and adjust map settings
fig.update_layout(
    width=1000,
    height=800,
    mapbox_style="white-bg",
    mapbox_zoom=3,
    mapbox_center={"lat": 37.0902, "lon": -95.7129},
    margin={"r":0,"t":0,"l":0,"b":0},
    showlegend=False  # This removes the legend
)

# If you have a Mapbox token:
# fig.update_layout(mapbox_accesstoken="YOUR_MAPBOX_TOKEN")

st.title("Election Results Map")
st.plotly_chart(fig, use_container_width=True)
