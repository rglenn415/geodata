import os
from dotenv import load_dotenv
from parcllabs import ParclLabsClient

load_dotenv()

parcl_api_key = os.getenv('PARCL_API_KEY')
print(parcl_api_key)
client = ParclLabsClient(parcl_api_key)

# get top 2 metros by population
markets = client.search.markets.retrieve(
        location_type='CBSA',
        sort_by='TOTAL_POPULATION',
        sort_order='DESC',
        limit=2
)
# top 2 metros based on population. We will use these markets to query other services in the remainder of this readme
top_market_parcl_ids = markets['parcl_id'].tolist()
print(top_market_parcl_ids)