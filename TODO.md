# Credit Risk Scoring System - Technical Todo List

## Project Overview
Build a data-driven Credit Risk Scoring System that predicts the likelihood of a loan applicant defaulting, using financial history, behavioral data, and credit bureau information.

---

## 1. ETL / Data Engineering Pipeline

### 1.1 Data Ingestion
- [x] Set up batch ingestion from core banking systems
- [x] Implement Bureau APIs integration
- [x] Connect to transaction databases
- [ ] (Optional) Configure streaming ingestion for real-time risk scoring

### 1.2 Data Quality Validation
- [x] Implement missing value check
- [x] Add data type & schema validation
- [x] Build outlier detection mechanism
- [x] Handle duplicate records

### 1.3 Data Cleansing & Transformation
- [x] Implement missing field imputation logic
- [x] Standardize income & amount formats
- [x] Normalize categorical values (employment type, loan purpose)

### 1.4 Feature Engineering
- [x] Calculate Financial Ratios: Debt-to-income, credit utilization
- [x] Extract Behavioral Features: Delayed payments, monthly spend stability
- [x] Compute Derived Metrics: Rolling 6-month delinquencies, volatility of account balance
- [x] Process Bureau Features: Number of past defaults, enquiry rate

### 1.5 Feature Encoding
- [x] Implement one-hot encoding for categorical variables
- [x] Apply WOE (Weight of Evidence) encoding for explainability
- [x] Set up target encoding with leakage prevention

### 1.6 Data Storage
- [x] Configure Data Lake for raw and refined datasets
- [x] Set up Data Warehouse for curated, aggregated tables

---

## 2. Data Science Modeling

### 2.1 Model Development
- [x] Implement LightGBM model for credit risk prediction
- [x] Configure 80/20 train/validate split

### 2.2 Model Evaluation
- [x] Implement AUC-ROC metric calculation
- [x] Implement KS statistic calculation
- [x] Validate model meets target: AUC ≥ 0.80
- [x] Validate model meets target: KS ≥ 30

### 2.3 Model Calibration (Optional)
- [x] Evaluate need for CalibratedClassifierCV
- [x] Implement calibration if required

---

## 3. Dashboard Visualization

### 3.1 Portfolio Risk Overview
- [x] Create histogram of predicted risk scores

### 3.2 Model Performance
- [x] Display AUC & KS values

### 3.3 Insights
- [x] Build insight bar chart for feature importance

### 3.4 Fairness Check
- [x] Implement comparison of average risk score by gender
- [x] Add bias detection metrics

---

## 4. Monitoring & Compliance

- [x] Set up real-time loan portfolio risk monitoring dashboards
- [x] Ensure regulatory compliance for fairness and bias mitigation
- [x] Implement transparent, fair, and explainable credit decisions

---

## 5. Documentation & Deployment

- [x] Document project details in README.md
- [x] Push codebase to GitHub
- [x] Create API documentation for model inference
- [x] Set up CI/CD pipeline

---

## Data Sources Reference

| Source | Data Points |
|--------|-------------|
| Loan Application Data | Applicant demographics, Employment details, Declared income, Loan amount, tenure |
| Transaction History | Bank account statements, Spends, inflows/outflows, Delinquency history, Outstanding loans |
| Credit Bureau Reports | Credit score, Past loan performance, Enquiries, Credit utilization ratio |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| AUC-ROC | ≥ 0.80 |
| KS Statistic | ≥ 30 |

---

*Last Updated: February 3, 2026*
