import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np

# Load dataset
file_path = "top_10_percent_units.csv"  # Update with your local file path
df = pd.read_csv(file_path)

# Extract longitude and latitude from 'the_geom'
df["longitude"] = df["the_geom"].str.extract(r'POINT \((-?\d+\.\d+) -?\d+\.\d+\)')[0].astype(float)
df["latitude"] = df["the_geom"].str.extract(r'POINT \(-?\d+\.\d+ (-?\d+\.\d+)\)')[0].astype(float)

# Remove rows with missing coordinates, price, or property area
df_filtered = df.dropna(subset=["latitude", "longitude", "total_assessed_value", "property_area"])

# Normalize 'total_assessed_value' and 'property_area' to balance their impact
df_filtered["value_score"] = np.log1p(df_filtered["total_assessed_value"]) * np.log1p(df_filtered["property_area"])

# Create a base map centered around San Francisco
sf_map = folium.Map(location=[37.7749, -122.4194], zoom_start=12)

# Add heatmap layer
heat_data = df_filtered[["latitude", "longitude", "value_score"]].values.tolist()
HeatMap(heat_data, radius=10, blur=15, max_zoom=1).add_to(sf_map)

# Save map
sf_map.save("sf_heatmap.html")
print("Heatmap saved as 'sf_heatmap.html'. Open it in a browser to view.")
