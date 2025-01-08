import pandas as pd

def generate_historical_data(search_log_path, product_data_path, output_path):
    # Load the search log and product data
    search_log_df = pd.read_csv(search_log_path)
    product_data_df = pd.read_csv(product_data_path)
    
    # Extract product cost for each product ID
    product_costs = product_data_df.set_index('_id')['cost'].to_dict()
    
    # Initialize a dictionary to store aggregated data
    aggregated_data = {}

    # Group by query and _id to aggregate interaction metrics
    for (query, _id), group in search_log_df.groupby(['query', '_id']):
        # Count total occurrences of each action
        total_purchases = group[group['action'] == 'purchased'].shape[0]
        add_to_cart_count = group[group['action'] == 'add_to_cart'].shape[0]
        total_click_count = group[group['action'] == 'click'].shape[0]

        # Calculate revenue for one day, three days, and five days
        one_day_purchases = group[(group['action'] == 'purchased') & (group['days_ago_action_performed'] <= 1)].shape[0]
        three_day_purchases = group[(group['action'] == 'purchased') & (group['days_ago_action_performed'] <= 3)].shape[0]
        five_day_purchases = group[(group['action'] == 'purchased') & (group['days_ago_action_performed'] <= 5)].shape[0]

        # Get the product cost for the current _id
        cost = product_costs.get(_id, 0)

        # Compute revenue based on product cost
        one_day_revenue = round(one_day_purchases * cost, 2)
        three_day_revenue = round(three_day_purchases * cost, 2)
        five_day_revenue = round(five_day_purchases * cost, 2)

        # Store the aggregated data
        aggregated_data[(query, _id)] = {
            "total_purchases": total_purchases,
            "add_to_cart_count": add_to_cart_count,
            "total_click_count": total_click_count,
            "one_day_revenue": one_day_revenue,
            "three_day_revenue": three_day_revenue,
            "five_day_revenue": five_day_revenue
        }

    # Convert aggregated data to a DataFrame
    historical_data_df = pd.DataFrame.from_dict(aggregated_data, orient='index').reset_index()
    historical_data_df.columns = ['query', '_id', 'total_purchases', 'add_to_cart_count', 'total_click_count', 'one_day_revenue', 'three_day_revenue', 'five_day_revenue']

    # Save to CSV
    historical_data_df.to_csv(output_path, index=False)

    print(f"Historical data has been generated and saved to {output_path}")

# Paths to input and output files
search_log_path = 'data_processing/data/search_log.csv'
product_data_path = 'data_processing/data/product_data.csv'
output_path = 'data_processing/data/historical_data.csv'

# Generate the historical data
generate_historical_data(search_log_path, product_data_path, output_path)
