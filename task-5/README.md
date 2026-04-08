# Customer Sales Machine Learning Pipeline

## Objective
The objective of this project is to build an end-to-end Machine Learning pipeline that processes raw sales transaction data, performs feature engineering at the customer level, and trains multiple classification models to predict customer behavior (specifically, a synthetic churn prediction target based on recency).

## Solution Overview
The solution is built using a modular Python structure:
1.  **Data Ingestion & Cleaning**: Loads raw CSV data, handles numeric formatting (removing commas), and parses date fields.
2.  **Customer Aggregation**: Transforms transaction-row data into customer-level summaries (Total Spend, Transaction Frequency, Tenure, etc.).
3.  **Feature Engineering**: Creates derived features like `avg_monthly_spend`, `tenure_bin` (categorical), `activity_intensity`, and `spend_variability`.
4.  **Preprocessing Pipeline**: Leverages Scikit-Learn `Pipeline` and `ColumnTransformer` to automate:
    - **Imputation**: Handling missing values with median/constant strategies.
    - **Encoding**: Converting categorical features via One-Hot Encoding.
    - **Scaling**: Standardizing numeric features for sensitive models like SVM and Logistic Regression.
5.  **Model Comparison**: Evaluates 4 distinct algorithms using 5-fold Cross-Validation:
    - Logistic Regression
    - Random Forest
    - Support Vector Machine (SVM)
    - XGBoost
6.  **Hyperparameter Tuning**: Optimizes the XGBoost model using `GridSearchCV` to maximize the F1-score.
7.  **Model Serialization**: Saves the final trained pipeline to a `.pkl` file for future inference.

## Project Structure
```
task-5/
├── dataset/
│   └── raw_sales_transition_data.csv  # Raw transaction data
├── src/
│   ├── data_preprocessing.py          # Data cleaning and aggregation logic
│   ├── feature_engineering.py         # Logic for deriving new customer metrics
│   ├── model_training.py              # Pipeline construction and training loops
│   └── evaluation.py                  # Metrics extraction and model saving
├── models/
│   └── churn_prediction_model.pkl      # Saved final pipeline (binary)
├── main.py                            # Main orchestrator script
├── log.txt                            # Automated execution logs
└── README.md                          # Project documentation
```

## Features & Logging
- **Clean Execution**: Unwanted library warnings (e.g., XGBoost, Scikit-Learn deprecations) are automatically suppressed for a clean terminal experience.
- **Persistent Logging**: All execution results, including model benchmnarks and feature importances, are saved to `task-5/log.txt` for future reference.
- **Model Traceability**: Detailed hyperparameters and feature rankings are captured in every run.

## Requirements & Dependencies
The project requires Python 3.8+ and the following libraries:
- `pandas`: For data manipulation and aggregation.
- `numpy`: For numerical computations.
- `scikit-learn`: For the ML framework, pipelines, and evaluation.
- `xgboost`: For gradient boosting models.
- `tabulate`: For clean console output of comparison tables.
- `joblib`: For saving and loading the trained model.

## Setup & Usage
1.  **Install Dependencies**:
    ```bash
    pip install pandas numpy scikit-learn xgboost tabulate joblib
    ```
2.  **Run the Pipeline**:
    Execute the following command from the project root:
    ```bash
    python task-5/main.py
    ```

## Latest Execution Results
```text
=== Data Ingestion ===
Loaded 2,000 records (10 features)
Missing values filled: No missing values detected in critical numeric columns.
Engineered 14 new features (tenure_bin, avg_monthly_spend, trans_per_month...)

=== Model Comparison (5-Fold Cross-Validation) ===
+---------------------+------------+-------------+----------+----------+-----------+
| Model               |   Accuracy |   Precision |   Recall |       F1 |   ROC-AUC |
|---------------------+------------+-------------+----------+----------+-----------|
| Logistic Regression |   0.722957 |    0.538074 | 0.543112 | 0.537999 |  0.785449 |
| Random Forest       |   0.692153 |    0.493165 | 0.448554 | 0.464387 |  0.754043 |
| SVM                 |   0.699538 |    0.503182 | 0.560204 | 0.52071  |  0.757471 |
| XGBoost             |   0.67496  |    0.464333 | 0.477636 | 0.469103 |  0.748372 |
+---------------------+------------+-------------+----------+----------+-----------+

=== Best Model: Logistic Regression ===
Hyperparameters: {'classifier__learning_rate': 0.05, 'classifier__max_depth': 3, 'classifier__n_estimators': 200}

Top 5 Feature Importances:
1. tenure_days               — 0.337
2. activity_intensity        — 0.060
3. total_quantity            — 0.056
4. region_Taunggyi           — 0.042
5. avg_item_count            — 0.041

Model saved to task-5/models/churn_prediction_model.pkl
```

## Example Output
The pipeline produces a step-by-step log of the process:
- Record count and features loaded.
- Feature engineering status.
- A comparison table of all tested models with 5 metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
- Hyperparameters of the tuned best model.
- Top 5 feature importances for transparency.
- Path to the saved model file.
