from marqo import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("MARQO_API_KEY")

mq = Client(url="https://api.marqo.ai", api_key=api_key)

# For safety reasons, replace this with your index name here
index_name = "your-index-name"

# This will delete all documents in your index
def empty_index(input_index_name):
    index = mq.index(input_index_name)
    res =  index.search(q = '', limit=400)
    while len(res['hits']) > 0:
        id_set = []
        for hit in res['hits']:
            id_set.append(hit['_id'])
        index.delete_documents(id_set)
        res = index.search(q = '', limit=400)

empty_index(index_name)
