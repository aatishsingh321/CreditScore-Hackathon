# Model Evaluation Guide

## Overview
Comprehensive guide for evaluating credit risk models using industry-standard metrics: AUC-ROC and KS Statistic.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Key Metrics](#key-metrics)
3. [Module Architecture](#module-architecture)
4. [Usage Guide](#usage-guide)
5. [Interpretation](#interpretation)
6. [Target Validation](#target-validation)
7. [Best Practices](#best-practices)

---

## 1. Introduction

Model evaluation is critical for credit risk scoring systems to ensure:
- **Discrimination Power**: Model can distinguish between good and bad customers
- **Business Value**: Predictions are actionable for lending decisions
- **Regulatory Compliance**: Meets industry standards and requirements
- **Continuous Improvement**: Track model performance over time

---

## 2. Key Metrics

### 2.1 AUC-ROC (Area Under ROC Curve)

**Definition**: Measures the model's ability to rank positive cases higher than negative cases.

**Range**: 0.0 to 1.0

**Interpretation**:
- **0.90 - 1.00**: Excellent - Outstanding discrimination
- **0.80 - 0.90**: Good - Acceptable for production
- **0.70 - 0.80**: Fair - May need improvement
- **0.60 - 0.70**: Poor - Significant improvement needed
- **0.50 - 0.60**: Fail - No better than random guessing

**Advantages**:
- Threshold-independent measure
- Widely used and understood
- Robust to class imbalance

**Target**: **AUC ≥ 0.80**

---

### 2.2 KS Statistic (Kolmogorov-Smirnov)

**Definition**: Maximum vertical distance between cumulative distributions of good and bad customers.

**Formula**: KS = max(TPR - FPR) × 100

**Range**: 0 to 100 (percentage)

**Interpretation**:
- **40+**: Excellent - Strong separation
- **30 - 40**: Good - Acceptable separation
- **20 - 30**: Fair - Weak separation
- **< 20**: Poor - Insufficient discrimination

**Advantages**:
- Intuitive business interpretation
- Identifies optimal threshold
- Common in credit risk industry

**Target**: **KS ≥ 30%**

---

### 2.3 Gini Coefficient

**Definition**: Derived from AUC, measures inequality in predictions.

**Formula**: Gini = 2 × AUC - 1

**Range**: 0.0 to 1.0

**Interpretation**: Higher is better (1 = perfect discrimination)

---

### 2.4 Classification Metrics

**Accuracy**: Overall correctness of predictions
- Formula: (TP + TN) / Total

**Precision**: Accuracy of positive predictions
- Formula: TP / (TP + FP)
- Answers: "Of all predicted defaults, how many actually defaulted?"

**Recall (Sensitivity)**: Coverage of actual positives
- Formula: TP / (TP + FN)
- Answers: "Of all actual defaults, how many did we catch?"

**Specificity**: Coverage of actual negatives
- Formula: TN / (TN + FP)
- Answers: "Of all non-defaults, how many did we correctly identify?"

**F1-Score**: Harmonic mean of precision and recall
- Formula: 2 × (Precision × Recall) / (Precision + Recall)

---

## 3. Module Architecture

### 3.1 Core Class: ModelEvaluator

```python
from model_evaluation import ModelEvaluator

# Initialize with targets
evaluator = ModelEvaluator(target_auc=0.80, target_ks=30.0)

# Evaluate model
metrics = evaluator.evaluate(y_true, y_pred_proba, y_pred_class)

# Generate report
evaluator.generate_report()

# Validate targets
validation = evaluator.validate_targets()
```

### 3.2 Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `calculate_auc_roc()` | Calculate AUC-ROC score | float |
| `calculate_ks_statistic()` | Calculate KS statistic | (ks, threshold) |
| `calculate_gini()` | Calculate Gini coefficient | float |
| `calculate_classification_metrics()` | Calculate precision, recall, etc. | dict |
| `evaluate()` | Run comprehensive evaluation | dict |
| `validate_targets()` | Check if model meets targets | dict |
| `generate_report()` | Generate formatted report | str |
| `plot_roc_curve()` | Plot ROC curve | None |
| `plot_ks_curve()` | Plot KS curve | None |
| `plot_confusion_matrix()` | Plot confusion matrix | None |
| `export_metrics()` | Export to CSV | None |

---

## 4. Usage Guide

### 4.1 Basic Usage

```python
from model_evaluation import ModelEvaluator
import numpy as np

# Your model predictions
y_true = np.array([0, 1, 0, 1, 1])
y_pred_proba = np.array([0.2, 0.8, 0.3, 0.7, 0.9])

# Create evaluator
evaluator = ModelEvaluator(target_auc=0.80, target_ks=30.0)

# Evaluate
metrics = evaluator.evaluate(y_true, y_pred_proba)

# Generate report
evaluator.generate_report()
```

### 4.2 From CSV File

```python
from model_evaluation import evaluate_model_from_predictions

# Load and evaluate from CSV
evaluator = evaluate_model_from_predictions(
    predictions_file="models/validation_predictions.csv",
    target_auc=0.80,
    target_ks=30.0
)

# Generate report
evaluator.generate_report()
```

### 4.3 Validation Against Targets

```python
# Check if model meets requirements
validation = evaluator.validate_targets()

print(f"AUC: {validation['auc_actual']:.4f} (Target: {validation['auc_target']:.2f})")
print(f"KS:  {validation['ks_actual']:.2f}% (Target: {validation['ks_target']:.0f}%)")

if validation['overall_pass']:
    print("✅ Model approved for production")
else:
    print("❌ Model needs improvement")
```

### 4.4 Generate Visualizations

```python
# ROC Curve
evaluator.plot_roc_curve(save_path="roc_curve.png", show=True)

# KS Curve
evaluator.plot_ks_curve(save_path="ks_curve.png", show=True)

# Confusion Matrix
evaluator.plot_confusion_matrix(save_path="confusion_matrix.png", show=True)
```

### 4.5 Export Results

```python
# Export metrics to CSV
evaluator.export_metrics("evaluation_metrics.csv")

# Save report to file
report = evaluator.generate_report(verbose=False)
with open("evaluation_report.txt", 'w') as f:
    f.write(report)
```

---

## 5. Interpretation

### 5.1 Reading the Report

**Section 1: Discrimination Metrics**
- Shows model's ability to separate classes
- Focus on AUC-ROC and KS statistic
- ✓ PASS or ✗ FAIL against targets

**Section 2: Classification Metrics**
- Shows performance at chosen threshold
- Balance precision vs recall based on business needs

**Section 3: Confusion Matrix**
- True Positives: Correctly predicted defaults
- False Positives: Incorrectly flagged as default (Type I error)
- False Negatives: Missed defaults (Type II error)
- True Negatives: Correctly predicted non-defaults

**Section 4: Model Interpretation**
- Plain English interpretation of metrics
- Business-friendly explanations

**Section 5: Validation Summary**
- Overall PASS/FAIL status
- Production readiness assessment

### 5.2 Understanding Trade-offs

**High Precision, Low Recall**:
- Conservative model
- Few false alarms, but misses many defaults
- Good for premium products

**Low Precision, High Recall**:
- Aggressive model
- Catches most defaults, but many false alarms
- Good for high-risk portfolios

**Balanced F1-Score**:
- Compromise between precision and recall
- Good starting point for most applications

---

## 6. Target Validation

### 6.1 Industry Standards

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| AUC-ROC | 0.70 | 0.80 | 0.90 |
| KS Statistic | 20% | 30% | 40% |
| Gini | 0.40 | 0.60 | 0.80 |

### 6.2 Hackathon Targets

- **AUC-ROC**: ≥ 0.80 (Good)
- **KS Statistic**: ≥ 30% (Good)

These are **industry-standard thresholds** suitable for production credit risk models.

### 6.3 What If Model Doesn't Meet Targets?

**Options**:
1. **Feature Engineering**: Add more predictive features
2. **Hyperparameter Tuning**: Optimize model parameters
3. **Algorithm Selection**: Try different models (XGBoost, Neural Networks)
4. **Data Quality**: Improve data collection and cleaning
5. **Ensemble Methods**: Combine multiple models
6. **Domain Expertise**: Incorporate expert business rules

---

## 7. Best Practices

### 7.1 Evaluation Strategy

1. **Split Data Properly**
   - Use separate validation/test sets
   - Never evaluate on training data
   - Consider time-based splits for temporal data

2. **Monitor Multiple Metrics**
   - Don't rely on single metric
   - Consider business context
   - Track trends over time

3. **Validate on Recent Data**
   - Model performance may degrade
   - Use most recent data for validation
   - Set up monitoring for production

### 7.2 Threshold Selection

**Methods**:
1. **KS Threshold**: Use threshold at maximum KS
2. **Business Rules**: Based on risk appetite
3. **Cost-Benefit Analysis**: Minimize expected loss
4. **Regulatory Requirements**: Compliance constraints

**Example**:
```python
# Get optimal threshold from KS
metrics = evaluator.evaluate(y_true, y_pred_proba)
optimal_threshold = metrics['ks_threshold']

# Use for predictions
y_pred_class = (y_pred_proba >= optimal_threshold).astype(int)
```

### 7.3 Monitoring in Production

**Track These Metrics**:
- AUC-ROC over time
- KS statistic over time
- Default rate vs predicted rate
- Score distribution shifts
- Feature drift

**Set Alerts For**:
- AUC drops below threshold
- KS drops below threshold
- Significant score distribution changes
- Unusual default patterns

### 7.4 Documentation

**Always Document**:
- Model version and date
- Training data period
- Validation results
- Threshold selection rationale
- Approval status
- Known limitations

---

## 8. Example Output

### 8.1 Sample Evaluation Report

```
================================================================================
MODEL EVALUATION REPORT
================================================================================

1. DISCRIMINATION METRICS
--------------------------------------------------------------------------------
   AUC-ROC:           0.6764  ✗ FAIL (Target: ≥0.80)
   KS Statistic:      26.30%  ✗ FAIL (Target: ≥30.0%)
   KS Threshold:      0.3870
   Gini Coefficient:  0.3528

2. CLASSIFICATION METRICS
--------------------------------------------------------------------------------
   Accuracy:          0.6925
   Precision:         0.3045
   Recall:            0.5121
   F1-Score:          0.3819
   Specificity:       0.7336

3. CONFUSION MATRIX
--------------------------------------------------------------------------------
   True Positives:    190
   True Negatives:    1195
   False Positives:   434
   False Negatives:   181

4. MODEL INTERPRETATION
--------------------------------------------------------------------------------
   AUC-ROC: POOR - Model has poor discrimination
   KS Statistic: FAIR - Fair separation between classes

5. VALIDATION SUMMARY
--------------------------------------------------------------------------------
   Overall Status:    ✗ FAIL
```

---

## 9. Troubleshooting

### 9.1 Common Issues

**Issue**: Low AUC-ROC
- **Cause**: Weak features, poor model
- **Solution**: Feature engineering, try different algorithms

**Issue**: Low KS Statistic
- **Cause**: Poor class separation
- **Solution**: Add discriminative features, adjust threshold

**Issue**: High AUC but Low Precision
- **Cause**: Class imbalance, wrong threshold
- **Solution**: Adjust threshold, use class weights

**Issue**: Overfitting (Train AUC >> Validation AUC)
- **Cause**: Model too complex
- **Solution**: Regularization, reduce complexity, more data

---

## 10. References

- **AUC-ROC**: Hanley & McNeil (1982)
- **KS Statistic**: Kolmogorov (1933), Smirnov (1948)
- **Credit Risk Modeling**: Siddiqi (2006) - "Credit Risk Scorecards"
- **Model Validation**: Basel Committee on Banking Supervision

---

## Quick Reference

### Key Commands

```python
# Basic evaluation
evaluator = ModelEvaluator(target_auc=0.80, target_ks=30.0)
metrics = evaluator.evaluate(y_true, y_pred_proba)
evaluator.generate_report()

# Validation
validation = evaluator.validate_targets()
print(f"Status: {'PASS' if validation['overall_pass'] else 'FAIL'}")

# Visualization
evaluator.plot_roc_curve(save_path="roc.png")
evaluator.plot_ks_curve(save_path="ks.png")

# Export
evaluator.export_metrics("metrics.csv")
```

### Metrics Thresholds

| Metric | Target | Excellent |
|--------|--------|-----------|
| AUC-ROC | ≥ 0.80 | ≥ 0.90 |
| KS Statistic | ≥ 30% | ≥ 40% |
| Gini | ≥ 0.60 | ≥ 0.80 |

---

*Last Updated: February 3, 2026*
