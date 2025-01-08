from marqo import Client
from dotenv import load_dotenv
import os
import config

# Load environment variables from .env file
load_dotenv()

# Define API key 
api_key = os.getenv("MARQO_API_KEY")

# Set up Marqo client
mq = Client(url="https://api.marqo.ai", api_key=api_key)

# Define Marqo index name
index_name = config.INDEX_NAME

# Define the index settings
settings = {
    "treatUrlsAndPointersAsImages": True,  # Indicates that URLs or pointers in the data should be treated as image inputs
    "model": "Marqo/marqo-fashionSigLIP",  # Specifies the embedding model to be used for indexing and querying
    "normalizeEmbeddings": True,  # Enables normalization of embeddings for better similarity calculations
    "inferenceType": "marqo.GPU",  # Specifies GPU-based inference for faster computations
    "numberOfShards": 1,  # Sets the number of shards for the index (affects distributed storage)
    "numberOfReplicas": 0,  # Specifies the number of replicas for the index (data redundancy)
    "numberOfInferences": 1,  # Defines the maximum number of concurrent inferences
    "storageClass": "marqo.basic",  # Specifies the storage class for the index (basic is a standard option)
}

# Create the index
mq.create_index(index_name = index_name, settings_dict=settings)