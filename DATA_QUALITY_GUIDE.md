# Data Quality Validation Guide

## Overview
This guide describes the data quality validation framework implemented for the Credit Risk Scoring System.

## Features Implemented

### 1. Missing Value Check ✓
**Purpose**: Identify and report missing/null values across all dataset columns.

**Implementation**:
- Scans all columns for null/NaN values
- Calculates missing count and percentage per column
- Provides overall dataset completeness metrics

**Output**:
```
Total Missing Values: 0 (0.00% of all cells)
✓ No missing values found
```

**Usage**:
```python
from data_quality_validation import DataQualityValidator

validator = DataQualityValidator()
df = pd.read_csv('data/credit_risk_dataset.csv')
missing_report = validator.check_missing_values(df)
```

---

### 2. Data Type & Schema Validation ✓
**Purpose**: Ensure data conforms to expected schema and type constraints.

**Validation Rules**:
- **Data Types**: Validates expected dtype for each column (int64, float64, object, datetime64)
- **Nullability**: Enforces non-null constraints on critical fields
- **Uniqueness**: Checks for duplicate values in ID columns (e.g., applicant_id)
- **Allowed Values**: Validates categorical fields against allowed value lists
- **Range Constraints**: Enforces min/max bounds on numeric fields

**Schema Constraints**:
| Field | Type | Constraints |
|-------|------|-------------|
| applicant_id | object | Not null, Unique |
| age | int64 | Not null, 18-100 |
| credit_score | int64 | Not null, 300-900 |
| annual_income | float64 | Not null, >= 0 |
| interest_rate | float64 | Not null, 0-100 |
| gender | object | Not null, ['Male', 'Female'] |

**Output**:
```
Validated Columns: 42
  ✓ Valid: 42
  ⚠ Warnings: 0
  ✗ Errors: 0
```

**Usage**:
```python
schema_report = validator.validate_schema(df)
```

---

### 3. Outlier Detection Mechanism ✓
**Purpose**: Identify statistical outliers that may indicate data quality issues or rare cases.

**Methods Available**:

#### A. IQR (Interquartile Range) Method (Default)
- Calculates Q1 (25th percentile) and Q3 (75th percentile)
- Computes IQR = Q3 - Q1
- Flags values outside: [Q1 - 3*IQR, Q3 + 3*IQR]
- **More lenient** multiplier (3.0) suitable for financial data

#### B. Z-Score Method
- Calculates standard deviations from mean
- Flags values with |z-score| > 4.0
- **More lenient** threshold (4.0) for skewed distributions

**Configuration**:
```python
config = {
    'outlier_detection': {
        'method': 'iqr',  # or 'zscore'
        'iqr_multiplier': 3.0,
        'zscore_threshold': 4.0
    }
}
validator = DataQualityValidator(config)
```

**Output**:
```
Method: IQR
Total Outliers Detected: 5739
Columns Analyzed: 40

Columns with Outliers (showing top 10):
column                    num_outliers  pct_outliers
num_written_off_accounts  1486         14.86%
num_settled_accounts      1004         10.04%
interest_rate             540          5.40%
```

**Important Note**: For credit risk modeling, outliers often represent legitimate high-risk cases and should be carefully reviewed rather than automatically removed.

**Usage**:
```python
outlier_report = validator.detect_outliers(df, method='iqr')
```

---

### 4. Duplicate Record Handling ✓
**Purpose**: Detect and handle duplicate records based on key identifiers.

**Features**:
- Detects complete row duplicates
- Detects duplicates based on specific columns (e.g., applicant_id)
- Configurable duplicate handling strategy (keep first/last/none)

**Configuration**:
```python
config = {
    'duplicate_handling': {
        'subset': ['applicant_id'],  # Check these columns
        'keep': 'first'  # Keep first occurrence
    }
}
```

**Output**:
```
Complete Duplicate Rows: 0
Duplicates on ['applicant_id']: 0
✓ No duplicate records found
```

**Cleaning Action**:
The `clean_data()` method automatically removes duplicates based on configuration:
```python
df_cleaned, report = validator.clean_data(df)
# report['duplicates_removed'] = 0
```

**Usage**:
```python
duplicate_report = validator.check_duplicates(df)
```

---

## Complete Workflow

### 1. Run Full Validation
```python
from data_quality_validation import DataQualityValidator
import pandas as pd

# Load data
df = pd.read_csv('data/credit_risk_dataset.csv')

# Initialize validator
validator = DataQualityValidator()

# Run all validations
result = validator.validate_all(df)

# Check result
if result.is_valid:
    print("✓ All validations passed")
else:
    print("✗ Validation failed")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
```

### 2. Clean Data (If Needed)
```python
# Apply cleaning
df_cleaned, cleaning_report = validator.clean_data(df)

# Save cleaned data
df_cleaned.to_csv('data/credit_risk_dataset_cleaned.csv', index=False)

print(f"Removed {cleaning_report['duplicates_removed']} duplicates")
print(f"Converted {cleaning_report['type_conversions']} data types")
```

### 3. Custom Configuration
```python
custom_config = {
    'schema': {
        'applicant_id': {'dtype': 'object', 'nullable': False, 'unique': True},
        'age': {'dtype': 'int64', 'nullable': False, 'min': 18, 'max': 100},
        # ... more fields
    },
    'outlier_detection': {
        'method': 'zscore',
        'zscore_threshold': 3.5
    },
    'duplicate_handling': {
        'subset': ['applicant_id', 'application_date'],
        'keep': 'last'
    }
}

validator = DataQualityValidator(custom_config)
```

---

## CLI Usage

Run validation from command line:
```bash
cd /Users/apple/CreditScore-Hackathon
python data_quality_validation.py
```

This will:
1. Load the dataset
2. Run all 4 validation checks
3. Display comprehensive report
4. Optionally clean the data

---

## Validation Report Structure

The validation report contains:

```python
{
    'missing_values': {
        'total_missing': 0,
        'overall_pct': 0.0,
        'missing_by_column': []
    },
    'schema_validation': {
        'errors': [],
        'warnings': [],
        'valid_columns': 42,
        'error_columns': 0,
        'warning_columns': 0
    },
    'outlier_detection': {
        'method': 'iqr',
        'total_outliers': 5739,
        'columns_analyzed': 40,
        'outlier_summary': [...]
    },
    'duplicate_check': {
        'num_duplicates': 0,
        'complete_duplicates': 0,
        'subset_duplicates': 0
    }
}
```

---

## Best Practices

### 1. Missing Values
- **Critical fields** (IDs, dates): Zero tolerance
- **Numeric features**: Consider imputation strategies
- **Categorical features**: May need "Unknown" category
- **Target variable**: Must be complete

### 2. Outliers
- **Don't automatically remove**: May be legitimate high-risk cases
- **Investigate**: Check if outliers are data errors or valid extremes
- **Domain knowledge**: Use business rules to validate ranges
- **Document decisions**: Keep audit trail of outlier handling

### 3. Duplicates
- **Always check on primary key**: Prevents data integrity issues
- **Investigate cause**: System error vs. resubmissions
- **Keep strategy**: Business logic determines which to keep
- **Log removed records**: Maintain audit trail

### 4. Schema Validation
- **Update schema** as data evolves
- **Version control**: Track schema changes
- **Fail fast**: Catch type mismatches early in pipeline
- **Document exceptions**: Some fields may have valid range exceptions

---

## Integration with ETL Pipeline

```python
# In your ETL pipeline
def etl_with_validation(raw_data_path):
    # Load raw data
    df = pd.read_csv(raw_data_path)
    
    # Validate
    validator = DataQualityValidator()
    result = validator.validate_all(df)
    
    # Handle validation results
    if not result.is_valid:
        # Log errors
        logger.error(f"Data quality check failed: {result.errors}")
        
        # Send alerts
        send_alert(result.errors)
        
        # Optionally stop pipeline
        raise ValueError("Data quality validation failed")
    
    # Clean data
    df_cleaned, report = validator.clean_data(df)
    
    # Continue with feature engineering
    df_features = engineer_features(df_cleaned)
    
    return df_features
```

---

## Performance Considerations

- **Parallelization**: Validation checks are independent and can be parallelized
- **Sampling**: For very large datasets (>10M rows), consider sampling for outlier detection
- **Caching**: Schema validation can cache results for repeated runs
- **Memory**: Cleaned dataset is a copy; original is preserved

---

## Troubleshooting

### Common Issues

**1. Type Conversion Errors**
```
Issue: "Cannot convert to datetime"
Solution: Check date format, use pd.to_datetime with format parameter
```

**2. Too Many Outliers Detected**
```
Issue: Legitimate variation flagged as outliers
Solution: Adjust IQR multiplier (3.0 → 4.0) or use domain-specific ranges
```

**3. Schema Validation Fails**
```
Issue: Extra columns not in schema
Solution: Update schema config or filter columns before validation
```

**4. Memory Issues with Large Datasets**
```
Issue: Out of memory during validation
Solution: Process in chunks or use Dask for larger-than-memory datasets
```

---

## Testing

Run unit tests:
```bash
pytest tests/test_data_quality.py -v
```

---

## Future Enhancements

- [ ] Automated imputation strategies
- [ ] Time-series specific validations
- [ ] Cross-field validation rules (e.g., start_date < end_date)
- [ ] Integration with Great Expectations
- [ ] Real-time validation API
- [ ] Visualization dashboard for validation results
- [ ] Automated data profiling reports

---

## References

- [IQR Method for Outlier Detection](https://en.wikipedia.org/wiki/Interquartile_range)
- [Z-Score Method](https://en.wikipedia.org/wiki/Standard_score)
- [Pandas Data Validation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html)

---

*Last Updated: February 3, 2026*
