import re
import csv
import json
import time
from collections import defaultdict

# Helper function to create valid keys
def make_modifier_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", value).lower()

# Load historical data from a CSV file
def load_historical_data(csv_file):
    historical_data = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numeric fields to appropriate types
            row["total_purchases"] = int(row["total_purchases"])
            row["add_to_cart_count"] = int(row["add_to_cart_count"])
            row["total_click_count"] = int(row["total_click_count"])
            row["one_day_revenue"] = float(row["one_day_revenue"])
            row["three_day_revenue"] = float(row["three_day_revenue"])
            row["five_day_revenue"] = float(row["five_day_revenue"])
            historical_data.append(row)
    return historical_data

# Load product data from a CSV file
def load_product_data(csv_file):
    product_data = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numeric fields to appropriate types
            row["cost"] = float(row["cost"])
            row["in_stock"] = row["in_stock"].lower() == 'true'
            product_data.append(row)
    return product_data

# Update product data with exact match boosters and revenue modifiers
def update_product_data(product_data, historical_data):
    for product in product_data:
        product_name_key = make_modifier_key(product["product_name"])
        product["exact_match_boosters"] = {product_name_key: 1000}

        # Initialize revenue modifiers as nested dictionaries
        product["one_day_revenue_modifiers"] = defaultdict(float)
        product["three_day_revenue_modifiers"] = defaultdict(float)
        product["five_day_revenue_modifiers"] = defaultdict(float)

        for hist in historical_data:
            query_name_key = make_modifier_key(hist["query"])
            if hist["_id"] == product["_id"]:
                if hist["one_day_revenue"] > 0:
                    product["one_day_revenue_modifiers"][query_name_key] = hist["one_day_revenue"]
                if hist["three_day_revenue"] > 0:
                    product["three_day_revenue_modifiers"][query_name_key] = hist["three_day_revenue"]
                if hist["five_day_revenue"] > 0:
                    product["five_day_revenue_modifiers"][query_name_key] = hist["five_day_revenue"]

        # Convert defaultdicts to regular dictionaries
        product["one_day_revenue_modifiers"] = dict(product["one_day_revenue_modifiers"])
        product["three_day_revenue_modifiers"] = dict(product["three_day_revenue_modifiers"])
        product["five_day_revenue_modifiers"] = dict(product["five_day_revenue_modifiers"])

    return product_data

# Main script
if __name__ == "__main__":
    historical_data_file = "./data_processing/data/historical_data.csv"  # Path to historical data CSV file
    product_data_file = "./data_processing/data/product_data.csv"        # Path to product data CSV file
    output_file = "./data_processing/data/complete_data.json"            # Output JSON file

    start_time = time.time()  # Start timer

    # Load data
    print("Loading historical data...")
    historical_data = load_historical_data(historical_data_file)
    print(f"Loaded historical data in {time.time() - start_time:.2f} seconds.")

    print("Loading product data...")
    product_data = load_product_data(product_data_file)
    print(f"Loaded product data in {time.time() - start_time:.2f} seconds.")

    # Update product data
    print("Updating product data...")
    updated_product_data = update_product_data(product_data, historical_data)
    print(f"Updated product data in {time.time() - start_time:.2f} seconds.")

    # Save updated product data to JSON file
    print("Saving updated product data...")
    with open(output_file, "w") as file:
        json.dump(updated_product_data, file, indent=4)
    print(f"Saved updated product data to {output_file} in {time.time() - start_time:.2f} seconds.")

    total_time = time.time() - start_time  # End timer
    print(f"Total execution time: {total_time:.2f} seconds.")
