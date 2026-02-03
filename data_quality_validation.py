"""
Credit Risk Scoring - Data Quality Validation Module
Implements comprehensive data quality checks including:
- Missing value detection
- Data type & schema validation
- Outlier detection
- Duplicate record handling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class ValidationResult:
    """Store validation results"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    report: Dict


class DataQualityValidator:
    """Comprehensive data quality validation for credit risk dataset"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize validator with configuration"""
        self.config = config or self._get_default_config()
        self.validation_results = {}
        
    def _get_default_config(self) -> Dict:
        """Define default validation configuration and expected schema"""
        return {
            'schema': {
                'applicant_id': {'dtype': 'object', 'nullable': False, 'unique': True},
                'application_date': {'dtype': 'datetime64[ns]', 'nullable': False},
                'gender': {'dtype': 'object', 'nullable': False, 'allowed_values': ['Male', 'Female']},
                'age': {'dtype': 'int64', 'nullable': False, 'min': 18, 'max': 100},
                'education': {'dtype': 'object', 'nullable': False},
                'marital_status': {'dtype': 'object', 'nullable': False},
                'dependents': {'dtype': 'int64', 'nullable': False, 'min': 0, 'max': 10},
                'residence_type': {'dtype': 'object', 'nullable': False},
                'years_at_current_residence': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'city': {'dtype': 'object', 'nullable': False},
                'employment_type': {'dtype': 'object', 'nullable': False},
                'industry': {'dtype': 'object', 'nullable': False},
                'annual_income': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'years_employed': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'years_with_current_employer': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'loan_purpose': {'dtype': 'object', 'nullable': False},
                'loan_amount_requested': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'loan_tenure_months': {'dtype': 'int64', 'nullable': False, 'min': 1},
                'interest_rate': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'credit_score': {'dtype': 'int64', 'nullable': False, 'min': 300, 'max': 900},
                'num_credit_accounts': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'num_active_accounts': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'credit_history_months': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'num_delinquent_accounts': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'max_dpd_last_12m': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'num_enquiries_6m': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'num_enquiries_12m': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'total_outstanding_debt': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'secured_loan_percentage': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'num_written_off_accounts': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'num_settled_accounts': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'avg_monthly_balance': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'balance_volatility': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'avg_monthly_spending': {'dtype': 'float64', 'nullable': False, 'min': 0},
                'essential_spending_pct': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'discretionary_spending_pct': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'num_bounced_checks_12m': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'salary_credit_regularity': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'num_digital_txns_monthly': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'cash_withdrawal_pct': {'dtype': 'float64', 'nullable': False, 'min': 0, 'max': 100},
                'min_balance_breaches_12m': {'dtype': 'int64', 'nullable': False, 'min': 0},
                'emi_bounce_count_12m': {'dtype': 'int64', 'nullable': False, 'min': 0},
            },
            'outlier_detection': {
                'method': 'iqr',  # 'iqr' or 'zscore'
                'iqr_multiplier': 3.0,  # More lenient than standard 1.5
                'zscore_threshold': 4.0,  # More lenient than standard 3.0
            },
            'duplicate_handling': {
                'subset': ['applicant_id'],  # Columns to check for duplicates
                'keep': 'first'  # Which duplicate to keep
            }
        }
    
    def validate_all(self, df: pd.DataFrame) -> ValidationResult:
        """Run all validation checks"""
        errors = []
        warnings = []
        report = {}
        
        print("="*70)
        print("DATA QUALITY VALIDATION REPORT")
        print("="*70)
        print(f"\nDataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # 1. Check for missing values
        print("\n" + "-"*70)
        print("1. MISSING VALUE CHECK")
        print("-"*70)
        missing_result = self.check_missing_values(df)
        report['missing_values'] = missing_result
        
        if missing_result['total_missing'] > 0:
            warnings.append(f"Found {missing_result['total_missing']} missing values")
        
        # 2. Schema & Data Type Validation
        print("\n" + "-"*70)
        print("2. SCHEMA & DATA TYPE VALIDATION")
        print("-"*70)
        schema_result = self.validate_schema(df)
        report['schema_validation'] = schema_result
        
        if schema_result['errors']:
            errors.extend(schema_result['errors'])
        if schema_result['warnings']:
            warnings.extend(schema_result['warnings'])
        
        # 3. Outlier Detection
        print("\n" + "-"*70)
        print("3. OUTLIER DETECTION")
        print("-"*70)
        outlier_result = self.detect_outliers(df)
        report['outlier_detection'] = outlier_result
        
        if outlier_result['total_outliers'] > 0:
            warnings.append(f"Found {outlier_result['total_outliers']} potential outliers")
        
        # 4. Duplicate Records
        print("\n" + "-"*70)
        print("4. DUPLICATE RECORD CHECK")
        print("-"*70)
        duplicate_result = self.check_duplicates(df)
        report['duplicate_check'] = duplicate_result
        
        if duplicate_result['num_duplicates'] > 0:
            errors.append(f"Found {duplicate_result['num_duplicates']} duplicate records")
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        is_valid = len(errors) == 0
        
        if is_valid:
            print("✓ Data quality validation PASSED")
        else:
            print("✗ Data quality validation FAILED")
        
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
        
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
        
        print("="*70)
        
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, report=report)
    
    def check_missing_values(self, df: pd.DataFrame) -> Dict:
        """Check for missing values in dataset"""
        missing_stats = pd.DataFrame({
            'column': df.columns,
            'missing_count': df.isnull().sum(),
            'missing_pct': (df.isnull().sum() / len(df) * 100).round(2)
        })
        
        missing_stats = missing_stats[missing_stats['missing_count'] > 0].sort_values(
            'missing_count', ascending=False
        )
        
        total_missing = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        overall_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        
        print(f"Total Missing Values: {total_missing} ({overall_pct:.2f}% of all cells)")
        
        if len(missing_stats) > 0:
            print("\nColumns with Missing Values:")
            print(missing_stats.to_string(index=False))
        else:
            print("✓ No missing values found")
        
        return {
            'total_missing': int(total_missing),
            'overall_pct': float(overall_pct),
            'missing_by_column': missing_stats.to_dict('records') if len(missing_stats) > 0 else []
        }
    
    def validate_schema(self, df: pd.DataFrame) -> Dict:
        """Validate data types and schema constraints"""
        errors = []
        warnings = []
        validation_details = []
        
        schema = self.config.get('schema', {})
        
        # Check for missing columns
        expected_cols = set(schema.keys())
        actual_cols = set(df.columns)
        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols
        
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        if extra_cols:
            warnings.append(f"Extra columns not in schema: {extra_cols}")
        
        # Validate each column
        for col, constraints in schema.items():
            if col not in df.columns:
                continue
            
            detail = {'column': col, 'status': 'valid', 'issues': []}
            
            # Check data type
            expected_dtype = constraints.get('dtype')
            actual_dtype = str(df[col].dtype)
            
            # Convert datetime if needed
            if expected_dtype == 'datetime64[ns]' and actual_dtype != 'datetime64[ns]':
                try:
                    df[col] = pd.to_datetime(df[col])
                    actual_dtype = 'datetime64[ns]'
                except:
                    detail['issues'].append(f"Cannot convert to datetime")
                    detail['status'] = 'error'
            
            if expected_dtype and not actual_dtype.startswith(expected_dtype.split('[')[0]):
                detail['issues'].append(f"Type mismatch: expected {expected_dtype}, got {actual_dtype}")
                detail['status'] = 'warning'
            
            # Check nullable constraint
            if not constraints.get('nullable', True):
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    detail['issues'].append(f"Found {null_count} null values (not allowed)")
                    detail['status'] = 'error'
            
            # Check unique constraint
            if constraints.get('unique', False):
                dup_count = df[col].duplicated().sum()
                if dup_count > 0:
                    detail['issues'].append(f"Found {dup_count} duplicate values (should be unique)")
                    detail['status'] = 'error'
            
            # Check allowed values
            if 'allowed_values' in constraints:
                invalid_values = set(df[col].dropna().unique()) - set(constraints['allowed_values'])
                if invalid_values:
                    detail['issues'].append(f"Invalid values: {invalid_values}")
                    detail['status'] = 'error'
            
            # Check numeric ranges
            if pd.api.types.is_numeric_dtype(df[col]):
                if 'min' in constraints:
                    below_min = (df[col] < constraints['min']).sum()
                    if below_min > 0:
                        detail['issues'].append(f"{below_min} values below minimum ({constraints['min']})")
                        detail['status'] = 'error'
                
                if 'max' in constraints:
                    above_max = (df[col] > constraints['max']).sum()
                    if above_max > 0:
                        detail['issues'].append(f"{above_max} values above maximum ({constraints['max']})")
                        detail['status'] = 'error'
            
            if detail['status'] == 'error':
                errors.append(f"{col}: {'; '.join(detail['issues'])}")
            elif detail['status'] == 'warning':
                warnings.append(f"{col}: {'; '.join(detail['issues'])}")
            
            validation_details.append(detail)
        
        # Print summary
        valid_cols = sum(1 for d in validation_details if d['status'] == 'valid')
        error_cols = sum(1 for d in validation_details if d['status'] == 'error')
        warning_cols = sum(1 for d in validation_details if d['status'] == 'warning')
        
        print(f"Validated Columns: {len(validation_details)}")
        print(f"  ✓ Valid: {valid_cols}")
        if warning_cols > 0:
            print(f"  ⚠ Warnings: {warning_cols}")
        if error_cols > 0:
            print(f"  ✗ Errors: {error_cols}")
        
        if error_cols > 0 or warning_cols > 0:
            print("\nIssues Found:")
            for detail in validation_details:
                if detail['status'] != 'valid':
                    symbol = '✗' if detail['status'] == 'error' else '⚠'
                    print(f"  {symbol} {detail['column']}: {'; '.join(detail['issues'])}")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'validation_details': validation_details,
            'valid_columns': valid_cols,
            'error_columns': error_cols,
            'warning_columns': warning_cols
        }
    
    def detect_outliers(self, df: pd.DataFrame, method: Optional[str] = None) -> Dict:
        """Detect outliers in numeric columns"""
        method = method or self.config['outlier_detection']['method']
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude ID-like columns and binary/categorical numerics
        exclude_cols = ['applicant_id', 'default']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        outlier_summary = []
        total_outliers = 0
        
        for col in numeric_cols:
            if method == 'iqr':
                outliers = self._detect_outliers_iqr(df[col])
            else:  # zscore
                outliers = self._detect_outliers_zscore(df[col])
            
            num_outliers = outliers.sum()
            if num_outliers > 0:
                total_outliers += num_outliers
                pct = (num_outliers / len(df) * 100)
                outlier_summary.append({
                    'column': col,
                    'num_outliers': int(num_outliers),
                    'pct_outliers': round(pct, 2),
                    'min_value': float(df[col].min()),
                    'max_value': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median())
                })
        
        print(f"Method: {method.upper()}")
        print(f"Total Outliers Detected: {total_outliers}")
        print(f"Columns Analyzed: {len(numeric_cols)}")
        
        if outlier_summary:
            print(f"\nColumns with Outliers (showing top 10):")
            outlier_df = pd.DataFrame(outlier_summary).sort_values('num_outliers', ascending=False).head(10)
            print(outlier_df.to_string(index=False))
        else:
            print("✓ No significant outliers detected")
        
        return {
            'method': method,
            'total_outliers': total_outliers,
            'columns_analyzed': len(numeric_cols),
            'outlier_summary': outlier_summary
        }
    
    def _detect_outliers_iqr(self, series: pd.Series) -> pd.Series:
        """Detect outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        multiplier = self.config['outlier_detection']['iqr_multiplier']
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        return (series < lower_bound) | (series > upper_bound)
    
    def _detect_outliers_zscore(self, series: pd.Series) -> pd.Series:
        """Detect outliers using Z-score method"""
        threshold = self.config['outlier_detection']['zscore_threshold']
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    def check_duplicates(self, df: pd.DataFrame) -> Dict:
        """Check for duplicate records"""
        subset = self.config['duplicate_handling'].get('subset')
        
        # Check complete duplicates
        complete_dups = df.duplicated(keep=False).sum()
        
        # Check duplicates on subset
        if subset:
            subset_dups = df.duplicated(subset=subset, keep=False).sum()
            duplicate_rows = df[df.duplicated(subset=subset, keep=False)]
        else:
            subset_dups = 0
            duplicate_rows = pd.DataFrame()
        
        print(f"Complete Duplicate Rows: {complete_dups}")
        if subset:
            print(f"Duplicates on {subset}: {subset_dups}")
        
        if subset_dups > 0:
            print(f"\nSample Duplicate Records (showing first 5):")
            sample_dups = duplicate_rows.head(10)[subset + ['gender', 'age', 'loan_amount_requested']]
            print(sample_dups.to_string(index=False))
        else:
            print("✓ No duplicate records found")
        
        return {
            'num_duplicates': int(subset_dups if subset else complete_dups),
            'complete_duplicates': int(complete_dups),
            'subset_duplicates': int(subset_dups) if subset else None,
            'duplicate_subset': subset,
            'duplicate_records': duplicate_rows.to_dict('records') if len(duplicate_rows) > 0 else []
        }
    
    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Apply data cleaning based on validation results"""
        cleaning_report = {}
        df_cleaned = df.copy()
        
        print("\n" + "="*70)
        print("DATA CLEANING")
        print("="*70)
        
        # 1. Handle duplicates
        subset = self.config['duplicate_handling'].get('subset')
        keep = self.config['duplicate_handling'].get('keep', 'first')
        
        initial_rows = len(df_cleaned)
        if subset:
            df_cleaned = df_cleaned.drop_duplicates(subset=subset, keep=keep)
        else:
            df_cleaned = df_cleaned.drop_duplicates(keep=keep)
        
        duplicates_removed = initial_rows - len(df_cleaned)
        cleaning_report['duplicates_removed'] = duplicates_removed
        print(f"\n1. Removed {duplicates_removed} duplicate records")
        
        # 2. Convert data types
        schema = self.config.get('schema', {})
        type_conversions = 0
        for col, constraints in schema.items():
            if col in df_cleaned.columns:
                expected_dtype = constraints.get('dtype')
                if expected_dtype == 'datetime64[ns]' and df_cleaned[col].dtype != 'datetime64[ns]':
                    try:
                        df_cleaned[col] = pd.to_datetime(df_cleaned[col])
                        type_conversions += 1
                    except:
                        pass
        
        cleaning_report['type_conversions'] = type_conversions
        print(f"2. Converted {type_conversions} columns to correct data types")
        
        # 3. Optionally handle outliers (capping)
        # Note: For credit risk, outliers may be legitimate, so we just report but don't remove
        print(f"3. Outliers preserved (may be legitimate for credit risk modeling)")
        
        print(f"\nCleaned Dataset Shape: {df_cleaned.shape[0]} rows × {df_cleaned.shape[1]} columns")
        print("="*70)
        
        return df_cleaned, cleaning_report


def main():
    """Example usage of data quality validation"""
    
    # Load dataset
    print("Loading credit risk dataset...")
    df = pd.read_csv('data/credit_risk_dataset.csv')
    
    # Initialize validator
    validator = DataQualityValidator()
    
    # Run validation
    result = validator.validate_all(df)
    
    # Optional: Clean data
    if not result.is_valid or result.warnings:
        print("\nProceed with data cleaning? (y/n): ", end='')
        choice = input().lower()
        
        if choice == 'y':
            df_cleaned, cleaning_report = validator.clean_data(df)
            
            # Save cleaned data
            output_path = 'data/credit_risk_dataset_cleaned.csv'
            df_cleaned.to_csv(output_path, index=False)
            print(f"\n✓ Cleaned dataset saved to: {output_path}")
    
    return result


if __name__ == "__main__":
    result = main()
