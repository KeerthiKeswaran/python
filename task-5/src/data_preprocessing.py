import pandas as pd
import numpy as np

def load_and_clean_data(file_path):
    # Load dataset
    df = pd.read_csv(file_path)
    
    # Cleaning Numeric Columns (PPU and Amount have commas)
    for col in ['PPU', 'Amount']:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
            
    # Cleaning Date Column
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    
    return df

def aggregate_customer_data(df):
    # Sort by date
    df = df.sort_values(by=['Customer ID', 'Date'])
    
    # Reference date for "recency" (assuming the last date in dataset is "today")
    ref_date = df['Date'].max()
    
    # Aggregations
    cust_df = df.groupby('Customer ID').agg({
        'Date': ['min', 'max', 'count'],
        'Amount': ['sum', 'mean', 'std', 'max'],
        'Quantity': ['sum', 'mean'],
        'Product Category': 'nunique',
        'Region': 'first'
    })
    
    # Flatten columns
    cust_df.columns = [
        'first_purchase', 'last_purchase', 'total_transactions',
        'total_spend', 'avg_transaction_value', 'spend_std', 'max_single_spend',
        'total_quantity', 'avg_item_count',
        'unique_categories', 'region'
    ]
    
    # Calculate Tenure and Recency
    cust_df['tenure_days'] = (cust_df['last_purchase'] - cust_df['first_purchase']).dt.days
    cust_df['recency_days'] = (ref_date - cust_df['last_purchase']).dt.days
    
    # Target Variable: Churn (Synthetically defined)
    # Let's say if a customer hasn't purchased in the last 60 days, they are "churned"
    # Given the dataset timeframe, we'll adjust the threshold
    threshold = cust_df['recency_days'].quantile(0.7) # top 30% most inactive are "churned"
    cust_df['target'] = (cust_df['recency_days'] > threshold).astype(int)
    
    return cust_df.reset_index()
