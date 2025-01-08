from marqo import Client
from dotenv import load_dotenv
import os
import config

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("MARQO_API_KEY")

mq = Client(url="https://api.marqo.ai", api_key=api_key)

# Define Marqo index name
index_name = config.INDEX_NAME

# Delete the index
mq.delete_index(index_name)