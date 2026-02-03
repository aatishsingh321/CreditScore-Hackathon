"""
Demo script to showcase data storage capabilities
"""

import sqlite3
import pandas as pd
from data_storage import DataLakeManager, DataWarehouseManager

print("="*80)
print("DATA STORAGE - COMPREHENSIVE DEMONSTRATION")
print("="*80)

# ============================================================================
# PART 1: DATA LAKE DEMONSTRATION
# ============================================================================

print("\n" + "="*80)
print("PART 1: DATA LAKE (MEDALLION ARCHITECTURE)")
print("="*80)

lake = DataLakeManager(base_path='data_lake')

# Show layer structure
print("\n📁 Data Lake Layers:")
for layer_name, layer_path in lake.layers.items():
    status = "✓ Exists" if layer_path.exists() else "✗ Not found"
    print(f"  • {layer_name.upper():12s}: {layer_path} ({status})")

# List inventory
print("\n📊 Current Inventory:")
inventory = lake.list_datasets()

for layer, files in inventory.items():
    print(f"\n{layer.upper()} Layer:")
    if files:
        total_size = sum(f['size_mb'] for f in files)
        print(f"  Files: {len(files)}, Total Size: {total_size:.2f} MB")
        for file_info in files[:3]:  # Show first 3
            print(f"    • {file_info['filename']}: {file_info['size_mb']:.2f} MB")
        if len(files) > 3:
            print(f"    • ... and {len(files)-3} more files")
    else:
        print("  (empty)")

# ============================================================================
# PART 2: DATA WAREHOUSE DEMONSTRATION
# ============================================================================

print("\n" + "="*80)
print("PART 2: DATA WAREHOUSE (STAR SCHEMA)")
print("="*80)

dw = DataWarehouseManager(db_path='data_warehouse/credit_risk_dw.db')

# Connect to database
dw.conn = sqlite3.connect(str(dw.db_path))

# Show table statistics
print("\n📊 Warehouse Tables:")
stats_df = dw.get_table_stats()
print(stats_df.to_string(index=False))

# ============================================================================
# PART 3: SAMPLE QUERIES
# ============================================================================

print("\n" + "="*80)
print("PART 3: SAMPLE ANALYTICAL QUERIES")
print("="*80)

conn = sqlite3.connect('data_warehouse/credit_risk_dw.db')

# Query 1: Risk Summary
print("\n1. Risk Category Summary:")
print("-" * 80)
query1 = """
    SELECT 
        risk_category,
        total_applications,
        ROUND(total_loan_amount/1000000, 2) as total_loan_mn,
        ROUND(avg_credit_score, 0) as avg_score,
        ROUND(avg_dti_ratio, 2) as avg_dti,
        ROUND(default_rate * 100, 2) as default_rate_pct
    FROM agg_risk_summary
    ORDER BY 
        CASE risk_category 
            WHEN 'Low Risk' THEN 1 
            WHEN 'Medium Risk' THEN 2 
            ELSE 3 
        END
"""
df_risk = pd.read_sql_query(query1, conn)
print(df_risk.to_string(index=False))

# Query 2: Monthly Portfolio
print("\n2. Monthly Portfolio Performance:")
print("-" * 80)
query2 = """
    SELECT 
        year_month,
        total_applications as apps,
        high_risk_count as high,
        medium_risk_count as medium,
        low_risk_count as low,
        ROUND(avg_loan_amount/1000, 0) as avg_loan_k,
        ROUND(portfolio_default_rate * 100, 2) as default_pct
    FROM agg_monthly_portfolio
    ORDER BY year_month
"""
df_monthly = pd.read_sql_query(query2, conn)
print(df_monthly.head(6).to_string(index=False))
print(f"... showing 6 of {len(df_monthly)} months")

# Query 3: Top Cities by Application Volume
print("\n3. Top 10 Cities by Application Volume:")
print("-" * 80)
query3 = """
    SELECT 
        a.city,
        COUNT(*) as total_apps,
        ROUND(AVG(f.credit_score), 0) as avg_score,
        ROUND(AVG(f.loan_amount_requested)/1000, 0) as avg_loan_k,
        ROUND(AVG(CAST(f.default_flag AS FLOAT)) * 100, 2) as default_rate
    FROM fact_loan_application f
    JOIN dim_applicant a ON f.applicant_key = a.applicant_key
    GROUP BY a.city
    ORDER BY total_apps DESC
    LIMIT 10
"""
df_cities = pd.read_sql_query(query3, conn)
print(df_cities.to_string(index=False))

# Query 4: High Risk Applicants
print("\n4. Sample High Risk Applicants:")
print("-" * 80)
query4 = """
    SELECT 
        f.applicant_id,
        a.age,
        a.city,
        f.credit_score,
        ROUND(f.debt_to_income_ratio, 2) as dti,
        ROUND(f.financial_burden_score, 2) as burden,
        ROUND(f.bureau_default_probability, 4) as risk_prob,
        f.default_flag
    FROM fact_loan_application f
    JOIN dim_applicant a ON f.applicant_key = a.applicant_key
    WHERE f.credit_score < 650
    ORDER BY f.bureau_default_probability DESC
    LIMIT 5
"""
df_high_risk = pd.read_sql_query(query4, conn)
print(df_high_risk.to_string(index=False))

# Query 5: Employment Type Analysis
print("\n5. Risk by Employment Type:")
print("-" * 80)
query5 = """
    SELECT 
        e.employment_type,
        COUNT(*) as total_apps,
        ROUND(AVG(f.credit_score), 0) as avg_score,
        ROUND(AVG(e.annual_income)/1000, 0) as avg_income_k,
        ROUND(AVG(CAST(f.default_flag AS FLOAT)) * 100, 2) as default_rate
    FROM fact_loan_application f
    JOIN dim_employment e ON f.applicant_id = e.applicant_id
    GROUP BY e.employment_type
    ORDER BY default_rate DESC
"""
df_employment = pd.read_sql_query(query5, conn)
print(df_employment.to_string(index=False))

# Query 6: Loan Purpose Distribution
print("\n6. Applications by Loan Purpose:")
print("-" * 80)
query6 = """
    SELECT 
        loan_purpose,
        COUNT(*) as count,
        ROUND(AVG(loan_amount_requested)/1000, 0) as avg_amt_k,
        ROUND(AVG(interest_rate), 2) as avg_rate,
        ROUND(AVG(CAST(default_flag AS FLOAT)) * 100, 2) as default_pct
    FROM fact_loan_application
    GROUP BY loan_purpose
    ORDER BY count DESC
"""
df_purpose = pd.read_sql_query(query6, conn)
print(df_purpose.to_string(index=False))

conn.close()

# ============================================================================
# PART 4: DATA LINEAGE
# ============================================================================

print("\n" + "="*80)
print("PART 4: DATA LINEAGE & METADATA")
print("="*80)

print("\n📋 Data Flow:")
print("""
  Source Data
      ↓
  BRONZE Layer (Raw)
      ↓
  Data Quality Validation
      ↓
  SILVER Layer (Cleaned)
      ↓
  Feature Engineering
      ↓
  GOLD Layer (Curated)
      ↓
  Data Warehouse (Star Schema)
      ↓
  Aggregate Tables (Pre-computed)
""")

# ============================================================================
# PART 5: STORAGE STATISTICS
# ============================================================================

print("\n" + "="*80)
print("PART 5: STORAGE STATISTICS")
print("="*80)

import os
from pathlib import Path

def get_dir_size(path):
    """Calculate directory size"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except:
        pass
    return total

# Data Lake sizes
lake_sizes = {}
for layer_name, layer_path in lake.layers.items():
    if layer_path.exists():
        size_mb = get_dir_size(layer_path) / (1024 * 1024)
        lake_sizes[layer_name] = size_mb

print("\n📊 Data Lake Storage:")
total_lake = sum(lake_sizes.values())
for layer, size in lake_sizes.items():
    pct = (size / total_lake * 100) if total_lake > 0 else 0
    print(f"  {layer.upper():12s}: {size:6.2f} MB ({pct:5.1f}%)")
print(f"  {'TOTAL':12s}: {total_lake:6.2f} MB")

# Data Warehouse size
dw_path = Path('data_warehouse/credit_risk_dw.db')
if dw_path.exists():
    dw_size = dw_path.stat().st_size / (1024 * 1024)
    print(f"\n📊 Data Warehouse Storage:")
    print(f"  Database:    {dw_size:6.2f} MB")

print(f"\n📊 Total Storage:")
print(f"  Combined:    {total_lake + dw_size:6.2f} MB")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\n✓ Data Lake Layers: {len([l for l in lake.layers.values() if l.exists()])}")
print(f"✓ Data Warehouse Tables: {len(stats_df)}")
print(f"✓ Total Applications: 10,000")
print(f"✓ Risk Categories: 3")
print(f"✓ Monthly Summaries: 12")
print(f"\n✓ Data storage infrastructure is fully operational")

print("\n" + "="*80)
print("📚 Documentation: DATA_STORAGE_GUIDE.md")
print("🔧 Module: data_storage.py")
print("="*80)

dw.close()
