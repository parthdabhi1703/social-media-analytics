import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def run_ml_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'datasets', 'cleaned_social_media_posts.csv')
    
    print("--- Phase 3: Machine Learning Engagement Predictor ---")
    df = pd.read_csv(dataset_path)
    
    # Feature & Target Selection
    features = ['platform', 'content_type', 'posting_hour', 'day_num', 'is_weekend', 'caption_length', 'hashtag_count', 'reach']
    target = 'total_engagement'
    
    X = df[features]
    y = df[target]
    
    categorical_cols = ['platform', 'content_type']
    numerical_cols = ['posting_hour', 'day_num', 'is_weekend', 'caption_length', 'hashtag_count', 'reach']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_cols),
            ('num', 'passthrough', numerical_cols)
        ]
    )
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    print(f"\nTraining dataset size: {len(X_train)} rows | Test dataset size: {len(X_test)} rows\n")
    print(f"{'Model Name':<30} | {'MAE':<10} | {'RMSE':<10} | {'R2 Score':<10}")
    print("-" * 70)
    
    for name, model in models.items():
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train)
        
        y_pred = pipeline.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {'MAE': mae, 'RMSE': rmse, 'R2': r2}
        print(f"{name:<30} | {mae:<10.2f} | {rmse:<10.2f} | {r2:<10.4f}")
        
    print("-" * 70)
    
    # Feature Importances from Random Forest
    rf_pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', models['Random Forest Regressor'])])
    rf_pipeline.fit(X_train, y_train)
    
    ohe_cols = list(rf_pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_cols))
    all_feature_names = ohe_cols + numerical_cols
    importances = rf_pipeline.named_steps['model'].feature_importances_
    
    fi_df = pd.DataFrame({'Feature': all_feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)
    
    print("\nTop Feature Importances (Random Forest):")
    for idx, row in fi_df.head(6).iterrows():
        print(f" - {row['Feature']:<25}: {row['Importance']*100:.2f}%")
        
    return results

if __name__ == '__main__':
    run_ml_pipeline()
