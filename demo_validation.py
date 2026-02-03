"""
Demo script to showcase all data quality validation features
"""

import pandas as pd
import numpy as np
from data_quality_validation import DataQualityValidator

print("="*80)
print("DATA QUALITY VALIDATION - FEATURE DEMONSTRATION")
print("="*80)

# Load dataset
print("\n📁 Loading dataset...")
df = pd.read_csv('data/credit_risk_dataset.csv')
print(f"   Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# Initialize validator
validator = DataQualityValidator()

print("\n" + "="*80)
print("FEATURE 1: MISSING VALUE CHECK")
print("="*80)
print("\n✓ Checking for missing/null values across all columns...")
missing_report = validator.check_missing_values(df)
print(f"\n📊 Result: {missing_report['total_missing']} missing values ({missing_report['overall_pct']:.2f}%)")

print("\n" + "="*80)
print("FEATURE 2: DATA TYPE & SCHEMA VALIDATION")
print("="*80)
print("\n✓ Validating data types and constraints...")
schema_report = validator.validate_schema(df)
print(f"\n📊 Result: {schema_report['valid_columns']} valid columns")
print(f"   Errors: {schema_report['error_columns']}")
print(f"   Warnings: {schema_report['warning_columns']}")

print("\n" + "="*80)
print("FEATURE 3: OUTLIER DETECTION")
print("="*80)
print("\n✓ Detecting outliers using IQR method...")
outlier_report = validator.detect_outliers(df, method='iqr')
print(f"\n📊 Result: {outlier_report['total_outliers']} outliers detected")
print(f"   Analyzed {outlier_report['columns_analyzed']} numeric columns")

print("\n" + "="*80)
print("FEATURE 4: DUPLICATE RECORD HANDLING")
print("="*80)
print("\n✓ Checking for duplicate records...")
duplicate_report = validator.check_duplicates(df)
print(f"\n📊 Result: {duplicate_report['num_duplicates']} duplicates found")
print(f"   Complete duplicates: {duplicate_report['complete_duplicates']}")

print("\n" + "="*80)
print("DEMONSTRATION: CREATING DATA WITH ISSUES")
print("="*80)

# Create a test dataset with known issues
print("\n🧪 Creating test dataset with intentional data quality issues...")
df_test = df.head(100).copy()

# 1. Introduce missing values
df_test.loc[0:5, 'annual_income'] = np.nan
df_test.loc[10:15, 'credit_score'] = np.nan
print("   ✓ Added 12 missing values")

# 2. Introduce duplicates
df_test = pd.concat([df_test, df_test.iloc[0:3]], ignore_index=True)
print("   ✓ Added 3 duplicate records")

# 3. Introduce schema violations
df_test.loc[20, 'age'] = 150  # Age too high
df_test.loc[21, 'credit_score'] = 1000  # Credit score too high
print("   ✓ Added 2 schema violations")

print("\n" + "="*80)
print("VALIDATING TEST DATASET WITH ISSUES")
print("="*80)

result = validator.validate_all(df_test)

print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"\n✓ All 4 data quality validation features have been implemented:")
print("  1. ✓ Missing Value Check - Identifies null/missing values")
print("  2. ✓ Data Type & Schema Validation - Validates types and constraints")
print("  3. ✓ Outlier Detection - Detects statistical anomalies")
print("  4. ✓ Duplicate Record Handling - Finds and removes duplicates")

print(f"\n📚 Documentation: See DATA_QUALITY_GUIDE.md for detailed usage")
print(f"🔧 Module: data_quality_validation.py")
print(f"✅ Status: All TODO items completed")

print("\n" + "="*80)
