from marqo import Client
from dotenv import load_dotenv
import os
import config
import re

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("MARQO_API_KEY")

mq = Client(url="https://api.marqo.ai", api_key=api_key)

# Define Marqo index name
index_name = config.INDEX_NAME

query = "green candy dress"

# Helper function to create valid keys
def make_modifier_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", value).lower()

def basic_search(query):
    basic_search = mq.index(config.INDEX_NAME).search(
                    query,
                    limit=50,
                    filter_string="in_stock:(true)"
                )

    return basic_search

def hybrid_search(query):
    hybrid_search = mq.index(config.INDEX_NAME).search(
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

    return hybrid_search


def hybrid_search_with_exact_boosters(query):

    query_key = make_modifier_key(query)

    hybrid_search_with_exact_boosters = mq.index(config.INDEX_NAME).search(
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

    return hybrid_search_with_exact_boosters


def hybrid_with_exact_boosters_and_modifiers(query):

    query_key = make_modifier_key(query)

    hybrid_with_exact_boosters_and_modifiers = mq.index(config.INDEX_NAME).search(
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

    return hybrid_with_exact_boosters_and_modifiers

print(basic_search(query)['hits'][0])
print(hybrid_search(query)['hits'][0])
print(hybrid_search_with_exact_boosters(query)['hits'][0])
print(hybrid_with_exact_boosters_and_modifiers(query)['hits'][0])



