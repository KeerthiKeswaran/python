import pandas as pd
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb
import joblib

def create_pipeline(classifier):
    numeric_features = [
        'total_transactions', 'total_spend', 'avg_transaction_value', 
        'max_single_spend', 'total_quantity', 'avg_item_count', 
        'unique_categories', 'tenure_days', 'avg_monthly_spend', 
        'trans_per_month', 'avg_qty_per_trans', 'spend_per_category',
        'relative_spend', 'spend_variability', 'activity_intensity', 
        'relative_quantity'
    ]
    categorical_features = ['region', 'tenure_bin']

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', classifier)
    ])

def train_and_compare_models(X, y):
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(probability=True, kernel='rbf', random_state=42),
        'XGBoost': xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    }

    results = []
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

    for name, clf in models.items():
        pipeline = create_pipeline(clf)
        cv_results = cross_validate(pipeline, X, y, cv=5, scoring=scoring)
        
        results.append({
            'Model': name,
            'Accuracy': cv_results['test_accuracy'].mean(),
            'Precision': cv_results['test_precision'].mean(),
            'Recall': cv_results['test_recall'].mean(),
            'F1': cv_results['test_f1'].mean(),
            'ROC-AUC': cv_results['test_roc_auc'].mean()
        })

    return pd.DataFrame(results)

def tune_xgboost(X, y):
    param_grid = {
        'classifier__max_depth': [3, 6],
        'classifier__learning_rate': [0.05, 0.1],
        'classifier__n_estimators': [100, 200]
    }
    
    pipeline = create_pipeline(xgb.XGBClassifier(eval_metric='logloss', random_state=42))
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1', n_jobs=-1)
    grid_search.fit(X, y)
    
    return grid_search.best_estimator_, grid_search.best_params_
