"""
Demonstration of Model Evaluation Module
Shows comprehensive evaluation of credit risk model with:
- AUC-ROC calculation
- KS statistic calculation
- Target validation
- Visualization
"""

import pandas as pd
import numpy as np
from model_evaluation import ModelEvaluator, evaluate_model_from_predictions
import os
import warnings
warnings.filterwarnings('ignore')


def main():
    print("=" * 80)
    print("CREDIT RISK MODEL EVALUATION DEMO")
    print("=" * 80)
    
    # ============================================================================
    # STEP 1: Load Model Predictions
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Loading Model Predictions")
    print("=" * 80)
    
    predictions_file = "models/validation_predictions.csv"
    
    if not os.path.exists(predictions_file):
        print(f"❌ Error: {predictions_file} not found!")
        print("Please run train_model.py first to generate predictions.")
        return
    
    # Load predictions
    df = pd.read_csv(predictions_file)
    print(f"✓ Loaded predictions: {len(df)} records")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few predictions:")
    print(df.head())
    
    # Extract data
    y_true = df['actual'].values
    y_pred_proba = df['predicted_probability'].values
    y_pred_class = df['predicted_class'].values if 'predicted_class' in df.columns else None
    
    print(f"\n✓ Extracted evaluation data:")
    print(f"   - True labels: {len(y_true)} records")
    print(f"   - Probability predictions: {len(y_pred_proba)} records")
    print(f"   - Class predictions: {len(y_pred_class) if y_pred_class is not None else 'Not available'}")
    
    # ============================================================================
    # STEP 2: Create Evaluator and Calculate Metrics
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Calculating Evaluation Metrics")
    print("=" * 80)
    
    # Create evaluator with target thresholds
    evaluator = ModelEvaluator(target_auc=0.80, target_ks=30.0)
    print(f"✓ Created evaluator with targets: AUC ≥ 0.80, KS ≥ 30%")
    
    # Run comprehensive evaluation
    metrics = evaluator.evaluate(y_true, y_pred_proba, y_pred_class)
    print(f"\n✓ Calculated {len(metrics)} evaluation metrics")
    
    # ============================================================================
    # STEP 3: Display Individual Metrics
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Individual Metric Calculations")
    print("=" * 80)
    
    print("\n📊 DISCRIMINATION METRICS:")
    print(f"   AUC-ROC:           {metrics['auc_roc']:.6f}")
    print(f"   KS Statistic:      {metrics['ks_statistic']:.2f}%")
    print(f"   KS Threshold:      {metrics['ks_threshold']:.6f}")
    print(f"   Gini Coefficient:  {metrics['gini_coefficient']:.6f}")
    
    print("\n📊 CLASSIFICATION METRICS:")
    print(f"   Accuracy:          {metrics['accuracy']:.6f}")
    print(f"   Precision:         {metrics['precision']:.6f}")
    print(f"   Recall:            {metrics['recall']:.6f}")
    print(f"   F1-Score:          {metrics['f1_score']:.6f}")
    print(f"   Specificity:       {metrics['specificity']:.6f}")
    
    print("\n📊 CONFUSION MATRIX:")
    print(f"   True Positives:    {metrics['true_positives']}")
    print(f"   True Negatives:    {metrics['true_negatives']}")
    print(f"   False Positives:   {metrics['false_positives']}")
    print(f"   False Negatives:   {metrics['false_negatives']}")
    
    # ============================================================================
    # STEP 4: Validate Against Targets
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Validating Against Target Thresholds")
    print("=" * 80)
    
    validation = evaluator.validate_targets()
    
    print("\n🎯 AUC-ROC VALIDATION:")
    print(f"   Target:    ≥ {validation['auc_target']:.2f}")
    print(f"   Actual:    {validation['auc_actual']:.4f}")
    print(f"   Status:    {'✅ PASS' if validation['auc_pass'] else '❌ FAIL'}")
    
    print("\n🎯 KS STATISTIC VALIDATION:")
    print(f"   Target:    ≥ {validation['ks_target']:.0f}%")
    print(f"   Actual:    {validation['ks_actual']:.2f}%")
    print(f"   Status:    {'✅ PASS' if validation['ks_pass'] else '❌ FAIL'}")
    
    print("\n🎯 OVERALL MODEL VALIDATION:")
    if validation['overall_pass']:
        print("   ✅ MODEL MEETS ALL TARGET REQUIREMENTS")
        print("   The model is approved for production deployment.")
    else:
        print("   ❌ MODEL DOES NOT MEET TARGET REQUIREMENTS")
        print("   Model requires improvement before deployment.")
    
    # ============================================================================
    # STEP 5: Generate Comprehensive Report
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Generating Comprehensive Evaluation Report")
    print("=" * 80)
    print()
    
    report = evaluator.generate_report(verbose=True)
    
    # ============================================================================
    # STEP 6: Export Results
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 6: Exporting Results")
    print("=" * 80)
    
    # Export metrics to CSV
    metrics_file = "models/evaluation_metrics.csv"
    evaluator.export_metrics(metrics_file)
    print(f"✓ Metrics exported to: {metrics_file}")
    
    # Save report to text file
    report_file = "models/evaluation_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")
    
    # ============================================================================
    # STEP 7: Generate Visualizations (Optional)
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 7: Generating Visualizations (Optional)")
    print("=" * 80)
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        print("\n📈 Generating ROC Curve...")
        evaluator.plot_roc_curve(save_path="models/roc_curve.png", show=False)
        print("✓ ROC curve saved to: models/roc_curve.png")
        
        print("\n📈 Generating KS Curve...")
        evaluator.plot_ks_curve(save_path="models/ks_curve.png", show=False)
        print("✓ KS curve saved to: models/ks_curve.png")
        
        print("\n📈 Generating Confusion Matrix...")
        evaluator.plot_confusion_matrix(save_path="models/confusion_matrix.png", show=False)
        print("✓ Confusion matrix saved to: models/confusion_matrix.png")
        
    except Exception as e:
        print(f"⚠ Visualization generation skipped: {e}")
    
    # ============================================================================
    # STEP 8: Summary Statistics
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 8: Summary Statistics")
    print("=" * 80)
    
    print("\n📊 PREDICTION DISTRIBUTION:")
    print(f"   Mean Probability:     {y_pred_proba.mean():.4f}")
    print(f"   Median Probability:   {np.median(y_pred_proba):.4f}")
    print(f"   Std Dev:              {y_pred_proba.std():.4f}")
    print(f"   Min Probability:      {y_pred_proba.min():.4f}")
    print(f"   Max Probability:      {y_pred_proba.max():.4f}")
    
    print("\n📊 ACTUAL CLASS DISTRIBUTION:")
    actual_counts = pd.Series(y_true).value_counts().sort_index()
    print(f"   Class 0 (Non-Default): {actual_counts.get(0, 0)} ({actual_counts.get(0, 0)/len(y_true)*100:.1f}%)")
    print(f"   Class 1 (Default):     {actual_counts.get(1, 0)} ({actual_counts.get(1, 0)/len(y_true)*100:.1f}%)")
    
    print("\n📊 PREDICTED CLASS DISTRIBUTION:")
    if y_pred_class is not None:
        pred_counts = pd.Series(y_pred_class).value_counts().sort_index()
        print(f"   Class 0 (Non-Default): {pred_counts.get(0, 0)} ({pred_counts.get(0, 0)/len(y_pred_class)*100:.1f}%)")
        print(f"   Class 1 (Default):     {pred_counts.get(1, 0)} ({pred_counts.get(1, 0)/len(y_pred_class)*100:.1f}%)")
    
    # ============================================================================
    # STEP 9: Risk Score Analysis
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 9: Risk Score Decile Analysis")
    print("=" * 80)
    
    # Create deciles
    df['decile'] = pd.qcut(df['predicted_probability'], q=10, labels=False, duplicates='drop') + 1
    
    # Analyze by decile
    decile_analysis = df.groupby('decile').agg({
        'actual': ['count', 'sum', 'mean'],
        'predicted_probability': 'mean'
    }).round(4)
    
    decile_analysis.columns = ['Count', 'Defaults', 'Default_Rate', 'Avg_Score']
    
    print("\n📊 DECILE ANALYSIS:")
    print(decile_analysis)
    
    print("\n" + "=" * 80)
    print("✅ MODEL EVALUATION COMPLETE")
    print("=" * 80)
    
    print("\n📁 Generated Files:")
    print(f"   1. {metrics_file}")
    print(f"   2. {report_file}")
    if os.path.exists("models/roc_curve.png"):
        print(f"   3. models/roc_curve.png")
        print(f"   4. models/ks_curve.png")
        print(f"   5. models/confusion_matrix.png")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
