"""
Generates portfolio-ready outputs for cover letter:
  - revenue_model.csv: tax revenue by percentile tier and rate
  - revenue_increase_vs_baseline.csv: additional revenue over current 1.17% rate
  - neighborhood_breakdown.csv: per-neighborhood value and revenue projections
  - heatmap_top_X_percent.html: geographic heatmap per percentile tier
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "datasets"))
OUTPUT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "output_data", "portfolio"))

IMPORT_FILE = "sf_assesor_data.csv"
BASELINE_RATE = 0.0117
TAX_RATES = [0.0117, 0.012, 0.013, 0.014, 0.015]
PERCENTILES = [5, 10, 15, 20]

USECOLS = [
    'use_code', 'assessed_fixtures_value', 'assessed_improvement_value',
    'assessed_land_value', 'property_area', 'number_of_bathrooms',
    'number_of_bedrooms', 'number_of_rooms', 'the_geom',
    'analysis_neighborhood', 'property_location'
]

DTYPE_MAP = {
    'assessed_fixtures_value': float,
    'assessed_improvement_value': float,
    'assessed_land_value': float,
    'property_area': float
}


def load_and_prepare():
    """Load assessor data, filter to valid SRES properties, compute values."""
    filepath = os.path.join(DATASETS_PATH, IMPORT_FILE)
    df = pd.read_csv(filepath, usecols=USECOLS, dtype=DTYPE_MAP)

    # Single-family residential only
    df = df[df['use_code'] == 'SRES']

    # Remove incomplete records (apt buildings without unit data)
    df = df[(df['number_of_bathrooms'] > 0) &
            (df['number_of_bedrooms'] > 0) &
            (df['number_of_rooms'] > 0)]

    df['total_assessed_value'] = (
        df['assessed_fixtures_value'] +
        df['assessed_improvement_value'] +
        df['assessed_land_value']
    )

    df['price_per_sqft'] = df['total_assessed_value'] / df['property_area']
    df['price_per_sqft'] = df['price_per_sqft'].replace([np.inf, -np.inf], np.nan)

    # Parse coordinates
    df['longitude'] = df['the_geom'].str.extract(r'POINT \((-?\d+\.\d+)')[0].astype(float)
    df['latitude'] = df['the_geom'].str.extract(r'POINT \(-?\d+\.\d+ (-?\d+\.\d+)')[0].astype(float)

    df = df.sort_values('total_assessed_value', ascending=False)
    return df


def fmt(val):
    """Format a number as currency string."""
    return f"${val:,.0f}"


def generate_revenue_model(df):
    """Revenue matrix: for each percentile tier, show revenue at each tax rate."""
    rows = []
    for p in PERCENTILES:
        n = int(len(df) * (p / 100))
        top = df.iloc[:n]
        total_val = top['total_assessed_value'].sum()
        row = {
            'tier': f'Top {p}%',
            'num_properties': f"{n:,}",
            'total_assessed_value': fmt(total_val),
        }
        for rate in TAX_RATES:
            label = f"revenue_at_{rate*100:.2f}%"
            row[label] = fmt(total_val * rate)
        rows.append(row)

    result = pd.DataFrame(rows)
    result.to_csv(os.path.join(OUTPUT_PATH, "revenue_model.csv"), index=False)
    print("Created: revenue_model.csv")
    return result


def generate_revenue_increase(df):
    """Show additional revenue over baseline 1.17% rate for each tier and rate."""
    rows = []
    for p in PERCENTILES:
        n = int(len(df) * (p / 100))
        top = df.iloc[:n]
        total_val = top['total_assessed_value'].sum()
        baseline_rev = total_val * BASELINE_RATE
        row = {
            'tier': f'Top {p}%',
            'num_properties': f"{n:,}",
            'baseline_revenue_at_1.17%': fmt(baseline_rev),
        }
        for rate in TAX_RATES:
            if rate == BASELINE_RATE:
                continue
            additional = (total_val * rate) - baseline_rev
            label = f"additional_at_{rate*100:.2f}%"
            row[label] = fmt(additional)
        rows.append(row)

    result = pd.DataFrame(rows)
    result.to_csv(os.path.join(OUTPUT_PATH, "revenue_increase_vs_baseline.csv"), index=False)
    print("Created: revenue_increase_vs_baseline.csv")
    return result


def generate_neighborhood_breakdown(df):
    """Per-neighborhood: count, total value, avg value, revenue at each rate."""
    # Use top 20% properties for neighborhood analysis
    n = int(len(df) * 0.20)
    top = df.iloc[:n].copy()

    grouped = top.groupby('analysis_neighborhood').agg(
        num_properties=('total_assessed_value', 'count'),
        total_assessed_value=('total_assessed_value', 'sum'),
        avg_assessed_value=('total_assessed_value', 'mean'),
        avg_price_per_sqft=('price_per_sqft', 'mean'),
    ).sort_values('total_assessed_value', ascending=False)

    for rate in TAX_RATES:
        label = f"revenue_at_{rate*100:.2f}%"
        grouped[label] = grouped['total_assessed_value'] * rate

    # Format for readability
    out = grouped.reset_index()
    out.rename(columns={'analysis_neighborhood': 'neighborhood'}, inplace=True)
    out['total_assessed_value'] = out['total_assessed_value'].apply(fmt)
    out['avg_assessed_value'] = out['avg_assessed_value'].apply(fmt)
    out['avg_price_per_sqft'] = out['avg_price_per_sqft'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    for rate in TAX_RATES:
        label = f"revenue_at_{rate*100:.2f}%"
        out[label] = out[label].apply(fmt)

    out.to_csv(os.path.join(OUTPUT_PATH, "neighborhood_breakdown.csv"), index=False)
    print("Created: neighborhood_breakdown.csv")
    return out


def generate_heatmaps(df):
    """One heatmap per percentile tier showing geographic spread of taxable properties."""
    for p in PERCENTILES:
        n = int(len(df) * (p / 100))
        top = df.iloc[:n].copy()
        top = top.dropna(subset=['latitude', 'longitude', 'total_assessed_value', 'property_area'])
        top['value_score'] = np.log1p(top['total_assessed_value']) * np.log1p(top['property_area'])

        sf_map = folium.Map(location=[37.7749, -122.4194], zoom_start=12, tiles="CartoDB positron")

        heat_data = top[['latitude', 'longitude', 'value_score']].values.tolist()
        HeatMap(heat_data, radius=10, blur=15, max_zoom=1).add_to(sf_map)

        filename = f"heatmap_top_{p}_percent.html"
        sf_map.save(os.path.join(OUTPUT_PATH, filename))
        print(f"Created: {filename}")


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    print("Loading data...")
    df = load_and_prepare()
    print(f"Loaded {len(df):,} valid SRES properties\n")

    print("--- Revenue Model ---")
    rev = generate_revenue_model(df)
    print(rev.to_string(index=False))
    print()

    print("--- Revenue Increase vs Baseline ---")
    inc = generate_revenue_increase(df)
    print(inc.to_string(index=False))
    print()

    print("--- Neighborhood Breakdown (Top 20%) ---")
    nb = generate_neighborhood_breakdown(df)
    print(nb.head(10).to_string(index=False))
    print()

    print("--- Generating Heatmaps ---")
    generate_heatmaps(df)

    print(f"\nAll outputs saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
