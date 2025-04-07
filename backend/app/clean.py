import pandas as pd

def remove_duplicates(input_file, output_file):
    # Read the CSV file
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Count original rows
    original_count = len(df)
    print(f"Original row count: {original_count}")
    
    # Remove duplicates
    df_deduplicated = df.drop_duplicates()
    
    # Count after deduplication
    deduplicated_count = len(df_deduplicated)
    print(f"Row count after deduplication: {deduplicated_count}")
    print(f"Removed {original_count - deduplicated_count} duplicate rows")
    
    # Save the deduplicated data
    df_deduplicated.to_csv(output_file, index=False)
    print(f"Deduplicated data saved to {output_file}")

# Define input and output file paths
input_file = "/Users/omprakashgunja/Documents/GitHub/lastbite-ai/backend/data/user_product_link_table_v2.csv"
output_file = "/Users/omprakashgunja/Documents/GitHub/lastbite-ai/backend/data/user_product_link_table_v2.csv"

# Run the deduplication
remove_duplicates(input_file, output_file)