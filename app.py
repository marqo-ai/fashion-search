import marqo
import requests
import io
import base64
from PIL import Image
import streamlit as st
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

index_name = "fashion-search"  # This must match the index name defined in the config.py file in marqo folder

# Initialize Marqo client
api_key = os.getenv("MARQO_API_KEY")  # To find your Marqo API key, visit https://www.marqo.ai/blog/finding-my-marqo-api-key
mq = marqo.Client("https://api.marqo.ai", api_key=api_key)

# Streamlit App
st.set_page_config(page_title="Fashion Search with Marqo", layout="wide")
st.title("Fashion Search with Marqo")

# Function to encode image in base64
def encode_image_to_base64(image):
    """Encodes a PIL image to a base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")

# Function to capitalize product titles
def capitalize_title(title):
    """Capitalizes each word in the product title."""
    words = title.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

# Function to filter out duplicate items based on the first part of the _id
def filter_unique_items(hits):
    """Filters out duplicate items by keeping only one image per item based on the _id prefix."""
    unique_items = {}
    filtered_hits = []

    for hit in hits:
        item_id = hit['_id'].split('_')[0]  # Get the first part of the _id before the underscore
        if item_id not in unique_items:
            unique_items[item_id] = True
            filtered_hits.append(hit)
        if len(filtered_hits) == 20:  # Stop when we have 20 unique items
            break

    return filtered_hits

# Helper function to create valid keys
def make_modifier_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", value).lower()

# Input box for query (search is triggered on Enter)
query = st.text_input("Search for items (e.g., green dress):", "")

# Radio button for selecting a single search method
search_method = st.radio(
    "Select a search method:",
    options=[
        "Basic Tensor Search",
        "Hybrid Search",
        "Hybrid Search with Exact Match Boosters",
        "Hybrid Search with Exact Match Boosters and Modifiers"
    ]
)

# Trigger search when query is entered and a search method is selected
if query and search_method:
    with st.spinner("Fetching results..."):
        query_key = make_modifier_key(query)
        res = None

        if search_method == "Basic Tensor Search":
            res = mq.index(index_name).search(
                query,
                limit=50,
                filter_string="in_stock:(true)"
            )
        elif search_method == "Hybrid Search":
            res = mq.index(index_name).search(
                query,
                search_method="HYBRID",
                limit=50,
                attributes_to_retrieve=[
                    "product_name",
                    "image_url",
                    "cost",
                ],
                hybrid_parameters={
                    "alpha": 0.5,
                    "rrfK": 60,
                    "searchableAttributesLexical": ["product_name"],
                },
                show_highlights=False,
                filter_string="in_stock:(true)",
            )
        elif search_method == "Hybrid Search with Exact Match Boosters":
            res = mq.index(index_name).search(
                query,
                search_method="HYBRID",
                limit=50,
                attributes_to_retrieve=[
                    "product_name",
                    "image_url",
                    "cost",
                ],
                hybrid_parameters={
                    "alpha": 0.5,
                    "rrfK": 60,
                    "scoreModifiersTensor": {
                        "add_to_score": [
                            {"field_name": f"exact_match_boosters.{query_key}", "weight": 1000}
                        ]
                    },
                    "scoreModifiersLexical": {
                        "add_to_score": [
                            {"field_name": f"exact_match_boosters.{query_key}", "weight": 1000}
                        ]
                    },
                    "searchableAttributesLexical": ["product_name"],
                },
                show_highlights=False,
                filter_string="in_stock:(true)",
            )

        elif search_method == "Hybrid Search with Exact Match Boosters and Modifiers":
            res = mq.index(index_name).search(
                query,
                search_method="HYBRID",
                limit=50,
                attributes_to_retrieve=["product_name", "image_url", "cost"],
                filter_string="in_stock:(true)",
                show_highlights=False,
                hybrid_parameters={
                    "alpha": 0.5,
                    "rrfK": 60,
                    "scoreModifiersTensor": {
                        "add_to_score": [
                            {"field_name": f"exact_match_boosters.{query_key}", "weight": 1000},
                            {"field_name": "one_day_revenue", "weight": 0.000002},
                            {"field_name": "three_day_revenue", "weight": 6.6e-7},
                            {"field_name": "five_day_revenue", "weight": 4e-7},
                            {"field_name": f"one_day_revenue_modifiers.{query_key}", "weight": 0.000005},
                            {"field_name": f"three_day_revenue_modifiers.{query_key}", "weight": 0.00000166666},
                            {"field_name": f"five_day_revenue_modifiers.{query_key}", "weight": 0.000001}
                        ]
                    },
                    "scoreModifiersLexical": {
                        "add_to_score": [
                            {"field_name": f"exact_match_boosters.{query_key}", "weight": 1000},
                            {"field_name": "one_day_revenue", "weight": 0.002},
                            {"field_name": "three_day_revenue", "weight": 0.0006},
                            {"field_name": "five_day_revenue", "weight": 0.0004},
                            {"field_name": f"one_day_revenue_modifiers.{query_key}", "weight": 1},
                            {"field_name": f"three_day_revenue_modifiers.{query_key}", "weight": 0.3333333333333333},
                            {"field_name": f"five_day_revenue_modifiers.{query_key}", "weight": 0.2}
                        ]
                    },
                    "searchableAttributesLexical": ["product_name"]
                }
            )

        # Display filtered results
        filtered_hits = filter_unique_items(res['hits'])

        st.subheader(f"Results from {search_method}")

        # CSS for consistent box size, alignment, and spacing
        st.markdown(
            """
            <style>
            .product-box {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: space-between;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                height: 400px;
                width: 100%;
                overflow: hidden;
                text-align: center;
                margin: 10px;
            }
            .product-box img {
                height: 200px;
                max-width: 100%;
                object-fit: contain;
                margin-bottom: 10px;
            }
            .product-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
                min-height: 40px;
            }
            .product-price {
                font-size: 18px;
                font-weight: bold;
                color: #E74C3C;
            }
            .stColumn > div {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Display results in rows of 5 using st.columns
        cols_per_row = 5
        cols = st.columns(cols_per_row)
        for i, hit in enumerate(filtered_hits):
            image_url = hit.get('image_url', None)
            product_name = hit.get('product_name', 'No Name')
            product_name = capitalize_title(product_name)
            price = hit.get('cost', 'N/A')

            if image_url:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                    img_base64 = encode_image_to_base64(image)

                    with cols[i % cols_per_row]:
                        st.markdown(
                            f"""
                            <div class="product-box">
                                <img src="data:image/png;base64,{img_base64}" alt="{product_name}" />
                                <div class="product-title">{product_name}</div>
                                <div class="product-price">£{price}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                except requests.RequestException:
                    with cols[i % cols_per_row]:
                        st.markdown(
                            f"""
                            <div class="product-box">
                                <div style="height: 200px; width: auto; border: 1px solid #ddd; border-radius: 5px; padding: 5px; display: flex; align-items: center; justify-content: center;">
                                    Failed to load image
                                </div>
                                <div class="product-title">{product_name}</div>
                                <div class="product-price">£{price}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
