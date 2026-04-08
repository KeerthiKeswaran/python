import os
import sys
import pandas as pd
from tabulate import tabulate
import warnings

# Suppress unwanted library logs and warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # For any tensorflow usage
os.environ['PYTHONWARNINGS'] = 'ignore'

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_preprocessing import load_and_clean_data, aggregate_customer_data
from feature_engineering import engineer_features
from model_training import train_and_compare_models, tune_xgboost
from evaluation import get_feature_importance, save_model

class Logger(object):
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

def run_pipeline():
    # Setup logging to file
    log_file = os.path.join(os.path.dirname(__file__), "log.txt")
    sys.stdout = Logger(log_file)
    
    dataset_path = 'task-5/dataset/raw_sales_transition_data.csv'
    if not os.path.exists(dataset_path):
        # Handle relative path if run from within task-5
        dataset_path = 'dataset/raw_sales_transition_data.csv'

    # 1. Data Ingestion
    print("=== Data Ingestion ===")
    raw_df = load_and_clean_data(dataset_path)
    
    # Calculate missing values before filling
    missing_ppu_pct = raw_df['PPU'].isnull().mean() * 100
    missing_amount_pct = raw_df['Amount'].isnull().mean() * 100
    
    # Process and aggregate
    cust_df = aggregate_customer_data(raw_df)
    
    print(f"Loaded {len(raw_df):,} records ({raw_df.shape[1]} features)")
    if missing_ppu_pct > 0 or missing_amount_pct > 0:
        print(f"Missing values filled: PPU ({missing_ppu_pct:.1f}%), Amount ({missing_amount_pct:.1f}%)")
    else:
        print("Missing values filled: No missing values detected in critical numeric columns.")

    # 2. Feature Engineering
    cust_df = engineer_features(cust_df)
    new_features_count = cust_df.shape[1] - 11 # Subtracting original aggregated columns
    print(f"Engineered {new_features_count} new features (tenure_bin, avg_monthly_spend, trans_per_month...)")

    # 3. Model Training and Comparison
    X = cust_df.drop(columns=['Customer ID', 'target', 'first_purchase', 'last_purchase'])
    y = cust_df['target']

    print("\n=== Model Comparison (5-Fold Cross-Validation) ===")
    comparison_df = train_and_compare_models(X, y)
    print(tabulate(comparison_df, headers='keys', tablefmt='psql', showindex=False))

    # 4. Best Model Selection and Tuning
    best_model_name = comparison_df.loc[comparison_df['F1'].idxmax(), 'Model']
    print(f"\n=== Best Model: {best_model_name} ===")
    
    # Tune XGBoost as it's typically the best (per sample format)
    tuned_model, best_params = tune_xgboost(X, y)
    print(f"Hyperparameters: {best_params}")

    # 5. Feature Importance
    importance_df = get_feature_importance(tuned_model, X)
    print("\nTop 5 Feature Importances:")
    for i, (idx, row) in enumerate(importance_df.head(5).iterrows(), 1):
        print(f"{i}. {row['Feature']:<25} — {row['Importance']:.3f}")

    # 6. Save Model
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_path = os.path.join(model_dir, 'churn_prediction_model.pkl')
    save_model(tuned_model, model_path)
    print(f"\nModel saved to {model_path}")
    print(f"Detailed results logged to {log_file}")

if __name__ == "__main__":
    run_pipeline()
