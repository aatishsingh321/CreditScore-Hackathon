"""
Credit Risk Scoring - LightGBM Model Development
Implements:
- LightGBM model for credit risk prediction
- 80/20 train/validation split
- Model evaluation metrics (AUC-ROC, KS statistic)
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, roc_curve, classification_report,
    confusion_matrix, precision_recall_curve, average_precision_score
)
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class CreditRiskModel:
    """LightGBM-based Credit Risk Prediction Model"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.target_column = 'default'
        self.train_metrics = {}
        self.val_metrics = {}
        
    def prepare_features(self, df):
        """
        Prepare feature matrix by selecting appropriate columns
        Excludes ID columns, date columns, target, and string columns
        """
        # Columns to exclude
        exclude_cols = [
            'applicant_id', 'application_date', 
            'default', 'default_probability'
        ]
        
        # Get all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter out excluded columns
        feature_cols = [c for c in numeric_cols if c not in exclude_cols]
        
        self.feature_columns = feature_cols
        
        print(f"Selected {len(feature_cols)} features for modeling")
        
        return feature_cols
    
    def split_data(self, df, test_size=0.2, random_state=42):
        """
        Split data into train and validation sets (80/20 split)
        Uses stratified sampling to maintain target distribution
        """
        print("\n" + "=" * 60)
        print("DATA SPLIT CONFIGURATION")
        print("=" * 60)
        
        if self.feature_columns is None:
            self.prepare_features(df)
        
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        # Stratified split to maintain class distribution
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        print(f"\nSplit ratio: {int((1-test_size)*100)}/{int(test_size*100)} (train/validation)")
        print(f"\nTraining set:")
        print(f"  - Samples: {len(X_train)}")
        print(f"  - Default rate: {y_train.mean()*100:.2f}%")
        print(f"  - Non-default: {(y_train==0).sum()}, Default: {(y_train==1).sum()}")
        
        print(f"\nValidation set:")
        print(f"  - Samples: {len(X_val)}")
        print(f"  - Default rate: {y_val.mean()*100:.2f}%")
        print(f"  - Non-default: {(y_val==0).sum()}, Default: {(y_val==1).sum()}")
        
        return X_train, X_val, y_train, y_val
    
    def train(self, X_train, y_train, X_val, y_val, params=None):
        """
        Train LightGBM model with early stopping
        """
        print("\n" + "=" * 60)
        print("LIGHTGBM MODEL TRAINING")
        print("=" * 60)
        
        # Default parameters optimized for credit risk
        if params is None:
            params = {
                'objective': 'binary',
                'metric': 'auc',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'max_depth': 6,
                'learning_rate': 0.05,
                'feature_fraction': 0.8,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'min_child_samples': 20,
                'reg_alpha': 0.1,
                'reg_lambda': 0.1,
                'verbose': -1,
                'random_state': 42,
                'n_jobs': -1,
                # Handle class imbalance
                'is_unbalance': True
            }
        
        print("\nModel Parameters:")
        for key, value in params.items():
            print(f"  - {key}: {value}")
        
        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # Train with early stopping
        print("\nTraining model...")
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=1000,
            valid_sets=[train_data, val_data],
            valid_names=['train', 'validation'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=100)
            ]
        )
        
        print(f"\nTraining complete!")
        print(f"Best iteration: {self.model.best_iteration}")
        print(f"Best validation AUC: {self.model.best_score['validation']['auc']:.4f}")
        
        return self.model
    
    def calculate_ks_statistic(self, y_true, y_pred_proba):
        """
        Calculate KS (Kolmogorov-Smirnov) statistic
        KS = max|cumulative_good_rate - cumulative_bad_rate|
        """
        # Sort by predicted probability
        df_ks = pd.DataFrame({
            'y_true': y_true,
            'y_pred': y_pred_proba
        }).sort_values('y_pred', ascending=False)
        
        # Calculate cumulative distributions
        df_ks['cum_good'] = (df_ks['y_true'] == 0).cumsum() / (df_ks['y_true'] == 0).sum()
        df_ks['cum_bad'] = (df_ks['y_true'] == 1).cumsum() / (df_ks['y_true'] == 1).sum()
        
        # KS statistic
        df_ks['ks'] = abs(df_ks['cum_bad'] - df_ks['cum_good'])
        ks_statistic = df_ks['ks'].max() * 100  # Convert to percentage
        
        # Find the threshold at max KS
        ks_threshold = df_ks.loc[df_ks['ks'].idxmax(), 'y_pred']
        
        return ks_statistic, ks_threshold
    
    def evaluate(self, X, y, dataset_name='Validation'):
        """
        Comprehensive model evaluation
        """
        print(f"\n" + "-" * 60)
        print(f"{dataset_name.upper()} SET EVALUATION")
        print("-" * 60)
        
        # Get predictions
        y_pred_proba = self.model.predict(X)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        auc_roc = roc_auc_score(y, y_pred_proba)
        ks_stat, ks_threshold = self.calculate_ks_statistic(y.values, y_pred_proba)
        avg_precision = average_precision_score(y, y_pred_proba)
        
        # Gini coefficient
        gini = 2 * auc_roc - 1
        
        metrics = {
            'auc_roc': auc_roc,
            'ks_statistic': ks_stat,
            'ks_threshold': ks_threshold,
            'gini': gini,
            'avg_precision': avg_precision
        }
        
        print(f"\n{'Metric':<25} {'Value':<15} {'Target':<15} {'Status'}")
        print("-" * 70)
        
        # AUC-ROC
        auc_status = "✓ PASS" if auc_roc >= 0.80 else "✗ FAIL"
        print(f"{'AUC-ROC':<25} {auc_roc:<15.4f} {'≥ 0.80':<15} {auc_status}")
        
        # KS Statistic
        ks_status = "✓ PASS" if ks_stat >= 30 else "✗ FAIL"
        print(f"{'KS Statistic':<25} {ks_stat:<15.2f} {'≥ 30':<15} {ks_status}")
        
        # Other metrics
        print(f"{'Gini Coefficient':<25} {gini:<15.4f}")
        print(f"{'Average Precision':<25} {avg_precision:<15.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"                 Predicted")
        print(f"                 No Default  Default")
        print(f"  Actual No Default    {cm[0,0]:<8}  {cm[0,1]:<8}")
        print(f"  Actual Default       {cm[1,0]:<8}  {cm[1,1]:<8}")
        
        # Classification Report
        print(f"\nClassification Report:")
        print(classification_report(y, y_pred, target_names=['No Default', 'Default']))
        
        return metrics, y_pred_proba
    
    def get_feature_importance(self, importance_type='gain', top_n=20):
        """
        Get feature importance from trained model
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")
        
        importance = self.model.feature_importance(importance_type=importance_type)
        feature_imp = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        # Normalize to percentage
        feature_imp['importance_pct'] = (
            feature_imp['importance'] / feature_imp['importance'].sum() * 100
        )
        
        return feature_imp.head(top_n)
    
    def save_model(self, path='models/credit_risk_lgbm.pkl'):
        """Save trained model and metadata"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics
        }
        
        joblib.dump(model_data, path)
        print(f"\nModel saved to: {path}")
        
        # Also save as native LightGBM format
        lgb_path = path.replace('.pkl', '.txt')
        self.model.save_model(lgb_path)
        print(f"LightGBM model saved to: {lgb_path}")
        
        return path
    
    def load_model(self, path='models/credit_risk_lgbm.pkl'):
        """Load trained model and metadata"""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        self.train_metrics = model_data['train_metrics']
        self.val_metrics = model_data['val_metrics']
        
        print(f"Model loaded from: {path}")
        return self


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("CREDIT RISK MODEL DEVELOPMENT")
    print("=" * 60)
    
    # Load encoded dataset
    print("\nLoading encoded dataset...")
    df = pd.read_csv('data/credit_risk_dataset_encoded.csv')
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    print(f"Target distribution: {df['default'].value_counts().to_dict()}")
    
    # Initialize model
    model = CreditRiskModel()
    
    # Prepare features
    print("\n" + "=" * 60)
    print("FEATURE PREPARATION")
    print("=" * 60)
    features = model.prepare_features(df)
    print(f"\nFeature list ({len(features)} features):")
    for i, feat in enumerate(features[:10]):
        print(f"  {i+1}. {feat}")
    if len(features) > 10:
        print(f"  ... and {len(features) - 10} more features")
    
    # Split data (80/20)
    X_train, X_val, y_train, y_val = model.split_data(df, test_size=0.2)
    
    # Train model
    model.train(X_train, y_train, X_val, y_val)
    
    # Evaluate on training set
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    
    model.train_metrics, train_pred = model.evaluate(X_train, y_train, 'Training')
    model.val_metrics, val_pred = model.evaluate(X_val, y_val, 'Validation')
    
    # Feature Importance
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE (Top 20)")
    print("=" * 60)
    
    feature_imp = model.get_feature_importance(top_n=20)
    print(f"\n{'Rank':<6} {'Feature':<40} {'Importance %':<12}")
    print("-" * 60)
    for i, row in feature_imp.iterrows():
        rank = feature_imp.index.get_loc(i) + 1
        print(f"{rank:<6} {row['feature']:<40} {row['importance_pct']:.2f}%")
    
    # Save model
    model.save_model('models/credit_risk_lgbm.pkl')
    
    # Save feature importance
    feature_imp_full = model.get_feature_importance(top_n=len(features))
    feature_imp_full.to_csv('models/feature_importance.csv', index=False)
    print(f"Feature importance saved to: models/feature_importance.csv")
    
    # Save predictions for validation set
    val_results = pd.DataFrame({
        'applicant_id': df.loc[X_val.index, 'applicant_id'].values,
        'actual': y_val.values,
        'predicted_probability': val_pred,
        'predicted_class': (val_pred >= 0.5).astype(int)
    })
    val_results.to_csv('models/validation_predictions.csv', index=False)
    print(f"Validation predictions saved to: models/validation_predictions.csv")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("MODEL DEVELOPMENT SUMMARY")
    print("=" * 60)
    
    print(f"\n{'Configuration':<30} {'Value'}")
    print("-" * 50)
    print(f"{'Algorithm':<30} LightGBM (Gradient Boosting)")
    print(f"{'Train/Validation Split':<30} 80/20")
    print(f"{'Training Samples':<30} {len(X_train)}")
    print(f"{'Validation Samples':<30} {len(X_val)}")
    print(f"{'Number of Features':<30} {len(features)}")
    print(f"{'Best Iteration':<30} {model.model.best_iteration}")
    
    print(f"\n{'Metric':<30} {'Training':<15} {'Validation':<15} {'Target'}")
    print("-" * 75)
    print(f"{'AUC-ROC':<30} {model.train_metrics['auc_roc']:<15.4f} {model.val_metrics['auc_roc']:<15.4f} ≥ 0.80")
    print(f"{'KS Statistic':<30} {model.train_metrics['ks_statistic']:<15.2f} {model.val_metrics['ks_statistic']:<15.2f} ≥ 30")
    print(f"{'Gini Coefficient':<30} {model.train_metrics['gini']:<15.4f} {model.val_metrics['gini']:<15.4f}")
    
    # Check if targets are met
    print("\n" + "-" * 50)
    auc_pass = model.val_metrics['auc_roc'] >= 0.80
    ks_pass = model.val_metrics['ks_statistic'] >= 30
    
    if auc_pass and ks_pass:
        print("✓ ALL TARGETS MET - Model is ready for deployment!")
    else:
        if not auc_pass:
            print("✗ AUC-ROC target not met")
        if not ks_pass:
            print("✗ KS Statistic target not met")
        print("\nConsider: hyperparameter tuning, feature engineering, or more data")
    
    return model


if __name__ == "__main__":
    model = main()
