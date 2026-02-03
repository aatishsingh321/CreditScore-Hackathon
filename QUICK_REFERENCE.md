# Data Quality Validation - Quick Reference

## 🎯 Quick Start

```bash
# Run validation
python data_quality_validation.py

# Run demo
python demo_validation.py
```

## 📚 API Reference

### Initialize Validator
```python
from data_quality_validation import DataQualityValidator
validator = DataQualityValidator()
```

### Run All Validations
```python
result = validator.validate_all(df)
# Returns: ValidationResult(is_valid, errors, warnings, report)
```

### Individual Checks

#### 1. Missing Values
```python
missing_report = validator.check_missing_values(df)
# Returns: {'total_missing': int, 'overall_pct': float, 'missing_by_column': list}
```

#### 2. Schema Validation
```python
schema_report = validator.validate_schema(df)
# Returns: {'errors': list, 'warnings': list, 'validation_details': list}
```

#### 3. Outlier Detection
```python
outlier_report = validator.detect_outliers(df, method='iqr')  # or 'zscore'
# Returns: {'total_outliers': int, 'outlier_summary': list}
```

#### 4. Duplicate Check
```python
duplicate_report = validator.check_duplicates(df)
# Returns: {'num_duplicates': int, 'duplicate_records': list}
```

### Clean Data
```python
df_clean, report = validator.clean_data(df)
# Returns: (cleaned_df, {'duplicates_removed': int, 'type_conversions': int})
```

## ⚙️ Configuration

```python
config = {
    'schema': {
        'column_name': {
            'dtype': 'int64',           # Expected data type
            'nullable': False,          # Allow nulls?
            'unique': True,             # Must be unique?
            'min': 0,                   # Minimum value (numeric)
            'max': 100,                 # Maximum value (numeric)
            'allowed_values': ['A','B'] # Valid categories
        }
    },
    'outlier_detection': {
        'method': 'iqr',               # 'iqr' or 'zscore'
        'iqr_multiplier': 3.0,         # IQR threshold
        'zscore_threshold': 4.0        # Z-score threshold
    },
    'duplicate_handling': {
        'subset': ['id_col'],          # Columns to check
        'keep': 'first'                # 'first', 'last', or False
    }
}

validator = DataQualityValidator(config)
```

## 📊 Output Structure

### ValidationResult
```python
{
    'is_valid': bool,
    'errors': ['error1', 'error2'],
    'warnings': ['warning1'],
    'report': {
        'missing_values': {...},
        'schema_validation': {...},
        'outlier_detection': {...},
        'duplicate_check': {...}
    }
}
```

## 🔧 Common Use Cases

### Case 1: Data Pipeline Integration
```python
def etl_pipeline(raw_data):
    df = pd.read_csv(raw_data)
    validator = DataQualityValidator()
    
    result = validator.validate_all(df)
    if not result.is_valid:
        raise ValueError(f"Validation failed: {result.errors}")
    
    df_clean, _ = validator.clean_data(df)
    return df_clean
```

### Case 2: Custom Validation Rules
```python
custom_config = {
    'schema': {
        'credit_score': {'dtype': 'int64', 'min': 300, 'max': 900},
        'age': {'dtype': 'int64', 'min': 18, 'max': 100}
    }
}
validator = DataQualityValidator(custom_config)
```

### Case 3: Outlier Investigation
```python
# Detect outliers
outliers = validator.detect_outliers(df, method='iqr')

# Inspect specific column
for item in outliers['outlier_summary']:
    if item['column'] == 'annual_income':
        print(f"Found {item['num_outliers']} outliers")
        print(f"Range: {item['min_value']} to {item['max_value']}")
```

## ✅ Feature Checklist

- [x] Missing value detection
- [x] Data type validation
- [x] Schema constraint checking
- [x] Outlier detection (IQR & Z-score)
- [x] Duplicate record handling
- [x] Automated data cleaning
- [x] Comprehensive reporting
- [x] Configurable validation rules

## 📁 Files

| File | Purpose |
|------|---------|
| `data_quality_validation.py` | Core module (21KB) |
| `DATA_QUALITY_GUIDE.md` | Full documentation (10KB) |
| `demo_validation.py` | Demo script (3KB) |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details (6KB) |
| `QUICK_REFERENCE.md` | This file |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Ensure pandas & numpy installed |
| "Too many outliers" | Adjust IQR multiplier to 4.0+ |
| "Type mismatch" | Check data loading, may need dtype specification |
| "Memory error" | Process data in chunks for large datasets |

## 📞 Documentation

- Full Guide: `DATA_QUALITY_GUIDE.md`
- Summary: `IMPLEMENTATION_SUMMARY.md`
- Demo: `python demo_validation.py`

---

*Last Updated: February 3, 2026*
