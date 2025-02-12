import geopandas as gpd
import pandas as pd
import os

def pull_data(import_file, output_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
    datasets_path = os.path.join(script_dir, "..", "datasets")  # Moves up to geodata, then into datasets
    datasets_path = os.path.abspath(datasets_path)  # Normalizes path
    filename = os.path.join(datasets_path, import_file)
    df = pd.read_csv(filename)

    print(datasets_path)  # Always resolves to C:\Users\skate\PirateLab\geodata\datasets

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

    output_data_path = os.path.join(script_dir, "..", "output_data")  # Moves up to geodata, then into datasets
    output_data_path = os.path.abspath(datasets_path) 
    # Save results
    output_filename = os.path.join(output_data_path, output_name)
    top_100_valuable_buildings.to_csv(output_filename, index=False)


def main():
    import_file = 'sf_assesor_data.csv'
    output_name = 'top_100_valuable_buildings.csv'
    pull_data(import_file, output_name)


if __name__ == "__main__":
    main()