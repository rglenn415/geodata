import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np
import os

import_file = "top_100_valuable_buildings.csv"
output_file_name = "sf_heatmap_100.html"

script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_data_path = os.path.join(script_dir, "..", "output_data")  # Moves up to geodata, then into datasets
output_data_path = os.path.abspath(output_data_path)  # Normalizes path
file_path = os.path.join(output_data_path, import_file)
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
output_file_name = os.path.join(output_data_path, output_file_name)
sf_map.save(output_file_name)
print(f"Heatmap saved as {output_file_name}. Open it in a browser to view.")
