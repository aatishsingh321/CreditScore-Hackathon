# Data Storage Architecture Guide

## Overview
This guide describes the complete data storage solution implemented for the Credit Risk Scoring System, including both Data Lake and Data Warehouse components.

---

## 🏗️ Architecture

### Data Lake (Medallion Architecture)

The Data Lake follows the **Medallion Architecture** with three layers:

```
data_lake/
├── bronze/          # Raw, unprocessed data
├── silver/          # Cleaned and validated data
├── gold/            # Feature-engineered, analysis-ready data
└── metadata/        # Metadata and catalog information
```

#### Layer Descriptions

| Layer | Purpose | Data Quality | Use Case |
|-------|---------|--------------|----------|
| **Bronze** | Raw data ingestion | As-is from source | Data backup, reprocessing |
| **Silver** | Cleaned & validated | Quality-checked | Analytics, reporting |
| **Gold** | Feature-engineered | Model-ready | Machine learning, advanced analytics |

---

### Data Warehouse (Dimensional Model)

The Data Warehouse uses a **Star Schema** with fact and dimension tables:

```
data_warehouse/
└── credit_risk_dw.db (SQLite)
    ├── Dimension Tables
    │   ├── dim_applicant       (Applicant demographics)
    │   ├── dim_employment      (Employment history)
    │   └── dim_time           (Date dimension)
    ├── Fact Tables
    │   ├── fact_loan_application  (Loan applications)
    │   └── fact_credit_bureau     (Credit bureau snapshots)
    └── Aggregate Tables
        ├── agg_risk_summary       (Risk category summaries)
        └── agg_monthly_portfolio  (Monthly portfolio stats)
```

---

## 📊 Schema Details

### Dimension Tables

#### dim_applicant
Stores applicant demographic information.

| Column | Type | Description |
|--------|------|-------------|
| applicant_key | INTEGER PK | Surrogate key |
| applicant_id | TEXT | Business key |
| gender | TEXT | Male/Female |
| age | INTEGER | Age in years |
| education | TEXT | Education level |
| marital_status | TEXT | Marital status |
| dependents | INTEGER | Number of dependents |
| residence_type | TEXT | Owned/Rented/etc |
| years_at_residence | INTEGER | Years at current address |
| city | TEXT | City of residence |

#### dim_employment
Tracks employment and income information (Type 2 SCD - historical tracking).

| Column | Type | Description |
|--------|------|-------------|
| employment_key | INTEGER PK | Surrogate key |
| applicant_id | TEXT | Foreign key to applicant |
| employment_type | TEXT | Salaried/Self-Employed/etc |
| industry | TEXT | Industry sector |
| annual_income | REAL | Annual income |
| years_employed | INTEGER | Total years employed |
| years_with_current_employer | INTEGER | Years with current employer |
| income_stability_score | REAL | Stability metric (0-1) |
| effective_date | DATE | Record effective date |

#### dim_time
Standard time dimension for temporal analysis.

| Column | Type | Description |
|--------|------|-------------|
| time_key | INTEGER PK | YYYYMMDD format |
| date | DATE | Calendar date |
| year | INTEGER | Year |
| quarter | INTEGER | Quarter (1-4) |
| month | INTEGER | Month (1-12) |
| day | INTEGER | Day of month |
| day_of_week | INTEGER | Day of week (0-6) |
| is_weekend | INTEGER | Weekend flag (0/1) |

---

### Fact Tables

#### fact_loan_application
Central fact table for loan applications with key metrics.

**Dimensions:**
- applicant_key → dim_applicant
- time_key → dim_time

**Measures:**
- Financial: loan_amount, income, DTI, EMI ratios
- Credit: credit_score, delinquencies, bureau scores
- Behavioral: payment scores, discipline scores
- Target: default_flag, default_probability

**Row Count:** 10,000 (one per application)

#### fact_credit_bureau
Stores credit bureau snapshots over time.

**Measures:**
- Credit score, account counts
- Delinquency history
- Enquiry rates
- Outstanding debt

**Row Count:** Can grow with periodic snapshots

---

### Aggregate Tables

#### agg_risk_summary
Pre-aggregated risk category statistics.

| Column | Type | Description |
|--------|------|-------------|
| risk_category | TEXT | High/Medium/Low Risk |
| total_applications | INTEGER | Count of applications |
| total_loan_amount | REAL | Sum of loan amounts |
| avg_credit_score | REAL | Average credit score |
| avg_dti_ratio | REAL | Average DTI |
| default_rate | REAL | Default rate (0-1) |
| avg_bureau_default_prob | REAL | Avg bureau probability |

**Current Stats:**
```
High Risk:   2,317 applications (credit_score < 650)
Medium Risk: 4,964 applications (650-749)
Low Risk:    2,719 applications (750+)
```

#### agg_monthly_portfolio
Monthly portfolio performance metrics.

| Column | Type | Description |
|--------|------|-------------|
| year_month | TEXT | YYYY-MM format |
| total_applications | INTEGER | Monthly applications |
| total_approved_amount | REAL | Total loan amount |
| avg_loan_amount | REAL | Average loan size |
| avg_interest_rate | REAL | Average rate |
| high_risk_count | INTEGER | High risk count |
| medium_risk_count | INTEGER | Medium risk count |
| low_risk_count | INTEGER | Low risk count |
| portfolio_default_rate | REAL | Monthly default rate |

**Coverage:** 12 months (2025 data)

---

## 🔧 Implementation

### Data Lake Operations

#### 1. Setup Data Lake
```python
from data_storage import DataLakeManager

lake = DataLakeManager(base_path='data_lake')
lake.setup_data_lake()
```

#### 2. Ingest to Bronze Layer
```python
source_files = {
    'credit_risk_raw': 'data/credit_risk_dataset.csv',
    'core_banking': 'data/core_banking_data.csv',
    'bureau': 'data/bureau_data.csv'
}

report = lake.ingest_to_bronze(source_files)
```

#### 3. Promote Through Layers
```python
# To Silver (cleaned data)
lake.promote_to_silver('source.csv', 'dataset_name')

# To Gold (feature-engineered data)
lake.promote_to_gold('source.csv', 'dataset_name')
```

#### 4. List Inventory
```python
inventory = lake.list_datasets()
for layer, files in inventory.items():
    print(f"{layer}: {len(files)} files")
```

---

### Data Warehouse Operations

#### 1. Setup Data Warehouse
```python
from data_storage import DataWarehouseManager

dw = DataWarehouseManager(db_path='data_warehouse/credit_risk_dw.db')
dw.setup_data_warehouse()
```

#### 2. Load Dimensions
```python
import pandas as pd

df = pd.read_csv('data/credit_risk_dataset_features.csv')
dw.load_dimensions(df)
```

#### 3. Load Facts
```python
dw.load_facts(df)
```

#### 4. Build Aggregates
```python
dw.build_aggregates()
```

#### 5. Query Data
```python
import sqlite3

conn = sqlite3.connect('data_warehouse/credit_risk_dw.db')

# Example: Get risk summary
query = "SELECT * FROM agg_risk_summary"
df_risk = pd.read_sql_query(query, conn)

conn.close()
```

---

## 📈 Sample Queries

### Risk Analysis
```sql
-- Applications by risk category
SELECT 
    risk_category,
    total_applications,
    total_loan_amount,
    ROUND(avg_credit_score, 2) as avg_score,
    ROUND(default_rate * 100, 2) as default_rate_pct
FROM agg_risk_summary
ORDER BY 
    CASE risk_category 
        WHEN 'Low Risk' THEN 1 
        WHEN 'Medium Risk' THEN 2 
        ELSE 3 
    END;
```

### Monthly Trends
```sql
-- Monthly portfolio trends
SELECT 
    year_month,
    total_applications,
    ROUND(avg_loan_amount, 0) as avg_loan,
    high_risk_count + medium_risk_count + low_risk_count as total_apps,
    ROUND(portfolio_default_rate * 100, 2) as default_rate_pct
FROM agg_monthly_portfolio
ORDER BY year_month;
```

### Top Risk Applicants
```sql
-- High risk applications
SELECT 
    f.applicant_id,
    a.age,
    a.city,
    f.credit_score,
    ROUND(f.debt_to_income_ratio, 2) as dti,
    ROUND(f.bureau_default_probability, 4) as default_prob,
    f.default_flag
FROM fact_loan_application f
JOIN dim_applicant a ON f.applicant_key = a.applicant_key
WHERE f.credit_score < 650
ORDER BY f.bureau_default_probability DESC
LIMIT 10;
```

### Geographic Distribution
```sql
-- Applications by city
SELECT 
    a.city,
    COUNT(*) as total_apps,
    ROUND(AVG(f.credit_score), 0) as avg_credit_score,
    ROUND(AVG(f.loan_amount_requested), 0) as avg_loan_amount,
    ROUND(AVG(CAST(f.default_flag AS FLOAT)) * 100, 2) as default_rate_pct
FROM fact_loan_application f
JOIN dim_applicant a ON f.applicant_key = a.applicant_key
GROUP BY a.city
HAVING COUNT(*) > 100
ORDER BY default_rate_pct DESC;
```

---

## 🔄 Data Flow

### ETL Pipeline

```
Source Systems
     ↓
┌─────────────────┐
│ Data Ingestion  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ BRONZE Layer    │  ← Raw data
│ (Data Lake)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Data Quality    │
│ Validation      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ SILVER Layer    │  ← Cleaned data
│ (Data Lake)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Feature         │
│ Engineering     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ GOLD Layer      │  ← Curated data
│ (Data Lake)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Data Warehouse  │  ← Star schema
│ Load            │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Aggregate       │
│ Tables          │
└─────────────────┘
```

---

## 📊 Current Storage Stats

### Data Lake

| Layer | Files | Total Size | Description |
|-------|-------|------------|-------------|
| Bronze | 4 | 4.98 MB | Raw source files |
| Silver | 1 | 5.53 MB | Cleaned dataset |
| Gold | 1 | 5.30 MB | Feature-engineered dataset |

### Data Warehouse

| Table | Records | Type | Purpose |
|-------|---------|------|---------|
| dim_applicant | 10,000 | Dimension | Applicant demographics |
| dim_employment | 10,000 | Dimension | Employment history |
| dim_time | 365 | Dimension | Date dimension |
| fact_loan_application | 10,000 | Fact | Loan applications |
| fact_credit_bureau | 0 | Fact | Bureau snapshots |
| agg_risk_summary | 3 | Aggregate | Risk categories |
| agg_monthly_portfolio | 12 | Aggregate | Monthly stats |

**Total Size:** 3.4 MB (SQLite database)

---

## 🎯 Best Practices

### Data Lake

1. **Immutability**: Bronze layer files are never modified
2. **Timestamping**: All bronze files have timestamps
3. **Metadata**: Maintain catalog in metadata layer
4. **Partitioning**: Consider partitioning by date for large datasets
5. **Compression**: Use Parquet or compressed CSV for large files

### Data Warehouse

1. **Surrogate Keys**: Use auto-increment keys for dimensions
2. **Indexing**: Index foreign keys and frequently queried columns
3. **Aggregates**: Pre-compute common aggregations
4. **Type 2 SCD**: Track historical changes in dimensions
5. **Incremental Loads**: Use upsert patterns for updates

---

## 🔍 Troubleshooting

### Common Issues

**1. "Table already exists" error**
```python
# Drop and recreate if needed
dw.conn.execute("DROP TABLE IF EXISTS table_name")
dw.setup_data_warehouse()
```

**2. Large file handling**
```python
# Use chunked reading for large files
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process_chunk(chunk)
```

**3. Database locked**
```python
# Close connections properly
dw.close()
```

---

## 🚀 Performance Optimization

### Data Lake

- **Partitioning**: Organize by date/category
- **Compression**: Use gzip or snappy compression
- **File Format**: Parquet > CSV for large data
- **Metadata**: Maintain a catalog for quick discovery

### Data Warehouse

- **Indexing**:
```sql
CREATE INDEX idx_applicant_id ON fact_loan_application(applicant_id);
CREATE INDEX idx_time_key ON fact_loan_application(time_key);
CREATE INDEX idx_credit_score ON fact_loan_application(credit_score);
```

- **Query Optimization**:
```sql
-- Use aggregates instead of facts for reporting
SELECT * FROM agg_risk_summary;  -- Fast
-- vs
SELECT ..., COUNT(*) FROM fact_loan_application GROUP BY ...;  -- Slow
```

---

## 📦 Storage Requirements

### Current

- Data Lake: ~16 MB
- Data Warehouse: 3.4 MB
- Total: ~20 MB

### Projected (100K records)

- Data Lake: ~160 MB
- Data Warehouse: ~34 MB
- Total: ~200 MB

### Scalability

- Can handle 1M+ records with current architecture
- Consider PostgreSQL/MySQL for 10M+ records
- Consider distributed storage (S3, HDFS) for 100M+ records

---

## 🔐 Security & Governance

### Access Control

```python
# Implement role-based access
roles = {
    'analyst': ['SELECT'],
    'engineer': ['SELECT', 'INSERT', 'UPDATE'],
    'admin': ['ALL']
}
```

### Data Lineage

```json
{
  "dataset": "gold/credit_risk_features_curated.csv",
  "source": "silver/credit_risk_cleaned_refined.csv",
  "transformations": [
    "feature_engineering",
    "data_quality_validation"
  ],
  "created_at": "2026-02-03T22:32:00Z"
}
```

### Audit Logging

```sql
CREATE TABLE audit_log (
    log_id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    user_id TEXT,
    action TEXT,
    table_name TEXT,
    record_id TEXT
);
```

---

## 🔄 Maintenance

### Regular Tasks

**Daily:**
- Ingest new data to Bronze
- Validate and promote to Silver
- Update fact tables

**Weekly:**
- Rebuild aggregates
- Optimize database (VACUUM)
- Review storage usage

**Monthly:**
- Archive old Bronze files
- Review and optimize queries
- Update documentation

---

## 📞 Module Reference

**Main Module:** `data_storage.py`

**Classes:**
- `DataLakeManager`: Manages data lake operations
- `DataWarehouseManager`: Manages data warehouse operations

**Key Methods:**
- `setup_data_lake()`: Initialize lake structure
- `ingest_to_bronze()`: Ingest raw data
- `promote_to_silver()`: Move to silver layer
- `promote_to_gold()`: Move to gold layer
- `setup_data_warehouse()`: Create DW schema
- `load_dimensions()`: Load dimension tables
- `load_facts()`: Load fact tables
- `build_aggregates()`: Create aggregate tables

---

*Last Updated: February 3, 2026*
*Version: 1.0*
