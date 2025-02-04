import geopandas as gpd
import pandas as pd
import os

# Load the file
dir = os.getcwd()
filename = os.path.join(dir, 'sf.csv')
df = pd.read_csv(filename)

# print(df.head())
# Filter for property_class_code that equals "SRES"
sres_df = df[df['use_code'] == "SRES"]

# Calculate the total assessed value by adding all relevant columns
sres_df['total_assessed_value'] = sres_df['assessed_fixtures_value'] + \
                                  sres_df['assessed_improvement_value'] + \
                                  sres_df['assessed_land_value']

# Find units in the top 10% of total assessed value
top_10_percentile_value = sres_df['total_assessed_value'].quantile(0.90)
top_10_percent_units = sres_df[sres_df['total_assessed_value'] > top_10_percentile_value]

print(f"\nUnits in the top 10% of total assessed value: {len(top_10_percent_units)}")
if len(top_10_percent_units) > 0:
    print(top_10_percent_units.head())

output_filename = os.path.join(dir, 'top_10_percent_units.csv')
top_10_percent_units.to_csv(output_filename, index=False)