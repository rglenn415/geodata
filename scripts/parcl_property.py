import os
from parcllabs import ParclLabsClient

API_KEY = os.getenv('PARCL_API_KEY')
client = ParclLabsClient(api_key=API_KEY,limit=10)

search_params = {
    'parcl_ids': [5374321],  # Required
    'property_type': 'SINGLE_FAMILY',  # Required
    #'current_entity_owner_name': None,  # Specify one of the options or None
    # 'square_footage_min': 4000,
    # 'square_footage_max': 5000,
    #'bedrooms_min': 2,
    #'bedrooms_max': 4,
    #'bathrooms_min': 2,
    #'bathrooms_max': 3,
    #'year_built_min': 1990,
    #'year_built_max': 2023,
    #'event_history_sale_flag': True,
    #'event_history_rental_flag': False,
    #'event_history_listing_flag': True,
    #'current_new_construction_flag': False,
    #'current_owner_occupied_flag': True,
    #'current_investor_owned_flag': False
}

search_results = client.property.search.retrieve(**search_params)

print(f"Found {len(search_results)} properties matching the criteria.")
search_results.to_csv('property.csv', index=False)