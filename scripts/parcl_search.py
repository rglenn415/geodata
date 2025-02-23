import os
from parcllabs import ParclLabsClient

# Replace with your actual API key
API_KEY = os.getenv('PARCL_API_KEY')

# Initialize the client with your API key
client = ParclLabsClient(api_key=API_KEY)

# Search for markets matching 'San Francisco'
markets = client.search.markets.retrieve(query='San Francisco')

parcl_ids = markets.merge(markets[['parcl_id', 'name']], on='parcl_id')

parcl_ids.to_csv('parcl.csv', index=False)

