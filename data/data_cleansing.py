"""
Credit Risk Scoring - Data Cleansing & Transformation
Implements:
- Missing field imputation logic
- Income & amount standardization
- Categorical value normalization
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import warnings
warnings.filterwarnings('ignore')


class DataCleanser:
    """Data cleansing and transformation pipeline for credit risk data"""
    
    def __init__(self):
        self.numerical_imputer = None
        self.categorical_imputer = None
        self.income_scaler = None
        self.amount_scaler = None
        self.categorical_mappings = {}
        
    # =========================================================================
    # 1. MISSING FIELD IMPUTATION
    # =========================================================================
    
    def analyze_missing_values(self, df):
        """Analyze and report missing values in the dataset"""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'column': missing.index,
            'missing_count': missing.values,
            'missing_pct': missing_pct.values
        })
        missing_df = missing_df[missing_df['missing_count'] > 0].sort_values(
            'missing_pct', ascending=False
        )
        
        print("=" * 60)
        print("MISSING VALUE ANALYSIS")
        print("=" * 60)
        
        if len(missing_df) == 0:
            print("No missing values found in the dataset!")
        else:
            print(f"\nColumns with missing values: {len(missing_df)}")
            print(missing_df.to_string(index=False))
            
        return missing_df
    
    def impute_numerical_features(self, df, strategy='median', columns=None):
        """
        Impute missing values in numerical columns
        
        Strategies:
        - 'mean': Replace with column mean
        - 'median': Replace with column median (robust to outliers)
        - 'knn': Use K-Nearest Neighbors for imputation
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target columns from imputation
        columns = [c for c in columns if c not in ['default', 'default_probability']]
        
        print(f"\nImputing {len(columns)} numerical columns using '{strategy}' strategy...")
        
        if strategy in ['mean', 'median']:
            self.numerical_imputer = SimpleImputer(strategy=strategy)
        elif strategy == 'knn':
            self.numerical_imputer = KNNImputer(n_neighbors=5)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        df[columns] = self.numerical_imputer.fit_transform(df[columns])
        
        return df
    
    def impute_categorical_features(self, df, strategy='most_frequent', columns=None):
        """
        Impute missing values in categorical columns
        
        Strategies:
        - 'most_frequent': Replace with mode
        - 'constant': Replace with 'Unknown'
        """
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove ID and date columns
        columns = [c for c in columns if c not in ['applicant_id', 'application_date']]
        
        print(f"\nImputing {len(columns)} categorical columns using '{strategy}' strategy...")
        
        if strategy == 'most_frequent':
            self.categorical_imputer = SimpleImputer(strategy='most_frequent')
        elif strategy == 'constant':
            self.categorical_imputer = SimpleImputer(strategy='constant', fill_value='Unknown')
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        df[columns] = self.categorical_imputer.fit_transform(df[columns])
        
        return df
    
    def impute_by_group(self, df, target_col, group_cols, strategy='median'):
        """
        Impute missing values based on group statistics
        E.g., impute income based on employment_type and industry
        """
        print(f"\nImputing '{target_col}' by groups: {group_cols}")
        
        if strategy == 'median':
            group_stats = df.groupby(group_cols)[target_col].transform('median')
        elif strategy == 'mean':
            group_stats = df.groupby(group_cols)[target_col].transform('mean')
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Fill missing with group statistic, then overall median for remaining
        df[target_col] = df[target_col].fillna(group_stats)
        df[target_col] = df[target_col].fillna(df[target_col].median())
        
        return df
    
    # =========================================================================
    # 2. INCOME & AMOUNT STANDARDIZATION
    # =========================================================================
    
    def standardize_income_formats(self, df):
        """
        Standardize income-related columns:
        - Convert to consistent currency format (INR)
        - Round to nearest thousand
        - Create standardized (z-score) and normalized (0-1) versions
        """
        print("\n" + "=" * 60)
        print("INCOME STANDARDIZATION")
        print("=" * 60)
        
        income_cols = ['annual_income', 'avg_monthly_balance', 'avg_monthly_spending']
        
        for col in income_cols:
            if col in df.columns:
                # Round to nearest thousand
                df[col] = df[col].round(-3)
                
                # Ensure no negative values
                df[col] = df[col].clip(lower=0)
                
                print(f"\n{col}:")
                print(f"  Range: {df[col].min():,.0f} - {df[col].max():,.0f}")
                print(f"  Mean: {df[col].mean():,.0f}")
                print(f"  Median: {df[col].median():,.0f}")
        
        # Create standardized versions (z-score normalization)
        self.income_scaler = StandardScaler()
        income_cols_present = [c for c in income_cols if c in df.columns]
        
        standardized_cols = [f'{c}_standardized' for c in income_cols_present]
        df[standardized_cols] = self.income_scaler.fit_transform(df[income_cols_present])
        
        print(f"\nCreated standardized columns: {standardized_cols}")
        
        return df
    
    def standardize_amount_formats(self, df):
        """
        Standardize loan and debt amount columns:
        - Round appropriately
        - Create log-transformed versions for skewed distributions
        - Create normalized (0-1) versions
        """
        print("\n" + "=" * 60)
        print("AMOUNT STANDARDIZATION")
        print("=" * 60)
        
        amount_cols = ['loan_amount_requested', 'total_outstanding_debt', 'estimated_monthly_emi']
        
        for col in amount_cols:
            if col in df.columns:
                # Round to nearest hundred
                df[col] = df[col].round(-2)
                
                # Ensure no negative values
                df[col] = df[col].clip(lower=0)
                
                # Create log-transformed version (add 1 to handle zeros)
                df[f'{col}_log'] = np.log1p(df[col])
                
                print(f"\n{col}:")
                print(f"  Range: {df[col].min():,.0f} - {df[col].max():,.0f}")
                print(f"  Skewness: {df[col].skew():.2f}")
                print(f"  Log-transformed skewness: {df[f'{col}_log'].skew():.2f}")
        
        # Create normalized versions (0-1 scaling)
        self.amount_scaler = MinMaxScaler()
        amount_cols_present = [c for c in amount_cols if c in df.columns]
        
        normalized_cols = [f'{c}_normalized' for c in amount_cols_present]
        df[normalized_cols] = self.amount_scaler.fit_transform(df[amount_cols_present])
        
        print(f"\nCreated log-transformed columns: {[f'{c}_log' for c in amount_cols_present]}")
        print(f"Created normalized columns: {normalized_cols}")
        
        return df
    
    # =========================================================================
    # 3. CATEGORICAL VALUE NORMALIZATION
    # =========================================================================
    
    def normalize_employment_type(self, df, column='employment_type'):
        """
        Normalize employment type values:
        - Standardize naming conventions
        - Group similar categories
        - Create binary flags for common types
        """
        print("\n" + "=" * 60)
        print("EMPLOYMENT TYPE NORMALIZATION")
        print("=" * 60)
        
        if column not in df.columns:
            print(f"Column '{column}' not found in dataframe")
            return df
        
        # Define mapping for standardization
        employment_mapping = {
            # Salaried variations
            'Salaried': 'SALARIED',
            'salaried': 'SALARIED',
            'SALARIED': 'SALARIED',
            'Employed': 'SALARIED',
            'Full-time': 'SALARIED',
            'Full Time': 'SALARIED',
            
            # Self-employed variations
            'Self-Employed': 'SELF_EMPLOYED',
            'Self Employed': 'SELF_EMPLOYED',
            'self-employed': 'SELF_EMPLOYED',
            'SELF-EMPLOYED': 'SELF_EMPLOYED',
            'Professional': 'SELF_EMPLOYED',
            
            # Business owner variations
            'Business Owner': 'BUSINESS_OWNER',
            'Business': 'BUSINESS_OWNER',
            'Businessman': 'BUSINESS_OWNER',
            'Entrepreneur': 'BUSINESS_OWNER',
            
            # Freelancer variations
            'Freelancer': 'FREELANCER',
            'Freelance': 'FREELANCER',
            'Contractor': 'FREELANCER',
            'Gig Worker': 'FREELANCER',
            
            # Retired variations
            'Retired': 'RETIRED',
            'Pensioner': 'RETIRED',
            
            # Other
            'Unemployed': 'UNEMPLOYED',
            'Student': 'STUDENT',
            'Homemaker': 'HOMEMAKER'
        }
        
        self.categorical_mappings['employment_type'] = employment_mapping
        
        # Apply mapping
        original_values = df[column].unique()
        df[f'{column}_normalized'] = df[column].map(employment_mapping).fillna('OTHER')
        
        # Create binary flags
        df['is_salaried'] = (df[f'{column}_normalized'] == 'SALARIED').astype(int)
        df['is_self_employed'] = (df[f'{column}_normalized'] == 'SELF_EMPLOYED').astype(int)
        df['is_business_owner'] = (df[f'{column}_normalized'] == 'BUSINESS_OWNER').astype(int)
        
        # Create employment stability score
        stability_scores = {
            'SALARIED': 5,
            'BUSINESS_OWNER': 4,
            'SELF_EMPLOYED': 3,
            'FREELANCER': 2,
            'RETIRED': 3,
            'UNEMPLOYED': 1,
            'STUDENT': 1,
            'HOMEMAKER': 2,
            'OTHER': 2
        }
        df['employment_stability_score'] = df[f'{column}_normalized'].map(stability_scores)
        
        print(f"\nOriginal values: {list(original_values)}")
        print(f"\nNormalized distribution:")
        print(df[f'{column}_normalized'].value_counts().to_string())
        print(f"\nCreated binary flags: is_salaried, is_self_employed, is_business_owner")
        print(f"Created employment_stability_score (1-5 scale)")
        
        return df
    
    def normalize_loan_purpose(self, df, column='loan_purpose'):
        """
        Normalize loan purpose values:
        - Standardize naming conventions
        - Create risk-based groupings
        - Create binary flags for secured vs unsecured
        """
        print("\n" + "=" * 60)
        print("LOAN PURPOSE NORMALIZATION")
        print("=" * 60)
        
        if column not in df.columns:
            print(f"Column '{column}' not found in dataframe")
            return df
        
        # Define mapping for standardization
        purpose_mapping = {
            # Home Loan variations
            'Home Loan': 'HOME_LOAN',
            'Housing Loan': 'HOME_LOAN',
            'Mortgage': 'HOME_LOAN',
            'Home Purchase': 'HOME_LOAN',
            'Home Construction': 'HOME_LOAN',
            'Home Improvement': 'HOME_IMPROVEMENT',
            
            # Personal Loan variations
            'Personal Loan': 'PERSONAL_LOAN',
            'Personal': 'PERSONAL_LOAN',
            'Debt Consolidation': 'PERSONAL_LOAN',
            'Medical': 'PERSONAL_LOAN',
            'Wedding': 'PERSONAL_LOAN',
            'Travel': 'PERSONAL_LOAN',
            
            # Auto Loan variations
            'Auto Loan': 'AUTO_LOAN',
            'Car Loan': 'AUTO_LOAN',
            'Vehicle Loan': 'AUTO_LOAN',
            'Two Wheeler': 'AUTO_LOAN',
            
            # Education Loan variations
            'Education Loan': 'EDUCATION_LOAN',
            'Education': 'EDUCATION_LOAN',
            'Student Loan': 'EDUCATION_LOAN',
            
            # Business Loan variations
            'Business Loan': 'BUSINESS_LOAN',
            'Working Capital': 'BUSINESS_LOAN',
            'Business Expansion': 'BUSINESS_LOAN',
            
            # Credit Card
            'Credit Card': 'CREDIT_CARD',
            
            # Consumer Durable
            'Consumer Durable': 'CONSUMER_DURABLE',
            'Electronics': 'CONSUMER_DURABLE',
            'Appliances': 'CONSUMER_DURABLE'
        }
        
        self.categorical_mappings['loan_purpose'] = purpose_mapping
        
        # Apply mapping
        original_values = df[column].unique()
        df[f'{column}_normalized'] = df[column].map(purpose_mapping).fillna('OTHER')
        
        # Create secured vs unsecured flag
        secured_loans = ['HOME_LOAN', 'AUTO_LOAN', 'HOME_IMPROVEMENT']
        df['is_secured_loan'] = df[f'{column}_normalized'].isin(secured_loans).astype(int)
        
        # Create loan risk category
        risk_categories = {
            'HOME_LOAN': 'LOW_RISK',
            'AUTO_LOAN': 'LOW_RISK',
            'EDUCATION_LOAN': 'MEDIUM_RISK',
            'PERSONAL_LOAN': 'MEDIUM_RISK',
            'BUSINESS_LOAN': 'MEDIUM_RISK',
            'HOME_IMPROVEMENT': 'LOW_RISK',
            'CONSUMER_DURABLE': 'HIGH_RISK',
            'CREDIT_CARD': 'HIGH_RISK',
            'OTHER': 'HIGH_RISK'
        }
        df['loan_risk_category'] = df[f'{column}_normalized'].map(risk_categories)
        
        # Create numerical risk score
        risk_scores = {'LOW_RISK': 1, 'MEDIUM_RISK': 2, 'HIGH_RISK': 3}
        df['loan_risk_score'] = df['loan_risk_category'].map(risk_scores)
        
        print(f"\nOriginal values: {list(original_values)}")
        print(f"\nNormalized distribution:")
        print(df[f'{column}_normalized'].value_counts().to_string())
        print(f"\nLoan risk category distribution:")
        print(df['loan_risk_category'].value_counts().to_string())
        print(f"\nCreated: is_secured_loan, loan_risk_category, loan_risk_score")
        
        return df
    
    def normalize_other_categoricals(self, df):
        """Normalize other categorical columns"""
        
        print("\n" + "=" * 60)
        print("OTHER CATEGORICAL NORMALIZATION")
        print("=" * 60)
        
        # Education normalization
        if 'education' in df.columns:
            education_mapping = {
                'High School': 'HIGH_SCHOOL',
                'Bachelor': 'BACHELOR',
                'Master': 'MASTER',
                'PhD': 'PHD',
                'Other': 'OTHER'
            }
            df['education_normalized'] = df['education'].map(education_mapping).fillna('OTHER')
            
            # Education level score
            edu_scores = {'OTHER': 1, 'HIGH_SCHOOL': 2, 'BACHELOR': 3, 'MASTER': 4, 'PHD': 5}
            df['education_score'] = df['education_normalized'].map(edu_scores)
            print(f"Normalized 'education' column")
        
        # Marital status normalization
        if 'marital_status' in df.columns:
            marital_mapping = {
                'Single': 'SINGLE',
                'Married': 'MARRIED',
                'Divorced': 'DIVORCED',
                'Widowed': 'WIDOWED'
            }
            df['marital_status_normalized'] = df['marital_status'].map(marital_mapping).fillna('OTHER')
            df['is_married'] = (df['marital_status_normalized'] == 'MARRIED').astype(int)
            print(f"Normalized 'marital_status' column")
        
        # Residence type normalization
        if 'residence_type' in df.columns:
            residence_mapping = {
                'Owned': 'OWNED',
                'Rented': 'RENTED',
                'Mortgaged': 'MORTGAGED',
                'Living with Parents': 'WITH_PARENTS'
            }
            df['residence_type_normalized'] = df['residence_type'].map(residence_mapping).fillna('OTHER')
            df['is_home_owner'] = df['residence_type_normalized'].isin(['OWNED', 'MORTGAGED']).astype(int)
            print(f"Normalized 'residence_type' column")
        
        # Gender normalization
        if 'gender' in df.columns:
            df['gender_normalized'] = df['gender'].str.upper()
            df['is_male'] = (df['gender_normalized'] == 'MALE').astype(int)
            print(f"Normalized 'gender' column")
        
        return df
    
    # =========================================================================
    # MAIN PIPELINE
    # =========================================================================
    
    def run_full_pipeline(self, df, introduce_missing=False):
        """
        Run the complete data cleansing pipeline
        """
        print("\n" + "=" * 60)
        print("STARTING DATA CLEANSING PIPELINE")
        print("=" * 60)
        print(f"Input shape: {df.shape}")
        
        # Optionally introduce missing values for testing
        if introduce_missing:
            df = self._introduce_missing_values(df)
        
        # Step 1: Analyze and impute missing values
        print("\n\n>>> STEP 1: MISSING VALUE IMPUTATION")
        self.analyze_missing_values(df)
        df = self.impute_numerical_features(df, strategy='median')
        df = self.impute_categorical_features(df, strategy='most_frequent')
        
        # Step 2: Standardize income and amount formats
        print("\n\n>>> STEP 2: INCOME & AMOUNT STANDARDIZATION")
        df = self.standardize_income_formats(df)
        df = self.standardize_amount_formats(df)
        
        # Step 3: Normalize categorical values
        print("\n\n>>> STEP 3: CATEGORICAL NORMALIZATION")
        df = self.normalize_employment_type(df)
        df = self.normalize_loan_purpose(df)
        df = self.normalize_other_categoricals(df)
        
        print("\n\n" + "=" * 60)
        print("DATA CLEANSING PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Output shape: {df.shape}")
        print(f"New columns added: {df.shape[1] - 51}")
        
        return df
    
    def _introduce_missing_values(self, df, missing_rate=0.05):
        """Introduce random missing values for testing imputation"""
        print(f"\nIntroducing {missing_rate*100}% missing values for testing...")
        
        df = df.copy()
        cols_to_corrupt = ['annual_income', 'credit_score', 'employment_type', 
                          'loan_purpose', 'age', 'total_outstanding_debt']
        
        for col in cols_to_corrupt:
            if col in df.columns:
                mask = np.random.random(len(df)) < missing_rate
                df.loc[mask, col] = np.nan
                print(f"  - {col}: {mask.sum()} missing values introduced")
        
        return df


def main():
    """Main execution function"""
    
    # Load the dataset
    print("Loading credit risk dataset...")
    df = pd.read_csv('data/credit_risk_dataset.csv')
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Initialize cleanser
    cleanser = DataCleanser()
    
    # Run full pipeline (with missing value introduction for demonstration)
    df_cleaned = cleanser.run_full_pipeline(df, introduce_missing=True)
    
    # Save cleaned dataset
    output_path = 'data/credit_risk_dataset_cleaned.csv'
    df_cleaned.to_csv(output_path, index=False)
    print(f"\nCleaned dataset saved to: {output_path}")
    
    # Print sample of new columns
    new_cols = [c for c in df_cleaned.columns if c not in df.columns]
    print(f"\n\nNew columns created ({len(new_cols)}):")
    for col in new_cols:
        print(f"  - {col}")
    
    # Print data types summary
    print("\n\nData Types Summary:")
    print(df_cleaned.dtypes.value_counts())
    
    return df_cleaned


if __name__ == "__main__":
    df_cleaned = main()
