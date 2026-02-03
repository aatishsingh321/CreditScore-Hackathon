# Feature Engineering Guide

## Overview
This guide describes the comprehensive feature engineering pipeline implemented for the Credit Risk Scoring System. The pipeline creates 52 new features across 4 categories.

---

## 📊 Feature Categories

### 1. Financial Ratios (7 Features) ✓

Financial health indicators based on income, debt, and obligations.

| Feature | Formula | Purpose |
|---------|---------|---------|
| `total_financial_obligation_ratio` | (EMI + Debt/60) * 12 / Income | Total monthly financial burden |
| `disposable_income_ratio` | 1 - EMI_ratio - Spending_ratio | Available income after obligations |
| `loan_to_monthly_income` | Loan / Monthly_Income | Loan size relative to monthly earnings |
| `debt_per_account` | Total_Debt / Num_Accounts | Average debt per credit account |
| `unsecured_loan_percentage` | 100 - Secured_Loan_% | Proportion of unsecured debt |
| `income_stability_score` | Years_Current / Years_Total | Employment stability indicator |
| `financial_burden_score` | Weighted avg of DTI, Util, EMI | Composite financial stress metric |

**Use Cases:**
- Assessing borrower's capacity to repay
- Identifying over-leveraged applicants
- Evaluating financial stability

---

### 2. Behavioral Features (14 Features) ✓

Payment patterns, spending habits, and financial discipline indicators.

| Feature | Description | Range |
|---------|-------------|-------|
| `has_payment_delays` | Any payment delays in last 12m | 0/1 |
| `severe_delinquency_flag` | 90+ day delays | 0/1 |
| `payment_delinquency_score` | Severity of payment issues | 0-1 |
| `spending_stability` | Inverse of balance volatility | 0-1 |
| `spending_pattern_score` | Quality of spending habits | 0-1 |
| `bounce_check_severity` | Bounced checks + EMI bounces | 0+ |
| `payment_reliability_score` | Salary regularity + bounce rate | 0-1 |
| `digital_txn_propensity` | Digital transaction usage | 0-1 |
| `cash_dependency_score` | Cash withdrawal dependency | 0-1 |
| `account_management_score` | Min balance breach rate | 0-1 |
| `financial_discipline_score` | Composite discipline metric | 0-1 |
| `spend_to_income_ratio` | Monthly spend / Income | 0+ |
| `discretionary_spend_amount` | Non-essential spending | 0+ |
| `financial_stress_indicator` | Count of stress signals | 0-3 |

**Key Insights:**
- Payment reliability predicts default risk
- High spending volatility indicates instability
- Digital transaction adoption correlates with financial literacy

---

### 3. Derived Metrics (14 Features) ✓

Time-based patterns, trends, and forward-looking projections.

| Feature | Description | Interpretation |
|---------|-------------|----------------|
| `estimated_delinquency_6m` | Recent 6-month delinquencies | Short-term risk indicator |
| `delinquency_trend` | Comparing 6m vs 12m rates | Improving/Worsening pattern |
| `balance_volatility_category` | Low/Med/High/Very High | Risk categorization |
| `balance_stability_score` | Normalized volatility | 0=unstable, 1=stable |
| `credit_maturity_score` | Credit history length | 0=new, 1=mature (10y+) |
| `active_account_ratio` | Active / Total accounts | Account utilization |
| `enquiry_velocity_6m` | Monthly enquiry rate | Credit seeking behavior |
| `enquiry_acceleration` | 6m vs 6m change | Increasing/decreasing trend |
| `recent_enquiry_intensity` | 6m share of 12m enquiries | Recent activity spike |
| `debt_growth_indicator` | New debt as % of total | Debt accumulation rate |
| `projected_total_debt` | Current + New loan | Future debt level |
| `projected_dti_after_loan` | DTI after approval | Forward-looking risk |
| `rolling_risk_score_6m` | Short-term risk composite | Recent risk profile |
| `credit_trend_indicator` | Improving/Stable/Deteriorating | Trajectory assessment |

**Applications:**
- Identify worsening credit behavior
- Predict post-loan financial stress
- Detect credit-seeking sprees

---

### 4. Bureau Features (17 Features) ✓

Credit bureau data transformations, default history, and enquiry patterns.

| Feature | Description | Risk Signal |
|---------|-------------|-------------|
| `total_past_defaults` | Write-offs + Settlements + Delinquent | Historical default count |
| `has_past_defaults` | Any default history | Binary flag |
| `has_writeoff` | Loan write-off history | Severe default flag |
| `has_settlements` | Settlement history | Partial default flag |
| `enquiry_rate_monthly` | Avg enquiries per month (12m) | Credit hunger |
| `enquiry_rate_6m` | Recent monthly enquiry rate | Short-term hunger |
| `high_enquiry_flag` | 6+ enquiries in 6m | Desperation signal |
| `credit_hungry_score` | Normalized enquiry intensity | 0=low, 1=high |
| `credit_score_category` | Poor/Fair/Good/Excellent | Qualitative rating |
| `credit_score_normalized` | (Score-300)/600 | 0-1 scale |
| `negative_events_count` | Sum of all negative events | Aggregate risk |
| `credit_history_quality` | Composite bureau health | Overall quality score |
| `delinquency_rate` | % of accounts delinquent | Portfolio quality |
| `bureau_default_probability` | Bureau-based default risk | 0-1 probability |
| `credit_mix_score` | Account diversity + secured% | Portfolio balance |
| `enquiry_to_account_ratio` | Enquiries / Accounts | Seeking vs having |
| `bureau_risk_score` | Overall bureau risk | Composite risk metric |

**Critical Indicators:**
- `has_writeoff` = Strongest default predictor
- `high_enquiry_flag` = Credit desperation
- `bureau_default_probability` = Overall bureau risk
- `credit_history_quality` = Composite health metric

---

## 🔧 Implementation

### Basic Usage

```python
from feature_engineering import FeatureEngineer
import pandas as pd

# Load data
df = pd.read_csv('data/credit_risk_dataset.csv')

# Create feature engineer
engineer = FeatureEngineer(verbose=True)

# Apply all transformations
df_features = engineer.transform_all(df)

# Save
df_features.to_csv('data/credit_risk_dataset_features.csv', index=False)
```

### Individual Category Processing

```python
# Only financial ratios
df_financial = engineer.calculate_financial_ratios(df)

# Only behavioral features
df_behavioral = engineer.extract_behavioral_features(df)

# Only derived metrics
df_derived = engineer.compute_derived_metrics(df)

# Only bureau features
df_bureau = engineer.process_bureau_features(df)
```

### Get Feature Lists

```python
# All engineered features
all_features = engineer.get_feature_list()

# By category
financial = engineer.get_feature_list('financial_ratios')
behavioral = engineer.get_feature_list('behavioral_features')
derived = engineer.get_feature_list('derived_metrics')
bureau = engineer.get_feature_list('bureau_features')
```

---

## 📈 Feature Statistics

### Dataset Transformation

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Columns | 51 | 103 | +52 |
| Feature Columns | ~42 | ~94 | +52 |
| Financial Ratios | 5 | 12 | +7 |
| Behavioral | 11 | 25 | +14 |
| Time-based | 0 | 14 | +14 |
| Bureau Derived | 12 | 29 | +17 |

### Feature Value Ranges

```python
# Key feature distributions
financial_burden_score:      0.0 - 3.0  (mean: 0.74)
payment_reliability_score:   0.0 - 1.0  (mean: 0.82)
credit_history_quality:      0.0 - 1.0  (mean: 0.67)
bureau_default_probability:  0.0 - 1.0  (mean: 0.28)
```

---

## 🎯 Feature Selection Recommendations

### High-Impact Features (Top 15)

Based on credit risk modeling best practices:

1. **`bureau_default_probability`** - Bureau-based risk
2. **`credit_score`** - Traditional credit score
3. **`financial_burden_score`** - Overall financial stress
4. **`has_writeoff`** - Severe default history
5. **`payment_delinquency_score`** - Payment behavior
6. **`projected_dti_after_loan`** - Forward-looking DTI
7. **`total_past_defaults`** - Default count
8. **`credit_history_quality`** - Bureau health
9. **`enquiry_rate_6m`** - Credit seeking
10. **`financial_discipline_score`** - Behavioral discipline
11. **`severe_delinquency_flag`** - 90+ day delays
12. **`bounce_check_severity`** - Payment failures
13. **`debt_to_income_ratio`** - Core DTI
14. **`credit_utilization`** - Credit usage
15. **`emi_to_income_ratio`** - Payment burden

### Feature Groups for Model Training

**Core Risk Features (8)**
- credit_score
- debt_to_income_ratio
- credit_utilization
- emi_to_income_ratio
- total_outstanding_debt
- loan_amount_requested
- annual_income
- employment_type

**Behavioral Risk Features (6)**
- payment_delinquency_score
- financial_discipline_score
- bounce_check_severity
- spending_stability
- payment_reliability_score
- financial_stress_indicator

**Bureau Risk Features (5)**
- bureau_default_probability
- credit_history_quality
- total_past_defaults
- credit_hungry_score
- bureau_risk_score

**Forward-Looking Features (4)**
- projected_dti_after_loan
- debt_growth_indicator
- rolling_risk_score_6m
- credit_trend_indicator

---

## 🔬 Feature Engineering Techniques

### 1. Ratio Features
Transform absolute values into relative metrics
```python
debt_to_income_ratio = total_debt / annual_income
```

### 2. Aggregation Features
Combine multiple signals into composite scores
```python
financial_burden_score = (dti * 0.4) + (utilization * 0.3) + (emi_ratio * 0.3)
```

### 3. Flag Features
Convert continuous to binary indicators
```python
high_enquiry_flag = (num_enquiries_6m > 5).astype(int)
```

### 4. Trend Features
Capture directional changes
```python
enquiry_acceleration = enquiries_6m - enquiries_previous_6m
```

### 5. Normalization Features
Scale to 0-1 range for comparability
```python
credit_score_normalized = (score - 300) / 600
```

### 6. Interaction Features
Capture relationships between variables
```python
enquiry_to_account_ratio = num_enquiries / num_accounts
```

---

## 🎓 Domain Knowledge Integration

### Credit Risk Best Practices

**DTI Thresholds**
- < 0.35: Low risk
- 0.35 - 0.50: Moderate risk
- > 0.50: High risk

**Credit Utilization**
- < 30%: Optimal
- 30-50%: Acceptable
- > 50%: Warning sign
- > 80%: High risk

**Payment Delays**
- 0 days: Excellent
- 1-30 days: Minor concern
- 31-90 days: Moderate risk
- 90+ days: High risk

**Enquiry Rate**
- < 2 per 6m: Normal
- 2-5 per 6m: Elevated
- > 5 per 6m: High risk

---

## 📝 Best Practices

### 1. Handle Missing Values
```python
# Before feature engineering
df = df.fillna({
    'num_enquiries_6m': 0,
    'max_dpd_last_12m': 0,
    'balance_volatility': df['balance_volatility'].median()
})
```

### 2. Check for Infinite Values
```python
# After feature engineering
df_features = df_features.replace([np.inf, -np.inf], np.nan)
```

### 3. Validate Feature Ranges
```python
# Ensure ratios are non-negative
df_features['debt_to_income_ratio'] = df_features['debt_to_income_ratio'].clip(0, 100)
```

### 4. Document Business Logic
```python
# Clear documentation for domain rules
# Example: Severe delinquency = 90+ days past due
df['severe_delinquency_flag'] = (df['max_dpd_last_12m'] >= 90).astype(int)
```

---

## 🧪 Validation

### Feature Quality Checks

```python
# Check for null values in new features
new_features = engineer.get_feature_list()
print(df_features[new_features].isnull().sum())

# Check for infinite values
print(df_features[new_features].replace([np.inf, -np.inf], np.nan).isnull().sum())

# Check feature distributions
print(df_features[new_features].describe())
```

### Correlation Analysis

```python
# Identify highly correlated features
correlation_matrix = df_features[new_features].corr()
high_corr = correlation_matrix[abs(correlation_matrix) > 0.9]
```

---

## 🚀 Performance

### Processing Metrics
- Dataset size: 10,000 records
- Processing time: ~2-3 seconds
- Features created: 52
- Memory usage: ~15 MB increase

### Scalability
- Linear time complexity: O(n)
- No expensive operations (joins, sorts)
- Vectorized pandas operations
- Suitable for 1M+ records

---

## 📊 Feature Catalog

Complete list of all 52 engineered features:

### Financial (7)
1. total_financial_obligation_ratio
2. disposable_income_ratio
3. loan_to_monthly_income
4. debt_per_account
5. unsecured_loan_percentage
6. income_stability_score
7. financial_burden_score

### Behavioral (14)
8. has_payment_delays
9. severe_delinquency_flag
10. payment_delinquency_score
11. spending_stability
12. spending_pattern_score
13. bounce_check_severity
14. payment_reliability_score
15. digital_txn_propensity
16. cash_dependency_score
17. account_management_score
18. financial_discipline_score
19. spend_to_income_ratio
20. discretionary_spend_amount
21. financial_stress_indicator

### Derived Metrics (14)
22. estimated_delinquency_6m
23. delinquency_trend
24. balance_volatility_category
25. balance_stability_score
26. credit_maturity_score
27. active_account_ratio
28. enquiry_velocity_6m
29. enquiry_acceleration
30. recent_enquiry_intensity
31. debt_growth_indicator
32. projected_total_debt
33. projected_dti_after_loan
34. rolling_risk_score_6m
35. credit_trend_indicator

### Bureau Features (17)
36. total_past_defaults
37. has_past_defaults
38. has_writeoff
39. has_settlements
40. enquiry_rate_monthly
41. enquiry_rate_6m
42. high_enquiry_flag
43. credit_hungry_score
44. credit_score_category
45. credit_score_normalized
46. negative_events_count
47. credit_history_quality
48. delinquency_rate
49. bureau_default_probability
50. credit_mix_score
51. enquiry_to_account_ratio
52. bureau_risk_score

---

## 🔄 Next Steps

After feature engineering:

1. **Feature Selection**: Use correlation analysis, feature importance
2. **Encoding**: One-hot encode categorical features
3. **Scaling**: Standardize/normalize for ML models
4. **Model Training**: Use engineered features in LightGBM/XGBoost
5. **Validation**: Track feature drift in production

---

*Last Updated: February 3, 2026*
*Module: feature_engineering.py*
