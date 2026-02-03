"""
Credit Risk Scoring - Model Evaluation
Implements:
- AUC-ROC metric calculation
- KS statistic calculation
- Target validation (AUC ≥ 0.80, KS ≥ 30)
- Comprehensive performance reporting
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    roc_auc_score, roc_curve, confusion_matrix,
    classification_report, precision_recall_curve,
    average_precision_score, f1_score, accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    """
    Comprehensive model evaluation framework for credit risk models
    
    Calculates key metrics:
    - AUC-ROC (Area Under ROC Curve)
    - KS Statistic (Kolmogorov-Smirnov)
    - Gini Coefficient
    - Precision, Recall, F1-Score
    - Confusion Matrix
    """
    
    def __init__(self, target_auc: float = 0.80, target_ks: float = 30.0):
        """
        Initialize evaluator with target thresholds
        
        Args:
            target_auc: Minimum acceptable AUC-ROC score (default: 0.80)
            target_ks: Minimum acceptable KS statistic (default: 30.0)
        """
        self.target_auc = target_auc
        self.target_ks = target_ks
        self.metrics = {}
        self.y_true = None
        self.y_pred_proba = None
        self.y_pred_class = None
        
    def calculate_auc_roc(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Calculate AUC-ROC (Area Under the Receiver Operating Characteristic curve)
        
        AUC-ROC measures the model's ability to distinguish between classes.
        - Range: 0 to 1
        - Interpretation:
          * 0.90-1.00: Excellent
          * 0.80-0.90: Good
          * 0.70-0.80: Fair
          * 0.60-0.70: Poor
          * 0.50-0.60: Fail (no better than random)
        
        Args:
            y_true: True binary labels (0 or 1)
            y_pred_proba: Predicted probabilities for positive class
            
        Returns:
            AUC-ROC score
        """
        auc = roc_auc_score(y_true, y_pred_proba)
        return auc
    
    def calculate_ks_statistic(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Tuple[float, float]:
        """
        Calculate KS (Kolmogorov-Smirnov) statistic
        
        KS measures the maximum separation between cumulative distributions
        of good (non-default) and bad (default) customers.
        
        - Range: 0 to 100
        - Interpretation:
          * 40+: Excellent model
          * 30-40: Good model
          * 20-30: Fair model
          * <20: Poor model
        
        Args:
            y_true: True binary labels (0 or 1)
            y_pred_proba: Predicted probabilities for positive class
            
        Returns:
            Tuple of (KS statistic, KS threshold where maximum separation occurs)
        """
        # Get ROC curve data
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        
        # KS is the maximum vertical distance between TPR and FPR
        ks_statistic = np.max(tpr - fpr) * 100  # Convert to percentage
        
        # Find the threshold at which KS is maximum
        ks_index = np.argmax(tpr - fpr)
        ks_threshold = thresholds[ks_index]
        
        return ks_statistic, ks_threshold
    
    def calculate_gini(self, auc: float) -> float:
        """
        Calculate Gini coefficient from AUC
        
        Gini = 2 * AUC - 1
        - Range: 0 to 1
        - Interpretation: Higher is better (1 = perfect discrimination)
        
        Args:
            auc: AUC-ROC score
            
        Returns:
            Gini coefficient
        """
        return 2 * auc - 1
    
    def calculate_classification_metrics(self, y_true: np.ndarray, y_pred_class: np.ndarray) -> Dict:
        """
        Calculate classification metrics (precision, recall, F1, accuracy)
        
        Args:
            y_true: True binary labels
            y_pred_class: Predicted binary labels
            
        Returns:
            Dictionary of classification metrics
        """
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred_class).ravel()
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred_class)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = f1_score(y_true, y_pred_class)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'specificity': specificity,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
    
    def evaluate(self, y_true: np.ndarray, y_pred_proba: np.ndarray, 
                 y_pred_class: Optional[np.ndarray] = None,
                 threshold: float = 0.5) -> Dict:
        """
        Comprehensive model evaluation
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            y_pred_class: Predicted classes (optional, will be generated if None)
            threshold: Classification threshold (default: 0.5)
            
        Returns:
            Dictionary containing all evaluation metrics
        """
        # Store data
        self.y_true = y_true
        self.y_pred_proba = y_pred_proba
        
        # Generate class predictions if not provided
        if y_pred_class is None:
            y_pred_class = (y_pred_proba >= threshold).astype(int)
        self.y_pred_class = y_pred_class
        
        # Calculate AUC-ROC
        auc = self.calculate_auc_roc(y_true, y_pred_proba)
        
        # Calculate KS statistic
        ks_stat, ks_threshold = self.calculate_ks_statistic(y_true, y_pred_proba)
        
        # Calculate Gini
        gini = self.calculate_gini(auc)
        
        # Calculate classification metrics
        clf_metrics = self.calculate_classification_metrics(y_true, y_pred_class)
        
        # Store all metrics
        self.metrics = {
            'auc_roc': auc,
            'ks_statistic': ks_stat,
            'ks_threshold': ks_threshold,
            'gini_coefficient': gini,
            **clf_metrics
        }
        
        return self.metrics
    
    def validate_targets(self) -> Dict[str, bool]:
        """
        Validate if model meets target performance thresholds
        
        Returns:
            Dictionary with validation results
        """
        if not self.metrics:
            raise ValueError("No metrics calculated. Run evaluate() first.")
        
        auc_pass = self.metrics['auc_roc'] >= self.target_auc
        ks_pass = self.metrics['ks_statistic'] >= self.target_ks
        
        validation = {
            'auc_target': self.target_auc,
            'auc_actual': self.metrics['auc_roc'],
            'auc_pass': auc_pass,
            'ks_target': self.target_ks,
            'ks_actual': self.metrics['ks_statistic'],
            'ks_pass': ks_pass,
            'overall_pass': auc_pass and ks_pass
        }
        
        return validation
    
    def generate_report(self, verbose: bool = True) -> str:
        """
        Generate comprehensive evaluation report
        
        Args:
            verbose: If True, print report to console
            
        Returns:
            Formatted report string
        """
        if not self.metrics:
            raise ValueError("No metrics calculated. Run evaluate() first.")
        
        # Get validation results
        validation = self.validate_targets()
        
        report_lines = [
            "=" * 80,
            "MODEL EVALUATION REPORT",
            "=" * 80,
            "",
            "1. DISCRIMINATION METRICS",
            "-" * 80,
            f"   AUC-ROC:           {self.metrics['auc_roc']:.4f}  " + 
            f"{'✓ PASS' if validation['auc_pass'] else '✗ FAIL'} (Target: ≥{self.target_auc:.2f})",
            f"   KS Statistic:      {self.metrics['ks_statistic']:.2f}%  " +
            f"{'✓ PASS' if validation['ks_pass'] else '✗ FAIL'} (Target: ≥{self.target_ks}%)",
            f"   KS Threshold:      {self.metrics['ks_threshold']:.4f}",
            f"   Gini Coefficient:  {self.metrics['gini_coefficient']:.4f}",
            "",
            "2. CLASSIFICATION METRICS",
            "-" * 80,
            f"   Accuracy:          {self.metrics['accuracy']:.4f}",
            f"   Precision:         {self.metrics['precision']:.4f}",
            f"   Recall:            {self.metrics['recall']:.4f}",
            f"   F1-Score:          {self.metrics['f1_score']:.4f}",
            f"   Specificity:       {self.metrics['specificity']:.4f}",
            "",
            "3. CONFUSION MATRIX",
            "-" * 80,
            f"   True Positives:    {self.metrics['true_positives']}",
            f"   True Negatives:    {self.metrics['true_negatives']}",
            f"   False Positives:   {self.metrics['false_positives']}",
            f"   False Negatives:   {self.metrics['false_negatives']}",
            "",
            "4. MODEL INTERPRETATION",
            "-" * 80,
        ]
        
        # Add AUC interpretation
        auc = self.metrics['auc_roc']
        if auc >= 0.90:
            auc_interp = "EXCELLENT - Model has excellent discrimination"
        elif auc >= 0.80:
            auc_interp = "GOOD - Model has good discrimination"
        elif auc >= 0.70:
            auc_interp = "FAIR - Model has fair discrimination"
        elif auc >= 0.60:
            auc_interp = "POOR - Model has poor discrimination"
        else:
            auc_interp = "FAIL - Model is no better than random"
        
        report_lines.append(f"   AUC-ROC: {auc_interp}")
        
        # Add KS interpretation
        ks = self.metrics['ks_statistic']
        if ks >= 40:
            ks_interp = "EXCELLENT - Strong separation between classes"
        elif ks >= 30:
            ks_interp = "GOOD - Good separation between classes"
        elif ks >= 20:
            ks_interp = "FAIR - Fair separation between classes"
        else:
            ks_interp = "POOR - Weak separation between classes"
        
        report_lines.append(f"   KS Statistic: {ks_interp}")
        
        report_lines.extend([
            "",
            "5. VALIDATION SUMMARY",
            "-" * 80,
            f"   Overall Status:    {'✓ PASS' if validation['overall_pass'] else '✗ FAIL'}",
            "",
            "=" * 80
        ])
        
        report = "\n".join(report_lines)
        
        if verbose:
            print(report)
        
        return report
    
    def plot_roc_curve(self, save_path: Optional[str] = None, show: bool = True):
        """
        Plot ROC curve
        
        Args:
            save_path: Path to save plot (optional)
            show: If True, display plot
        """
        if self.y_true is None or self.y_pred_proba is None:
            raise ValueError("No data available. Run evaluate() first.")
        
        # Calculate ROC curve
        fpr, tpr, _ = roc_curve(self.y_true, self.y_pred_proba)
        
        # Create plot
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', lw=2, 
                label=f'ROC Curve (AUC = {self.metrics["auc_roc"]:.4f})')
        plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_ks_curve(self, save_path: Optional[str] = None, show: bool = True):
        """
        Plot KS curve showing separation between good and bad customers
        
        Args:
            save_path: Path to save plot (optional)
            show: If True, display plot
        """
        if self.y_true is None or self.y_pred_proba is None:
            raise ValueError("No data available. Run evaluate() first.")
        
        # Calculate ROC curve components
        fpr, tpr, thresholds = roc_curve(self.y_true, self.y_pred_proba)
        
        # Calculate KS
        ks_stat = (tpr - fpr) * 100
        ks_max_idx = np.argmax(ks_stat)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(thresholds, tpr * 100, label='True Positive Rate (Bad)', color='red', lw=2)
        plt.plot(thresholds, fpr * 100, label='False Positive Rate (Good)', color='blue', lw=2)
        plt.plot(thresholds, ks_stat, label='KS Statistic', color='green', lw=2, linestyle='--')
        
        # Mark maximum KS
        plt.axvline(x=thresholds[ks_max_idx], color='black', linestyle=':', 
                   label=f'Max KS = {self.metrics["ks_statistic"]:.2f}% at {thresholds[ks_max_idx]:.4f}')
        
        plt.xlabel('Threshold')
        plt.ylabel('Percentage (%)')
        plt.title('KS Statistic Curve')
        plt.legend(loc='best')
        plt.grid(alpha=0.3)
        plt.xlim([0, 1])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_confusion_matrix(self, save_path: Optional[str] = None, show: bool = True):
        """
        Plot confusion matrix heatmap
        
        Args:
            save_path: Path to save plot (optional)
            show: If True, display plot
        """
        if self.y_true is None or self.y_pred_class is None:
            raise ValueError("No data available. Run evaluate() first.")
        
        # Calculate confusion matrix
        cm = confusion_matrix(self.y_true, self.y_pred_class)
        
        # Create plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Non-Default', 'Default'],
                   yticklabels=['Non-Default', 'Default'])
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.title('Confusion Matrix')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def export_metrics(self, filepath: str):
        """
        Export metrics to CSV file
        
        Args:
            filepath: Path to save metrics CSV
        """
        if not self.metrics:
            raise ValueError("No metrics calculated. Run evaluate() first.")
        
        # Create DataFrame
        metrics_df = pd.DataFrame([self.metrics])
        
        # Add validation results
        validation = self.validate_targets()
        validation_df = pd.DataFrame([validation])
        
        # Combine
        export_df = pd.concat([metrics_df, validation_df], axis=1)
        
        # Save
        export_df.to_csv(filepath, index=False)
        print(f"Metrics exported to: {filepath}")


def evaluate_model_from_predictions(predictions_file: str, 
                                    target_auc: float = 0.80,
                                    target_ks: float = 30.0) -> ModelEvaluator:
    """
    Convenience function to evaluate model from predictions CSV
    
    Expected CSV columns:
    - actual: True labels (0 or 1)
    - predicted_probability: Predicted probabilities
    - predicted_class: Predicted classes (optional)
    
    Args:
        predictions_file: Path to predictions CSV
        target_auc: Target AUC threshold
        target_ks: Target KS threshold
        
    Returns:
        ModelEvaluator instance with results
    """
    # Load predictions
    df = pd.read_csv(predictions_file)
    
    # Extract required columns
    y_true = df['actual'].values
    y_pred_proba = df['predicted_probability'].values
    
    # Get predicted class if available
    y_pred_class = df['predicted_class'].values if 'predicted_class' in df.columns else None
    
    # Create evaluator
    evaluator = ModelEvaluator(target_auc=target_auc, target_ks=target_ks)
    
    # Run evaluation
    evaluator.evaluate(y_true, y_pred_proba, y_pred_class)
    
    return evaluator


if __name__ == "__main__":
    print("Model Evaluation Module")
    print("=" * 80)
    print("\nUsage Example:")
    print("""
    from model_evaluation import ModelEvaluator
    
    # Create evaluator
    evaluator = ModelEvaluator(target_auc=0.80, target_ks=30.0)
    
    # Evaluate model
    metrics = evaluator.evaluate(y_true, y_pred_proba)
    
    # Generate report
    evaluator.generate_report()
    
    # Validate targets
    validation = evaluator.validate_targets()
    
    # Plot curves
    evaluator.plot_roc_curve()
    evaluator.plot_ks_curve()
    """)
