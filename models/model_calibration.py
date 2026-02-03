"""
Credit Risk Scoring - Model Calibration
Evaluates calibration need and implements calibration if required

Calibration ensures predicted probabilities match actual default rates.
E.g., if model predicts 30% default probability, ~30% of those cases should actually default.
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')


class ModelCalibrator:
    """Evaluate and apply model calibration for credit risk predictions"""
    
    def __init__(self):
        self.model = None
        self.calibrator = None
        self.features = None
        self.calibration_method = None
        
    def load_model(self, model_path='models/credit_risk_lgbm_optimized.pkl'):
        """Load trained model"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.features = model_data['features']
        print(f"Loaded model from: {model_path}")
        return self
    
    def calculate_calibration_metrics(self, y_true, y_pred_proba):
        """Calculate calibration metrics"""
        # Brier Score
        brier = brier_score_loss(y_true, y_pred_proba)
        
        # Log Loss
        logloss = log_loss(y_true, np.clip(y_pred_proba, 1e-10, 1-1e-10))
        
        # Calibration curve
        prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=10, strategy='uniform')
        
        # Expected Calibration Error
        n_bins = len(prob_true)
        bin_counts = np.histogram(y_pred_proba, bins=10, range=(0, 1))[0]
        bin_weights = bin_counts / len(y_pred_proba)
        ece = np.sum(bin_weights[:n_bins] * np.abs(prob_true - prob_pred))
        
        # Maximum Calibration Error
        mce = np.max(np.abs(prob_true - prob_pred)) if len(prob_true) > 0 else 0
        
        return {
            'brier_score': brier,
            'log_loss': logloss,
            'ece': ece,
            'mce': mce,
            'prob_true': prob_true,
            'prob_pred': prob_pred
        }
    
    def evaluate_calibration_need(self, X, y):
        """Evaluate if model calibration is needed"""
        print("\n" + "=" * 60)
        print("CALIBRATION EVALUATION")
        print("=" * 60)
        
        # Get predictions
        y_pred = self.model.predict(X)
        metrics = self.calculate_calibration_metrics(y, y_pred)
        
        print(f"\n{'Metric':<30} {'Value':<15} {'Threshold':<15} {'Status'}")
        print("-" * 75)
        
        brier_status = "⚠ NEEDS CALIBRATION" if metrics['brier_score'] > 0.1 else "✓ OK"
        print(f"{'Brier Score':<30} {metrics['brier_score']:<15.4f} {'< 0.10':<15} {brier_status}")
        
        ece_status = "⚠ NEEDS CALIBRATION" if metrics['ece'] > 0.05 else "✓ OK"
        print(f"{'Expected Calibration Error':<30} {metrics['ece']:<15.4f} {'< 0.05':<15} {ece_status}")
        
        mce_status = "⚠ NEEDS CALIBRATION" if metrics['mce'] > 0.15 else "✓ OK"
        print(f"{'Max Calibration Error':<30} {metrics['mce']:<15.4f} {'< 0.15':<15} {mce_status}")
        
        print(f"{'Log Loss':<30} {metrics['log_loss']:<15.4f}")
        
        # Calibration curve analysis
        print("\n" + "-" * 60)
        print("CALIBRATION CURVE ANALYSIS")
        print("-" * 60)
        print(f"{'Bin':<8} {'Predicted':<12} {'Actual':<12} {'Gap':<12}")
        print("-" * 50)
        
        for i, (pred, true) in enumerate(zip(metrics['prob_pred'], metrics['prob_true'])):
            gap = abs(true - pred)
            flag = "⚠" if gap > 0.1 else ""
            print(f"{i+1:<8} {pred:<12.3f} {true:<12.3f} {gap:<12.3f} {flag}")
        
        needs_calibration = (
            metrics['brier_score'] > 0.1 or 
            metrics['ece'] > 0.05 or 
            metrics['mce'] > 0.15
        )
        
        print("\n" + "=" * 60)
        if needs_calibration:
            print("⚠ CALIBRATION RECOMMENDED")
        else:
            print("✓ MODEL IS WELL-CALIBRATED")
        print("=" * 60)
        
        return needs_calibration, metrics
    
    def fit_isotonic_calibration(self, X_cal, y_cal):
        """Fit isotonic regression calibrator"""
        print("\nFitting Isotonic Regression calibrator...")
        
        # Get uncalibrated predictions
        y_pred_uncal = self.model.predict(X_cal)
        
        # Fit isotonic regression
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.calibrator.fit(y_pred_uncal, y_cal)
        self.calibration_method = 'isotonic'
        
        print("Isotonic calibration fitted successfully!")
        return self
    
    def fit_platt_calibration(self, X_cal, y_cal):
        """Fit Platt scaling (sigmoid) calibrator"""
        print("\nFitting Platt Scaling calibrator...")
        
        # Get uncalibrated predictions
        y_pred_uncal = self.model.predict(X_cal).reshape(-1, 1)
        
        # Fit logistic regression
        self.calibrator = LogisticRegression(C=1e10, solver='lbfgs')
        self.calibrator.fit(y_pred_uncal, y_cal)
        self.calibration_method = 'platt'
        
        print("Platt scaling calibration fitted successfully!")
        return self
    
    def calibrate(self, X):
        """Apply calibration to predictions"""
        if self.calibrator is None:
            raise ValueError("Calibrator not fitted. Call fit_isotonic_calibration or fit_platt_calibration first.")
        
        # Get uncalibrated predictions
        y_pred_uncal = self.model.predict(X)
        
        # Apply calibration
        if self.calibration_method == 'isotonic':
            y_pred_cal = self.calibrator.predict(y_pred_uncal)
        else:  # platt
            y_pred_cal = self.calibrator.predict_proba(y_pred_uncal.reshape(-1, 1))[:, 1]
        
        return y_pred_cal
    
    def fit_with_cv(self, X, y, method='isotonic', n_folds=5):
        """
        Fit calibration using cross-validation to prevent overfitting
        """
        print(f"\n{'='*60}")
        print(f"FITTING CALIBRATION WITH {n_folds}-FOLD CV")
        print(f"Method: {method}")
        print(f"{'='*60}")
        
        kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        # Collect out-of-fold predictions for calibration
        oof_preds = np.zeros(len(y))
        
        for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
            print(f"Processing fold {fold+1}/{n_folds}...")
            oof_preds[val_idx] = self.model.predict(X.iloc[val_idx])
        
        # Fit calibrator on out-of-fold predictions
        if method == 'isotonic':
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(oof_preds, y)
            self.calibration_method = 'isotonic'
        else:
            self.calibrator = LogisticRegression(C=1e10, solver='lbfgs')
            self.calibrator.fit(oof_preds.reshape(-1, 1), y)
            self.calibration_method = 'platt'
        
        print(f"\n{method.capitalize()} calibration fitted on OOF predictions!")
        return self
    
    def compare_calibration(self, X, y):
        """Compare before and after calibration metrics"""
        print("\n" + "=" * 60)
        print("CALIBRATION COMPARISON")
        print("=" * 60)
        
        # Uncalibrated predictions
        y_pred_uncal = self.model.predict(X)
        uncal_metrics = self.calculate_calibration_metrics(y, y_pred_uncal)
        
        # Calibrated predictions
        y_pred_cal = self.calibrate(X)
        cal_metrics = self.calculate_calibration_metrics(y, y_pred_cal)
        
        print(f"\n{'Metric':<30} {'Before':<15} {'After':<15} {'Change'}")
        print("-" * 75)
        
        for metric in ['brier_score', 'ece', 'mce', 'log_loss']:
            before = uncal_metrics[metric]
            after = cal_metrics[metric]
            change = ((after - before) / before) * 100 if before != 0 else 0
            direction = "↓" if change < 0 else "↑"
            print(f"{metric:<30} {before:<15.4f} {after:<15.4f} {change:+.1f}% {direction}")
        
        # AUC should remain similar
        uncal_auc = roc_auc_score(y, y_pred_uncal)
        cal_auc = roc_auc_score(y, y_pred_cal)
        print(f"{'AUC-ROC':<30} {uncal_auc:<15.4f} {cal_auc:<15.4f} (preserved)")
        
        return uncal_metrics, cal_metrics, y_pred_uncal, y_pred_cal
    
    def plot_calibration(self, y_true, y_pred_uncal, y_pred_cal, save_path='models/calibration_plot.png'):
        """Plot calibration curves"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Calibration curves
        ax1 = axes[0]
        ax1.plot([0, 1], [0, 1], 'k--', label='Perfect', linewidth=2)
        
        prob_true_u, prob_pred_u = calibration_curve(y_true, y_pred_uncal, n_bins=10)
        ax1.plot(prob_pred_u, prob_true_u, 's-', label='Before', color='red', markersize=8)
        
        prob_true_c, prob_pred_c = calibration_curve(y_true, y_pred_cal, n_bins=10)
        ax1.plot(prob_pred_c, prob_true_c, 'o-', label='After', color='green', markersize=8)
        
        ax1.set_xlabel('Mean Predicted Probability', fontsize=12)
        ax1.set_ylabel('Fraction of Positives', fontsize=12)
        ax1.set_title('Calibration Curve', fontsize=14)
        ax1.legend(loc='lower right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Histograms
        ax2 = axes[1]
        ax2.hist(y_pred_uncal, bins=30, alpha=0.5, label='Before', color='red', density=True)
        ax2.hist(y_pred_cal, bins=30, alpha=0.5, label='After', color='green', density=True)
        ax2.set_xlabel('Predicted Probability', fontsize=12)
        ax2.set_ylabel('Density', fontsize=12)
        ax2.set_title('Prediction Distribution', fontsize=14)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"\nCalibration plot saved to: {save_path}")
    
    def save(self, path='models/credit_risk_calibrated.pkl'):
        """Save calibrated model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'base_model': self.model,
            'calibrator': self.calibrator,
            'features': self.features,
            'calibration_method': self.calibration_method
        }
        joblib.dump(model_data, path)
        print(f"\nCalibrated model saved to: {path}")


def main():
    print("=" * 60)
    print("MODEL CALIBRATION ANALYSIS")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    df = pd.read_csv('data/credit_risk_dataset_encoded.csv')
    print(f"Loaded {len(df)} records")
    
    # Initialize calibrator
    calibrator = ModelCalibrator()
    calibrator.load_model('models/credit_risk_lgbm_optimized.pkl')
    
    # Prepare data
    X = df[calibrator.features]
    y = df['default']
    
    # Split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Step 1: Evaluate calibration need
    needs_cal, uncal_metrics = calibrator.evaluate_calibration_need(X_test, y_test)
    
    # Step 2: Fit calibration using CV on training data
    print("\n" + "=" * 60)
    print("IMPLEMENTING CALIBRATION")
    print("=" * 60)
    
    calibrator.fit_with_cv(X_train, y_train, method='isotonic', n_folds=5)
    
    # Step 3: Compare metrics
    uncal_m, cal_m, y_pred_uncal, y_pred_cal = calibrator.compare_calibration(X_test, y_test)
    
    # Step 4: Plot calibration curves
    calibrator.plot_calibration(y_test, y_pred_uncal, y_pred_cal)
    
    # Step 5: Save calibrated model
    calibrator.save('models/credit_risk_calibrated.pkl')
    
    # Summary
    print("\n" + "=" * 60)
    print("CALIBRATION SUMMARY")
    print("=" * 60)
    
    print(f"\n{'Item':<35} {'Value'}")
    print("-" * 55)
    print(f"{'Calibration Method':<35} Isotonic Regression")
    print(f"{'CV Folds':<35} 5")
    print(f"{'Calibration Needed':<35} {'Yes' if needs_cal else 'No'}")
    
    print(f"\n{'Metric':<35} {'Before':<15} {'After'}")
    print("-" * 65)
    print(f"{'Brier Score':<35} {uncal_m['brier_score']:<15.4f} {cal_m['brier_score']:.4f}")
    print(f"{'Expected Calibration Error':<35} {uncal_m['ece']:<15.4f} {cal_m['ece']:.4f}")
    print(f"{'Max Calibration Error':<35} {uncal_m['mce']:<15.4f} {cal_m['mce']:.4f}")
    
    print("\n✓ Calibration complete!")
    print("\nBenefits of calibrated probabilities:")
    print("  • More accurate risk-based pricing")
    print("  • Better regulatory compliance")
    print("  • Improved portfolio risk assessment")
    
    return calibrator


if __name__ == "__main__":
    calibrator = main()
