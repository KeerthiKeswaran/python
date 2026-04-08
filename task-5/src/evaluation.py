import pandas as pd
import numpy as np
import joblib

def get_feature_importance(model, X):
    # Get feature names from the pipeline
    # This is slightly tricky with ColumnTransformer
    preprocessor = model.named_steps['preprocessor']
    
    # Numeric features
    num_features = preprocessor.transformers_[0][2]
    
    # Categorical features (after one-hot encoding)
    cat_transformer = preprocessor.transformers_[1][1]
    cat_features = list(cat_transformer.named_steps['onehot'].get_feature_names_out(preprocessor.transformers_[1][2]))
    
    feature_names = num_features + cat_features
    
    # Get importances from classifier
    classifier = model.named_steps['classifier']
    
    if hasattr(classifier, 'feature_importances_'):
        importances = classifier.feature_importances_
    elif hasattr(classifier, 'coef_'):
        importances = np.abs(classifier.coef_[0])
    else:
        return None
        
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    return importance_df

def save_model(model, path):
    joblib.dump(model, path)
    return path
