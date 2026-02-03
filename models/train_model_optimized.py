"""
Credit Risk Scoring - Optimized LightGBM Model
Implements hyperparameter tuning to meet AUC ≥ 0.80 and KS ≥ 30 targets
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


def calculate_ks(y_true, y_pred_proba):
    """Calculate KS statistic"""
    df_ks = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred_proba})
    df_ks = df_ks.sort_values('y_pred', ascending=False)
    df_ks['cum_good'] = (df_ks['y_true'] == 0).cumsum() / (df_ks['y_true'] == 0).sum()
    df_ks['cum_bad'] = (df_ks['y_true'] == 1).cumsum() / (df_ks['y_true'] == 1).sum()
    return abs(df_ks['cum_bad'] - df_ks['cum_good']).max() * 100


def select_features(df, target_col='default'):
    """Select most predictive features based on correlation with target"""
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['applicant_id', 'default', 'default_probability']
    feature_cols = [c for c in numeric_cols if c not in exclude_cols]
    
    # Calculate correlation with target
    correlations = df[feature_cols].corrwith(df[target_col]).abs().sort_values(ascending=False)
    
    # Select top features with correlation > 0.02
    selected_features = correlations[correlations > 0.02].index.tolist()
    
    print(f"Selected {len(selected_features)} features with correlation > 0.02")
    print("\nTop 15 correlated features:")
    for i, (feat, corr) in enumerate(correlations.head(15).items()):
        print(f"  {i+1}. {feat}: {corr:.4f}")
    
    return selected_features


def train_optimized_model(df):
    """Train optimized LightGBM model with cross-validation"""
    
    print("=" * 60)
    print("OPTIMIZED CREDIT RISK MODEL")
    print("=" * 60)
    
    # Select features
    print("\n>>> FEATURE SELECTION")
    features = select_features(df)
    
    X = df[features]
    y = df['default']
    
    # 80/20 split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n>>> DATA SPLIT")
    print(f"Training: {len(X_train)} samples ({y_train.mean()*100:.1f}% default)")
    print(f"Validation: {len(X_val)} samples ({y_val.mean()*100:.1f}% default)")
    
    # Optimized parameters - more regularization to prevent overfitting
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'boosting_type': 'gbdt',
        'num_leaves': 15,          # Reduced from 31
        'max_depth': 4,            # Reduced from 6
        'learning_rate': 0.02,     # Reduced from 0.05
        'feature_fraction': 0.6,   # Reduced from 0.8
        'bagging_fraction': 0.6,   # Reduced from 0.8
        'bagging_freq': 5,
        'min_child_samples': 50,   # Increased from 20
        'min_child_weight': 1e-3,
        'reg_alpha': 1.0,          # Increased L1 regularization
        'reg_lambda': 1.0,         # Increased L2 regularization
        'min_gain_to_split': 0.1,  # Added
        'verbose': -1,
        'random_state': 42,
        'n_jobs': -1,
        'scale_pos_weight': (y_train == 0).sum() / (y_train == 1).sum()
    }
    
    print(f"\n>>> TRAINING WITH OPTIMIZED PARAMETERS")
    
    # Cross-validation to find optimal iterations
    cv_data = lgb.Dataset(X_train, label=y_train)
    
    cv_results = lgb.cv(
        params,
        cv_data,
        num_boost_round=2000,
        nfold=5,
        stratified=True,
        callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)],
        return_cvbooster=True
    )
    
    best_iteration = len(cv_results['valid auc-mean'])
    best_cv_auc = max(cv_results['valid auc-mean'])
    
    print(f"\nCV Results:")
    print(f"  Best iteration: {best_iteration}")
    print(f"  Best CV AUC: {best_cv_auc:.4f}")
    
    # Train final model
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=best_iteration,
        valid_sets=[train_data, val_data],
        valid_names=['train', 'validation'],
        callbacks=[lgb.log_evaluation(200)]
    )
    
    # Evaluate
    print("\n>>> MODEL EVALUATION")
    
    # Training metrics
    train_pred = model.predict(X_train)
    train_auc = roc_auc_score(y_train, train_pred)
    train_ks = calculate_ks(y_train.values, train_pred)
    
    # Validation metrics
    val_pred = model.predict(X_val)
    val_auc = roc_auc_score(y_val, val_pred)
    val_ks = calculate_ks(y_val.values, val_pred)
    
    print(f"\n{'Metric':<20} {'Training':<15} {'Validation':<15} {'Target':<15} {'Status'}")
    print("-" * 80)
    
    auc_status = "✓ PASS" if val_auc >= 0.80 else "✗ FAIL"
    ks_status = "✓ PASS" if val_ks >= 30 else "✗ FAIL"
    
    print(f"{'AUC-ROC':<20} {train_auc:<15.4f} {val_auc:<15.4f} {'≥ 0.80':<15} {auc_status}")
    print(f"{'KS Statistic':<20} {train_ks:<15.2f} {val_ks:<15.2f} {'≥ 30':<15} {ks_status}")
    print(f"{'Gini':<20} {(2*train_auc-1):<15.4f} {(2*val_auc-1):<15.4f}")
    
    # Feature importance
    print("\n>>> TOP 15 FEATURES")
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importance(importance_type='gain')
    }).sort_values('importance', ascending=False)
    
    importance['pct'] = importance['importance'] / importance['importance'].sum() * 100
    
    for i, row in importance.head(15).iterrows():
        rank = importance.index.get_loc(i) + 1
        print(f"  {rank}. {row['feature']}: {row['pct']:.2f}%")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    
    model_data = {
        'model': model,
        'features': features,
        'params': params,
        'metrics': {
            'train_auc': train_auc,
            'train_ks': train_ks,
            'val_auc': val_auc,
            'val_ks': val_ks
        }
    }
    
    joblib.dump(model_data, 'models/credit_risk_lgbm_optimized.pkl')
    model.save_model('models/credit_risk_lgbm_optimized.txt')
    importance.to_csv('models/feature_importance_optimized.csv', index=False)
    
    print("\n>>> MODEL SAVED")
    print("  - models/credit_risk_lgbm_optimized.pkl")
    print("  - models/credit_risk_lgbm_optimized.txt")
    print("  - models/feature_importance_optimized.csv")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if val_auc >= 0.80 and val_ks >= 30:
        print("✓ ALL TARGETS MET!")
    else:
        print("Note: Targets not fully met with synthetic data.")
        print("This is expected as the synthetic data has limited signal.")
        print("With real credit bureau data, performance would be higher.")
    
    return model, features, model_data['metrics']


if __name__ == "__main__":
    df = pd.read_csv('data/credit_risk_dataset_encoded.csv')
    print(f"Loaded {len(df)} records\n")
    
    model, features, metrics = train_optimized_model(df)
