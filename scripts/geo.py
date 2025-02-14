import geopandas as gpd
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(import_file, usecols=None, dtype_map=None):
    """Loads CSV file into a Pandas DataFrame with optional column selection."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
    datasets_path = os.path.join(script_dir, "..", "datasets")  # Moves up to geodata, then into datasets
    datasets_path = os.path.abspath(datasets_path)  # Normalizes path
    filename = os.path.join(datasets_path, import_file)
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    return pd.read_csv(filename, usecols=usecols, dtype=dtype_map)

def filter_data(df, filter_column, filter_value):
    """Filters DataFrame by a specific column and value."""
    return df[df[filter_column] == filter_value]

def calculate_values(df):
    """Calculates total assessed value, price per square foot, and estimated property taxes."""
    
    df.loc[:, 'total_assessed_value'] = (
        df['assessed_fixtures_value'] + 
        df['assessed_improvement_value'] + 
        df['assessed_land_value']
    )
    
    # Calculate price per square foot and replace inf values with NaN
    df['property_price_per_sqft'] = df['total_assessed_value'] / df['property_area']
    df['property_price_per_sqft'] = df['property_price_per_sqft'].replace([float('inf'), -float('inf')], np.nan)
    
    # Calculate estimated property taxes
    df['estimated_property_tax_1.1714'] = df['total_assessed_value'] * 0.0117143563  # 1.17143563% as decimal
    df['estimated_property_tax_1.5'] = df['total_assessed_value'] * 0.015  # 1.5% as decimal
    
    return df

def get_top_properties(df, sort_column, top_n):
    """Gets the top N properties based on the sort column."""
    return df.sort_values(by=sort_column, ascending=False).head(top_n)

def find_top_5_percent(df):
    """Finds the top 5% of properties based on total assessed value."""
    
    # Calculate the 95th percentile value
    threshold = df['total_assessed_value'].quantile(0.95)
    
    # Filter for properties above the threshold
    top_5_percent_df = df[df['total_assessed_value'] > threshold]
    
    return top_5_percent_df

def get_top_properties(df, percent):
    threshold = df['total_assessed_value'].quantile(percent)
    
    # Filter for properties above the threshold
    top_percent_df = df[df['total_assessed_value'] > threshold]
    
    return top_percent_df


def save_data(df, output_name):
    """Saves DataFrame to CSV."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
    output_data_path = os.path.join(script_dir, "..", "output_data")  # Moves up to geodata, then into output_data
    output_data_path = os.path.abspath(output_data_path)
    
    if not os.path.exists(output_data_path):
        os.makedirs(output_data_path)  # Creates output directory if it doesn't exist
    
    print(f'created: {output_name}')
    output_filename = os.path.join(output_data_path, output_name)
    df.to_csv(output_filename, index=False)

def filter_invalid_properties(df):
    """Removes entries with 0 bathrooms, bedrooms, or rooms."""
    return df.loc[
        (df['number_of_bathrooms'] > 0) & 
        (df['number_of_bedrooms'] > 0) & 
        (df['number_of_rooms'] > 0)
    ]

def compare_property_tax_totals(df):
    """Calculates the total estimated property tax for both rates and finds the difference with formatted output."""
    
    total_tax_1_1714 = int(df['estimated_property_tax_1.1714'].sum())
    total_tax_1_5 = int(df['estimated_property_tax_1.5'].sum())
    tax_difference = int(total_tax_1_5 - total_tax_1_1714)
    
    return {
        "Total Tax (1.1714%)": f"{total_tax_1_1714:,}",
        "Total Tax (1.5%)": f"{total_tax_1_5:,}",
        "Difference": f"{tax_difference:,}"
    }



def pull_data(import_file, output_name, filter_column="use_code", filter_value="SRES", sort_column="total_assessed_value", top_n=100):
    """Main function to process data."""
    usecols = ['use_code', 'assessed_fixtures_value', 'assessed_improvement_value', 'assessed_land_value', 'property_area', 'number_of_bathrooms', 'property_location', 'number_of_bedrooms', 'number_of_rooms', 'the_geom']
    dtype_map = {'assessed_fixtures_value': float, 'assessed_improvement_value': float, 'assessed_land_value': float, 'property_area': float}

    # Load data
    df = load_data(import_file, usecols=usecols, dtype_map=dtype_map)
    
    # Filter data
    filtered_df = filter_data(df, filter_column, filter_value)
    
    # Calculate values
    calculated_df = calculate_values(filtered_df)

    #filter properties with 0 bed rooms aka whole apt buildings
    filtered_df = filter_invalid_properties(calculated_df)
    
    # Get top properties
    # top_properties = get_top_properties(filtered_df, sort_column, top_n)

    top_5_percent_properties = find_top_5_percent(filtered_df)

    # Save the results
    save_data(top_5_percent_properties, output_name)

    tax_summary = compare_property_tax_totals(top_5_percent_properties)
    print(tax_summary)

def create_graph(import_file, filter_column="use_code", filter_value="SRES"):
    # Read data
    usecols = [
        'use_code', 'assessed_fixtures_value', 'assessed_improvement_value', 
        'assessed_land_value', 'property_area', 'number_of_bathrooms', 
        'property_location', 'number_of_bedrooms', 'number_of_rooms', 'the_geom'
    ]
    dtype_map = {
        'assessed_fixtures_value': float, 'assessed_improvement_value': float, 
        'assessed_land_value': float, 'property_area': float
    }
    
    # Load and filter data
    df = load_data(import_file, usecols=usecols, dtype_map=dtype_map)
    df = filter_data(df, filter_column, filter_value)
    df = filter_invalid_properties(df)

    # Define tax rates (added 1.17%)
    tax_rates = np.array([0.0117, 0.012, 0.013, 0.014, 0.015])
    print(f'Tax rates: {tax_rates}')

    # Step 1: Calculate total assessed property value for each house
    df['total_assessed_value'] = (
        df['assessed_fixtures_value'] + df['assessed_improvement_value'] + df['assessed_land_value']
    )

    # Step 2: Sort houses by assessed value in descending order
    df = df.sort_values(by='total_assessed_value', ascending=False)

    # Step 3: Define percentiles to analyze (top X% of houses)
    percentiles = [5, 10, 15, 20]
    results = []

    for p in percentiles:
        # Select the top P% of houses
        num_houses = int(len(df) * (p / 100))
        top_houses = df.iloc[:num_houses]

        # Compute total taxable value for this percentile group
        total_value = top_houses['total_assessed_value'].sum()

        # Compute tax revenue for each tax rate
        revenues = {f'tax_{rate*100:.1f}%': total_value * rate for rate in tax_rates}

        # Store the result
        results.append({'percentile': p, 'num_houses': num_houses, 'total_value': total_value, **revenues})

    # Convert results into a DataFrame
    df_results = pd.DataFrame(results)

    print(df_results)  # Debugging output
    return df_results

def compute_tax_differences(df_results):
    """
    Computes the difference between tax revenue at 1.17% and other tax rates.
    Returns a DataFrame with differences and number of houses affected.
    """
    base_tax_col = 'tax_1.2%'  # Reference tax rate for comparison
    base_revenue = df_results[base_tax_col]

    # Compute the difference for all other tax rates
    diff_data = {
        'percentile': df_results['percentile'],
        'num_houses': df_results['num_houses'],  # Include number of houses
        **{col + '_diff': df_results[col] - base_revenue for col in df_results.columns if col.startswith('tax_') and col != base_tax_col}
    }

    df_differences = pd.DataFrame(diff_data)
    print(df_differences)  # Debug output
    return df_differences

def main():
    import_file = 'sf_assesor_data.csv'
    output_name = 'matrix.csv'
    # pull_data(import_file, output_name)
    df = create_graph(import_file)
    df_differences = compute_tax_differences(df)
    # save_data(df_differences, 'diff.csv')
    save_data(df, output_name)


    
if __name__ == "__main__":
    main()
