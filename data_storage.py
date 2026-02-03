"""
Credit Risk Scoring - Data Storage Management
Implements:
- Data Lake with multiple zones (raw, refined, curated)
- Data Warehouse with aggregated tables
- ETL processes for data movement
- Metadata management
"""

import os
import json
import shutil
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataLakeManager:
    """
    Manages Data Lake with medallion architecture:
    - Bronze Layer: Raw data
    - Silver Layer: Cleaned/Refined data
    - Gold Layer: Feature-engineered data
    """
    
    def __init__(self, base_path: str = 'data_lake'):
        """Initialize Data Lake structure"""
        self.base_path = Path(base_path)
        self.layers = {
            'bronze': self.base_path / 'bronze',  # Raw data
            'silver': self.base_path / 'silver',  # Refined data
            'gold': self.base_path / 'gold',      # Curated data
            'metadata': self.base_path / 'metadata'  # Metadata
        }
        
    def setup_data_lake(self) -> Dict:
        """Create Data Lake directory structure"""
        print("="*80)
        print("DATA LAKE SETUP")
        print("="*80)
        
        setup_report = {
            'created_dirs': [],
            'existing_dirs': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for layer_name, layer_path in self.layers.items():
            if layer_path.exists():
                setup_report['existing_dirs'].append(str(layer_path))
                print(f"✓ {layer_name.upper()} layer already exists: {layer_path}")
            else:
                layer_path.mkdir(parents=True, exist_ok=True)
                setup_report['created_dirs'].append(str(layer_path))
                print(f"✓ Created {layer_name.upper()} layer: {layer_path}")
        
        # Create metadata file
        metadata_file = self.layers['metadata'] / 'lake_metadata.json'
        if not metadata_file.exists():
            metadata = {
                'created_at': datetime.now().isoformat(),
                'structure': {
                    'bronze': 'Raw, unprocessed data from source systems',
                    'silver': 'Cleaned and validated data',
                    'gold': 'Feature-engineered, analysis-ready data'
                },
                'datasets': {}
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"✓ Created metadata file: {metadata_file}")
        
        print("="*80)
        return setup_report
    
    def ingest_to_bronze(self, source_files: Dict[str, str]) -> Dict:
        """
        Ingest raw data files to Bronze layer
        Args:
            source_files: Dict of {dataset_name: source_file_path}
        """
        print("\n" + "="*80)
        print("INGESTING DATA TO BRONZE LAYER")
        print("="*80)
        
        ingestion_report = {
            'ingested': [],
            'failed': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for dataset_name, source_path in source_files.items():
            try:
                source_file = Path(source_path)
                if not source_file.exists():
                    print(f"✗ Source file not found: {source_path}")
                    ingestion_report['failed'].append({
                        'dataset': dataset_name,
                        'reason': 'File not found'
                    })
                    continue
                
                # Create timestamped bronze copy
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                bronze_file = self.layers['bronze'] / f"{dataset_name}_{timestamp}.csv"
                
                # Copy file
                shutil.copy2(source_file, bronze_file)
                
                # Get file stats
                df = pd.read_csv(bronze_file)
                stats = {
                    'dataset': dataset_name,
                    'bronze_path': str(bronze_file),
                    'records': len(df),
                    'columns': len(df.columns),
                    'size_mb': bronze_file.stat().st_size / (1024*1024)
                }
                
                ingestion_report['ingested'].append(stats)
                print(f"✓ Ingested {dataset_name}: {stats['records']} records, "
                      f"{stats['columns']} columns, {stats['size_mb']:.2f} MB")
                
            except Exception as e:
                print(f"✗ Failed to ingest {dataset_name}: {str(e)}")
                ingestion_report['failed'].append({
                    'dataset': dataset_name,
                    'reason': str(e)
                })
        
        print("="*80)
        return ingestion_report
    
    def promote_to_silver(self, bronze_file: str, dataset_name: str) -> str:
        """
        Promote cleaned/validated data to Silver layer
        """
        source_path = Path(bronze_file)
        if not source_path.exists():
            source_path = self.layers['bronze'] / bronze_file
        
        silver_file = self.layers['silver'] / f"{dataset_name}_refined.csv"
        
        # Copy to silver
        shutil.copy2(source_path, silver_file)
        
        print(f"✓ Promoted to SILVER: {dataset_name} -> {silver_file}")
        return str(silver_file)
    
    def promote_to_gold(self, silver_file: str, dataset_name: str) -> str:
        """
        Promote feature-engineered data to Gold layer
        """
        source_path = Path(silver_file)
        if not source_path.exists():
            source_path = self.layers['silver'] / silver_file
        
        gold_file = self.layers['gold'] / f"{dataset_name}_curated.csv"
        
        # Copy to gold
        shutil.copy2(source_path, gold_file)
        
        print(f"✓ Promoted to GOLD: {dataset_name} -> {gold_file}")
        return str(gold_file)
    
    def get_latest_file(self, layer: str, dataset_pattern: str) -> Optional[Path]:
        """Get latest file matching pattern in a layer"""
        layer_path = self.layers.get(layer)
        if not layer_path or not layer_path.exists():
            return None
        
        matching_files = list(layer_path.glob(f"{dataset_pattern}*.csv"))
        if not matching_files:
            return None
        
        # Return most recent file
        return max(matching_files, key=lambda p: p.stat().st_mtime)
    
    def list_datasets(self) -> Dict:
        """List all datasets in each layer"""
        inventory = {}
        
        for layer_name, layer_path in self.layers.items():
            if layer_name == 'metadata':
                continue
            
            if layer_path.exists():
                files = list(layer_path.glob('*.csv'))
                inventory[layer_name] = [
                    {
                        'filename': f.name,
                        'size_mb': f.stat().st_size / (1024*1024),
                        'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    }
                    for f in files
                ]
            else:
                inventory[layer_name] = []
        
        return inventory


class DataWarehouseManager:
    """
    Manages Data Warehouse with dimensional model
    - Fact tables: Loan applications, transactions
    - Dimension tables: Applicants, time, geography
    - Aggregate tables: Summary statistics, KPIs
    """
    
    def __init__(self, db_path: str = 'data_warehouse/credit_risk_dw.db'):
        """Initialize Data Warehouse"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    def setup_data_warehouse(self) -> Dict:
        """Create Data Warehouse schema"""
        print("\n" + "="*80)
        print("DATA WAREHOUSE SETUP")
        print("="*80)
        
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        setup_report = {
            'created_tables': [],
            'existing_tables': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Define schema
        schemas = self._get_warehouse_schema()
        
        for table_name, schema_sql in schemas.items():
            if table_name in existing_tables:
                setup_report['existing_tables'].append(table_name)
                print(f"✓ Table already exists: {table_name}")
            else:
                cursor.execute(schema_sql)
                setup_report['created_tables'].append(table_name)
                print(f"✓ Created table: {table_name}")
        
        self.conn.commit()
        print("="*80)
        return setup_report
    
    def _get_warehouse_schema(self) -> Dict[str, str]:
        """Define Data Warehouse schema"""
        return {
            # Dimension Tables
            'dim_applicant': """
                CREATE TABLE dim_applicant (
                    applicant_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_id TEXT UNIQUE NOT NULL,
                    gender TEXT,
                    age INTEGER,
                    education TEXT,
                    marital_status TEXT,
                    dependents INTEGER,
                    residence_type TEXT,
                    years_at_residence INTEGER,
                    city TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'dim_employment': """
                CREATE TABLE dim_employment (
                    employment_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_id TEXT NOT NULL,
                    employment_type TEXT,
                    industry TEXT,
                    annual_income REAL,
                    years_employed INTEGER,
                    years_with_current_employer INTEGER,
                    income_stability_score REAL,
                    effective_date DATE,
                    FOREIGN KEY (applicant_id) REFERENCES dim_applicant(applicant_id)
                )
            """,
            
            'dim_time': """
                CREATE TABLE dim_time (
                    time_key INTEGER PRIMARY KEY,
                    date DATE UNIQUE NOT NULL,
                    year INTEGER,
                    quarter INTEGER,
                    month INTEGER,
                    month_name TEXT,
                    day INTEGER,
                    day_of_week INTEGER,
                    day_name TEXT,
                    is_weekend INTEGER
                )
            """,
            
            # Fact Tables
            'fact_loan_application': """
                CREATE TABLE fact_loan_application (
                    application_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_key INTEGER,
                    time_key INTEGER,
                    applicant_id TEXT,
                    application_date DATE,
                    loan_purpose TEXT,
                    loan_amount_requested REAL,
                    loan_tenure_months INTEGER,
                    interest_rate REAL,
                    estimated_monthly_emi REAL,
                    
                    -- Financial Metrics
                    annual_income REAL,
                    total_outstanding_debt REAL,
                    debt_to_income_ratio REAL,
                    loan_to_income_ratio REAL,
                    emi_to_income_ratio REAL,
                    financial_burden_score REAL,
                    
                    -- Credit Bureau
                    credit_score INTEGER,
                    num_credit_accounts INTEGER,
                    credit_history_months INTEGER,
                    num_delinquent_accounts INTEGER,
                    total_past_defaults INTEGER,
                    bureau_default_probability REAL,
                    
                    -- Behavioral
                    payment_delinquency_score REAL,
                    financial_discipline_score REAL,
                    has_payment_delays INTEGER,
                    severe_delinquency_flag INTEGER,
                    
                    -- Target
                    default_flag INTEGER,
                    default_probability REAL,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (applicant_key) REFERENCES dim_applicant(applicant_key),
                    FOREIGN KEY (time_key) REFERENCES dim_time(time_key)
                )
            """,
            
            'fact_credit_bureau': """
                CREATE TABLE fact_credit_bureau (
                    bureau_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_id TEXT,
                    snapshot_date DATE,
                    credit_score INTEGER,
                    num_credit_accounts INTEGER,
                    num_active_accounts INTEGER,
                    credit_history_months INTEGER,
                    num_delinquent_accounts INTEGER,
                    max_dpd_last_12m INTEGER,
                    num_enquiries_6m INTEGER,
                    num_enquiries_12m INTEGER,
                    total_outstanding_debt REAL,
                    num_written_off_accounts INTEGER,
                    num_settled_accounts INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            # Aggregate Tables
            'agg_risk_summary': """
                CREATE TABLE agg_risk_summary (
                    summary_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_date DATE,
                    risk_category TEXT,
                    total_applications INTEGER,
                    total_loan_amount REAL,
                    avg_credit_score REAL,
                    avg_dti_ratio REAL,
                    default_rate REAL,
                    avg_bureau_default_prob REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'agg_monthly_portfolio': """
                CREATE TABLE agg_monthly_portfolio (
                    portfolio_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    year_month TEXT,
                    total_applications INTEGER,
                    total_approved_amount REAL,
                    avg_loan_amount REAL,
                    avg_interest_rate REAL,
                    high_risk_count INTEGER,
                    medium_risk_count INTEGER,
                    low_risk_count INTEGER,
                    portfolio_default_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
    
    def load_dimensions(self, df: pd.DataFrame) -> Dict:
        """Load dimension tables from source data"""
        print("\n" + "="*80)
        print("LOADING DIMENSION TABLES")
        print("="*80)
        
        load_report = {
            'loaded_tables': {},
            'timestamp': datetime.now().isoformat()
        }
        
        cursor = self.conn.cursor()
        
        # 1. Load dim_applicant
        dim_applicant = df[[
            'applicant_id', 'gender', 'age', 'education', 'marital_status',
            'dependents', 'residence_type', 'years_at_current_residence', 'city'
        ]].drop_duplicates('applicant_id')
        
        for _, row in dim_applicant.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO dim_applicant 
                (applicant_id, gender, age, education, marital_status, dependents,
                 residence_type, years_at_residence, city)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row))
        
        load_report['loaded_tables']['dim_applicant'] = len(dim_applicant)
        print(f"✓ Loaded dim_applicant: {len(dim_applicant)} records")
        
        # 2. Load dim_employment
        dim_employment = df[[
            'applicant_id', 'employment_type', 'industry', 'annual_income',
            'years_employed', 'years_with_current_employer', 'application_date'
        ]].copy()
        
        if 'income_stability_score' in df.columns:
            dim_employment['income_stability_score'] = df['income_stability_score']
        else:
            dim_employment['income_stability_score'] = None
        
        for _, row in dim_employment.iterrows():
            cursor.execute("""
                INSERT INTO dim_employment
                (applicant_id, employment_type, industry, annual_income,
                 years_employed, years_with_current_employer, income_stability_score,
                 effective_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['applicant_id'], row['employment_type'], row['industry'],
                row['annual_income'], row['years_employed'],
                row['years_with_current_employer'], row['income_stability_score'],
                row['application_date']
            ))
        
        load_report['loaded_tables']['dim_employment'] = len(dim_employment)
        print(f"✓ Loaded dim_employment: {len(dim_employment)} records")
        
        # 3. Load dim_time
        if 'application_date' in df.columns:
            dates = pd.to_datetime(df['application_date']).drop_duplicates()
            
            for date in dates:
                time_key = int(date.strftime('%Y%m%d'))
                cursor.execute("""
                    INSERT OR IGNORE INTO dim_time
                    (time_key, date, year, quarter, month, month_name,
                     day, day_of_week, day_name, is_weekend)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time_key, date.date(), date.year, (date.month-1)//3 + 1,
                    date.month, date.strftime('%B'), date.day,
                    date.dayofweek, date.strftime('%A'),
                    1 if date.dayofweek >= 5 else 0
                ))
            
            load_report['loaded_tables']['dim_time'] = len(dates)
            print(f"✓ Loaded dim_time: {len(dates)} records")
        
        self.conn.commit()
        print("="*80)
        return load_report
    
    def load_facts(self, df: pd.DataFrame) -> Dict:
        """Load fact tables from source data"""
        print("\n" + "="*80)
        print("LOADING FACT TABLES")
        print("="*80)
        
        load_report = {
            'loaded_tables': {},
            'timestamp': datetime.now().isoformat()
        }
        
        cursor = self.conn.cursor()
        
        # Load fact_loan_application
        fact_cols = [
            'applicant_id', 'application_date', 'loan_purpose',
            'loan_amount_requested', 'loan_tenure_months', 'interest_rate',
            'annual_income', 'total_outstanding_debt', 'credit_score',
            'num_credit_accounts', 'credit_history_months', 'num_delinquent_accounts'
        ]
        
        # Add optional columns if they exist
        optional_cols = [
            'estimated_monthly_emi', 'debt_to_income_ratio', 'loan_to_income_ratio',
            'emi_to_income_ratio', 'financial_burden_score', 'total_past_defaults',
            'bureau_default_probability', 'payment_delinquency_score',
            'financial_discipline_score', 'has_payment_delays',
            'severe_delinquency_flag', 'default', 'default_probability'
        ]
        
        available_cols = [col for col in fact_cols + optional_cols if col in df.columns]
        fact_df = df[available_cols].copy()
        
        for _, row in fact_df.iterrows():
            # Get dimension keys
            cursor.execute(
                "SELECT applicant_key FROM dim_applicant WHERE applicant_id = ?",
                (row['applicant_id'],)
            )
            applicant_key = cursor.fetchone()
            applicant_key = applicant_key[0] if applicant_key else None
            
            app_date = pd.to_datetime(row['application_date'])
            time_key = int(app_date.strftime('%Y%m%d'))
            
            # Insert fact record
            cursor.execute("""
                INSERT INTO fact_loan_application
                (applicant_key, time_key, applicant_id, application_date,
                 loan_purpose, loan_amount_requested, loan_tenure_months, interest_rate,
                 estimated_monthly_emi, annual_income, total_outstanding_debt,
                 debt_to_income_ratio, loan_to_income_ratio, emi_to_income_ratio,
                 financial_burden_score, credit_score, num_credit_accounts,
                 credit_history_months, num_delinquent_accounts, total_past_defaults,
                 bureau_default_probability, payment_delinquency_score,
                 financial_discipline_score, has_payment_delays, severe_delinquency_flag,
                 default_flag, default_probability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                applicant_key, time_key, row['applicant_id'], row['application_date'],
                row.get('loan_purpose'), row.get('loan_amount_requested'),
                row.get('loan_tenure_months'), row.get('interest_rate'),
                row.get('estimated_monthly_emi'), row.get('annual_income'),
                row.get('total_outstanding_debt'), row.get('debt_to_income_ratio'),
                row.get('loan_to_income_ratio'), row.get('emi_to_income_ratio'),
                row.get('financial_burden_score'), row.get('credit_score'),
                row.get('num_credit_accounts'), row.get('credit_history_months'),
                row.get('num_delinquent_accounts'), row.get('total_past_defaults'),
                row.get('bureau_default_probability'), row.get('payment_delinquency_score'),
                row.get('financial_discipline_score'), row.get('has_payment_delays'),
                row.get('severe_delinquency_flag'), row.get('default'),
                row.get('default_probability')
            ))
        
        load_report['loaded_tables']['fact_loan_application'] = len(fact_df)
        print(f"✓ Loaded fact_loan_application: {len(fact_df)} records")
        
        self.conn.commit()
        print("="*80)
        return load_report
    
    def build_aggregates(self) -> Dict:
        """Build aggregate tables for reporting"""
        print("\n" + "="*80)
        print("BUILDING AGGREGATE TABLES")
        print("="*80)
        
        cursor = self.conn.cursor()
        
        # 1. Risk Summary by Category
        cursor.execute("""
            INSERT INTO agg_risk_summary (summary_date, risk_category, total_applications,
                                         total_loan_amount, avg_credit_score, avg_dti_ratio,
                                         default_rate, avg_bureau_default_prob)
            SELECT 
                DATE('now') as summary_date,
                CASE 
                    WHEN credit_score < 650 THEN 'High Risk'
                    WHEN credit_score < 750 THEN 'Medium Risk'
                    ELSE 'Low Risk'
                END as risk_category,
                COUNT(*) as total_applications,
                SUM(loan_amount_requested) as total_loan_amount,
                AVG(credit_score) as avg_credit_score,
                AVG(debt_to_income_ratio) as avg_dti_ratio,
                AVG(CAST(default_flag AS FLOAT)) as default_rate,
                AVG(bureau_default_probability) as avg_bureau_default_prob
            FROM fact_loan_application
            GROUP BY risk_category
        """)
        
        risk_summary_count = cursor.rowcount
        print(f"✓ Built agg_risk_summary: {risk_summary_count} categories")
        
        # 2. Monthly Portfolio Summary
        cursor.execute("""
            INSERT INTO agg_monthly_portfolio (year_month, total_applications,
                                              total_approved_amount, avg_loan_amount,
                                              avg_interest_rate, high_risk_count,
                                              medium_risk_count, low_risk_count,
                                              portfolio_default_rate)
            SELECT 
                strftime('%Y-%m', application_date) as year_month,
                COUNT(*) as total_applications,
                SUM(loan_amount_requested) as total_approved_amount,
                AVG(loan_amount_requested) as avg_loan_amount,
                AVG(interest_rate) as avg_interest_rate,
                SUM(CASE WHEN credit_score < 650 THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN credit_score >= 650 AND credit_score < 750 THEN 1 ELSE 0 END) as medium_risk_count,
                SUM(CASE WHEN credit_score >= 750 THEN 1 ELSE 0 END) as low_risk_count,
                AVG(CAST(default_flag AS FLOAT)) as portfolio_default_rate
            FROM fact_loan_application
            GROUP BY year_month
        """)
        
        monthly_count = cursor.rowcount
        print(f"✓ Built agg_monthly_portfolio: {monthly_count} months")
        
        self.conn.commit()
        print("="*80)
        
        return {
            'agg_risk_summary': risk_summary_count,
            'agg_monthly_portfolio': monthly_count
        }
    
    def get_table_stats(self) -> pd.DataFrame:
        """Get statistics for all warehouse tables"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        stats = []
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats.append({'table_name': table, 'record_count': count})
        
        return pd.DataFrame(stats)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Execute complete data storage setup"""
    
    print("="*80)
    print("CREDIT RISK SCORING - DATA STORAGE SETUP")
    print("="*80)
    
    # 1. Setup Data Lake
    print("\n### PHASE 1: DATA LAKE CONFIGURATION ###\n")
    lake_manager = DataLakeManager()
    lake_setup = lake_manager.setup_data_lake()
    
    # 2. Ingest raw data to Bronze layer
    source_files = {
        'credit_risk_raw': 'data/credit_risk_dataset.csv',
        'core_banking': 'data/core_banking_data.csv',
        'bureau': 'data/bureau_data.csv',
        'transactions': 'data/transaction_data.csv'
    }
    
    ingestion_report = lake_manager.ingest_to_bronze(source_files)
    
    # 3. Promote cleaned data to Silver
    print("\n### PROMOTING TO SILVER LAYER ###")
    if Path('data/credit_risk_dataset_cleaned.csv').exists():
        lake_manager.promote_to_silver(
            'data/credit_risk_dataset_cleaned.csv',
            'credit_risk_cleaned'
        )
    
    # 4. Promote feature-engineered data to Gold
    print("\n### PROMOTING TO GOLD LAYER ###")
    if Path('data/credit_risk_dataset_features.csv').exists():
        lake_manager.promote_to_gold(
            'data/credit_risk_dataset_features.csv',
            'credit_risk_features'
        )
    
    # 5. Setup Data Warehouse
    print("\n### PHASE 2: DATA WAREHOUSE CONFIGURATION ###\n")
    dw_manager = DataWarehouseManager()
    dw_setup = dw_manager.setup_data_warehouse()
    
    # 6. Load data into warehouse
    print("\n### LOADING DATA INTO WAREHOUSE ###")
    df = pd.read_csv('data/credit_risk_dataset_features.csv')
    
    dim_report = dw_manager.load_dimensions(df)
    fact_report = dw_manager.load_facts(df)
    agg_report = dw_manager.build_aggregates()
    
    # 7. Generate statistics
    print("\n### DATA WAREHOUSE STATISTICS ###")
    stats_df = dw_manager.get_table_stats()
    print(stats_df.to_string(index=False))
    
    # 8. List Data Lake inventory
    print("\n### DATA LAKE INVENTORY ###")
    inventory = lake_manager.list_datasets()
    for layer, files in inventory.items():
        print(f"\n{layer.upper()} Layer:")
        if files:
            for file_info in files:
                print(f"  • {file_info['filename']}: {file_info['size_mb']:.2f} MB")
        else:
            print("  (empty)")
    
    # Cleanup
    dw_manager.close()
    
    print("\n" + "="*80)
    print("✓ DATA STORAGE SETUP COMPLETE")
    print("="*80)
    print(f"\nData Lake: {lake_manager.base_path}/")
    print(f"Data Warehouse: {dw_manager.db_path}")
    print("="*80)
    
    return {
        'lake_setup': lake_setup,
        'ingestion': ingestion_report,
        'dw_setup': dw_setup,
        'dimensions': dim_report,
        'facts': fact_report,
        'aggregates': agg_report
    }


if __name__ == "__main__":
    result = main()
