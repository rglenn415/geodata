import os
from parcllabs import ParclLabsClient


API_KEY = os.getenv('PARCL_API_KEY')
client = ParclLabsClient(api_key=API_KEY)

# Search for markets matching 'San Francisco'
markets = client.search.markets.retrieve(query='San Francisco')

parcl_ids = markets.merge(markets[['parcl_id', 'name']], on='parcl_id')

parcl_ids.to_csv('parcl.csv', index=False)

