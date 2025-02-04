import geopandas as gpd
import pandas as pd
import os

# Load the file
dir = os.getcwd()
filename = os.path.join(dir,'sf.csv')
df = pd.read_csv(filename)
# print(df.head())
print(df.columns)