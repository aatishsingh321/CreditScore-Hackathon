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
- [ ] Implement missing field imputation logic
- [ ] Standardize income & amount formats
- [ ] Normalize categorical values (employment type, loan purpose)

### 1.4 Feature Engineering
- [ ] Calculate Financial Ratios: Debt-to-income, credit utilization
- [ ] Extract Behavioral Features: Delayed payments, monthly spend stability
- [ ] Compute Derived Metrics: Rolling 6-month delinquencies, volatility of account balance
- [ ] Process Bureau Features: Number of past defaults, enquiry rate

### 1.5 Feature Encoding
- [ ] Implement one-hot encoding for categorical variables
- [ ] Apply WOE (Weight of Evidence) encoding for explainability
- [ ] Set up target encoding with leakage prevention

### 1.6 Data Storage
- [ ] Configure Data Lake for raw and refined datasets
- [ ] Set up Data Warehouse for curated, aggregated tables

---

## 2. Data Science Modeling

### 2.1 Model Development
- [ ] Implement LightGBM model for credit risk prediction
- [ ] Configure 80/20 train/validate split

### 2.2 Model Evaluation
- [ ] Implement AUC-ROC metric calculation
- [ ] Implement KS statistic calculation
- [ ] Validate model meets target: AUC ≥ 0.80
- [ ] Validate model meets target: KS ≥ 30

### 2.3 Model Calibration (Optional)
- [ ] Evaluate need for CalibratedClassifierCV
- [ ] Implement calibration if required

---

## 3. Dashboard Visualization

### 3.1 Portfolio Risk Overview
- [ ] Create histogram of predicted risk scores

### 3.2 Model Performance
- [ ] Display AUC & KS values

### 3.3 Insights
- [ ] Build insight bar chart for feature importance

### 3.4 Fairness Check
- [ ] Implement comparison of average risk score by gender
- [ ] Add bias detection metrics

---

## 4. Monitoring & Compliance

- [ ] Set up real-time loan portfolio risk monitoring dashboards
- [ ] Ensure regulatory compliance for fairness and bias mitigation
- [ ] Implement transparent, fair, and explainable credit decisions

---

## 5. Documentation & Deployment

- [ ] Document project details in README.md
- [ ] Push codebase to GitHub
- [ ] Create API documentation for model inference
- [ ] Set up CI/CD pipeline

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
