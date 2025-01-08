import pandas as pd

def merge_data(historical_data_path, product_data_path, output_path):
    # Load historical data and product data
    historical_data = pd.read_csv(historical_data_path)
    product_data = pd.read_csv(product_data_path)

    # Merge the two datasets on the '_id' column
    merged_data = pd.merge(historical_data, product_data, on='_id', how='left')

    # Save the merged dataset to a new CSV file
    merged_data.to_csv(output_path, index=False)

    print(f"Merged data has been saved to {output_path}")

# Paths to input and output files
historical_data_path = 'data_processing/data/historical_data.csv'
product_data_path = 'data_processing/data/product_data.csv'
output_path = 'data_processing/data/merged_data.csv'

# Call the function to merge data and save it to a new file
merge_data(historical_data_path, product_data_path, output_path)
