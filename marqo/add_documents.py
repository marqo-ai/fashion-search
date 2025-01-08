import json
import time
from marqo import Client
from dotenv import load_dotenv
import os
import config

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("MARQO_API_KEY")

# Initialize Marqo client
mq = Client(url="https://api.marqo.ai", api_key=api_key)

# Get the index name
index_name = config.INDEX_NAME

# Load documents from JSON file
json_file_path = "./data_processing/data/complete_data.json"
with open(json_file_path, 'r') as file:
    documents = json.load(file)

# Print the first document (for verification)
print(documents[0])

# Define batch size
batch_size = 64  # Define the batch size for uploading documents

# Start timing
start_time = time.time()

# Add documents to Marqo index
res = mq.index(index_name).add_documents(
    documents,  # List of documents to be indexed
    client_batch_size=batch_size,  # Number of documents to process and upload in each batch
    mappings={  # Custom field mapping for multimodal combination
        "image_title_multimodal": {  # Field name to be created
            "type": "multimodal_combination",  # Specifies that the field is a combination of text and image
            "weights": {  # Weights assigned to each component in the combination
                "product_name": 0.1,  # Low weight given to product name (text)
                "image_url": 0.9,  # High weight given to image URL (visual content)
            },
        }
    },
    tensor_fields=["image_title_multimodal"],  # Specifies that this field should be processed as tensors
    use_existing_tensors=True,  # Reuse existing tensors if they already exist for these documents
)

# End timing
end_time = time.time()

# Print the response from Marqo
# print(res)

# Print elapsed time
print(f"Time taken to add documents: {end_time - start_time:.2f} seconds")
