from marqo import Client
import os
from dotenv import load_dotenv
import config

load_dotenv()

api_key = os.getenv("MARQO_API_KEY")

mq = Client(url="https://api.marqo.ai", api_key=api_key)

index_name = config.INDEX_NAME

# Get documents by their ID
res = mq.index(config.INDEX_NAME).get_document(
    document_id="71246356_0",
)

print(res)

# Delete documents by their ID
mq.index(index_name).delete_documents(
    ids=[
        "71246356_0",
        ]
    )