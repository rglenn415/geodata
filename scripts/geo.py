import geopandas as gpd
import pandas as pd
import os

def pull_data(import_file, output_name):
    # Load the file
    dir = os.getcwd()
    filename = os.path.join(dir, import_file)
    df = pd.read_csv(filename)

    # Filter for property_class_code that equals "SRES"
    sres_df = df[df['use_code'] == "SRES"]
    print(len(sres_df))
    # Ensure required columns exist
    required_cols = {'assessed_fixtures_value', 'assessed_improvement_value', 'assessed_land_value', 'lot_area'}
    missing_cols = required_cols - set(sres_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Calculate total assessed value (excluding personal property)
    sres_df['total_assessed_value'] = (
        sres_df['assessed_fixtures_value'] + 
        sres_df['assessed_improvement_value'] + 
        sres_df['assessed_land_value']
    )

    # Calculate lot price per square foot (avoid division by zero)
    sres_df['property_price_per_sqft'] = sres_df['total_assessed_value'] / sres_df['property_area']
    sres_df.loc[sres_df['property_area'] == 0, 'property_price_per_sqft'] = None  # Handle zero lot area

    # # Find top 5% of properties based on lot price per sq ft
    # top_5_percentile_value = sres_df['property_price_per_sqft'].quantile(0.95)
    # top_5_percent_units = sres_df[sres_df['property_price_per_sqft'] > top_5_percentile_value]

    # top 100 properties
    top_100_valuable_buildings = sres_df.sort_values(by='total_assessed_value', ascending=False).head(100)

    # Save results
    output_filename = os.path.join(dir, output_name)
    top_100_valuable_buildings.to_csv(output_filename, index=False)


def main():
    import_file = 'sf.csv'
    output_name = 'top_100_valuable_buildings.csv'
    pull_data(import_file, output_name)


if __name__ == "__main__":
    main()