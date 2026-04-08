import pandas as pd
import numpy as np

def engineer_features(df):
    # 1. Tenure Bins
    df['tenure_bin'] = pd.cut(df['tenure_days'], bins=[-1, 30, 90, 180, 1000], labels=['New', 'Short-term', 'Mid-term', 'Loyal'])
    
    # 2. Avg Monthly Spend (assume 30 days = 1 month)
    df['months_tenure'] = (df['tenure_days'] / 30).apply(lambda x: max(x, 1))
    df['avg_monthly_spend'] = df['total_spend'] / df['months_tenure']
    
    # 3. Transaction Frequency
    df['trans_per_month'] = df['total_transactions'] / df['months_tenure']
    
    # 4. Quantity per transaction
    df['avg_qty_per_trans'] = df['total_quantity'] / df['total_transactions']
    
    # 5. Spend Diversity
    df['spend_per_category'] = df['total_spend'] / df['unique_categories']
    
    # 6. High Value Factor (spend vs median)
    median_spend = df['total_spend'].median()
    df['relative_spend'] = df['total_spend'] / median_spend
    
    # 7. Variability in spend (normalized)
    df['spend_variability'] = df['spend_std'] / df['avg_transaction_value']
    df.fillna({'spend_variability': 0}, inplace=True)
    
    # 8. Activity intensity (transactions per day of tenure)
    df['activity_intensity'] = df['total_transactions'] / (df['tenure_days'] + 1)
    
    # 9. Basket size vs avg
    df['relative_quantity'] = df['total_quantity'] / df['total_quantity'].median()
    
    # Drop intermediate columns if needed, but we can leave them for the pipeline to handle
    # Let's ensure no NaN from division
    cols_to_fill = ['avg_monthly_spend', 'trans_per_month', 'avg_qty_per_trans']
    df[cols_to_fill] = df[cols_to_fill].fillna(0)
    
    return df
