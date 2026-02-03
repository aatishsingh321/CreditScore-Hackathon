"""
Credit Risk Scoring - Feature Encoding Module
Implements:
- One-hot encoding for categorical variables
- WOE (Weight of Evidence) encoding for explainability
- Target encoding with leakage prevention (using K-Fold)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import KFold
import warnings
warnings.filterwarnings('ignore')


class FeatureEncoder:
    """Feature encoding pipeline for credit risk modeling"""
    
    def __init__(self):
        self.onehot_encoder = None
        self.onehot_columns = None
        self.woe_mappings = {}
        self.iv_scores = {}
        self.target_encodings = {}
        self.global_mean = None
        
    # =========================================================================
    # 1. ONE-HOT ENCODING
    # =========================================================================
    
    def fit_onehot_encoder(self, df, columns=None, max_categories=10):
        """
        Fit one-hot encoder on categorical columns
        
        Parameters:
        - columns: List of columns to encode (auto-detected if None)
        - max_categories: Max unique values for a column to be one-hot encoded
        """
        if columns is None:
            # Auto-detect categorical columns with reasonable cardinality
            columns = []
            for col in df.select_dtypes(include=['object', 'category']).columns:
                if col not in ['applicant_id', 'application_date']:
                    n_unique = df[col].nunique()
                    if n_unique <= max_categories:
                        columns.append(col)
        
        self.onehot_columns = columns
        print(f"Fitting one-hot encoder on {len(columns)} columns:")
        for col in columns:
            print(f"  - {col}: {df[col].nunique()} categories")
        
        self.onehot_encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown='ignore',
            drop='first'  # Drop first to avoid multicollinearity
        )
        self.onehot_encoder.fit(df[columns])
        
        return self
    
    def transform_onehot(self, df):
        """Apply one-hot encoding transformation"""
        if self.onehot_encoder is None:
            raise ValueError("Encoder not fitted. Call fit_onehot_encoder first.")
        
        # Transform
        encoded = self.onehot_encoder.transform(df[self.onehot_columns])
        
        # Create column names
        feature_names = self.onehot_encoder.get_feature_names_out(self.onehot_columns)
        
        # Create DataFrame
        encoded_df = pd.DataFrame(
            encoded,
            columns=feature_names,
            index=df.index
        )
        
        # Combine with original data (excluding original categorical columns)
        result = pd.concat([
            df.drop(columns=self.onehot_columns),
            encoded_df
        ], axis=1)
        
        print(f"\nOne-hot encoding complete:")
        print(f"  - Original columns removed: {len(self.onehot_columns)}")
        print(f"  - New columns added: {len(feature_names)}")
        
        return result, feature_names.tolist()
    
    def fit_transform_onehot(self, df, columns=None, max_categories=10):
        """Fit and transform in one step"""
        self.fit_onehot_encoder(df, columns, max_categories)
        return self.transform_onehot(df)
    
    # =========================================================================
    # 2. WEIGHT OF EVIDENCE (WOE) ENCODING
    # =========================================================================
    
    def calculate_woe_iv(self, df, feature, target, bins=10):
        """
        Calculate WOE and Information Value for a feature
        
        WOE = ln(Distribution of Good / Distribution of Bad)
        IV = Σ (Distribution of Good - Distribution of Bad) * WOE
        
        IV Interpretation:
        - < 0.02: Not useful for prediction
        - 0.02 - 0.1: Weak predictive power
        - 0.1 - 0.3: Medium predictive power
        - 0.3 - 0.5: Strong predictive power
        - > 0.5: Suspicious (too good, check for overfitting)
        """
        df_temp = df[[feature, target]].copy()
        
        # For numerical features, bin them first
        if df_temp[feature].dtype in ['int64', 'float64']:
            df_temp[f'{feature}_binned'] = pd.qcut(
                df_temp[feature], 
                q=bins, 
                duplicates='drop'
            )
            feature_col = f'{feature}_binned'
        else:
            feature_col = feature
        
        # Calculate distribution
        total_good = (df_temp[target] == 0).sum()
        total_bad = (df_temp[target] == 1).sum()
        
        woe_table = df_temp.groupby(feature_col).agg({
            target: ['count', 'sum']
        }).reset_index()
        
        woe_table.columns = ['category', 'total', 'bad']
        woe_table['good'] = woe_table['total'] - woe_table['bad']
        
        # Calculate distributions
        woe_table['dist_good'] = woe_table['good'] / total_good
        woe_table['dist_bad'] = woe_table['bad'] / total_bad
        
        # Handle zeros to avoid log(0)
        woe_table['dist_good'] = woe_table['dist_good'].replace(0, 0.0001)
        woe_table['dist_bad'] = woe_table['dist_bad'].replace(0, 0.0001)
        
        # Calculate WOE
        woe_table['woe'] = np.log(woe_table['dist_good'] / woe_table['dist_bad'])
        
        # Calculate IV contribution
        woe_table['iv'] = (woe_table['dist_good'] - woe_table['dist_bad']) * woe_table['woe']
        
        # Total IV
        iv = woe_table['iv'].sum()
        
        # Create WOE mapping
        woe_mapping = dict(zip(woe_table['category'].astype(str), woe_table['woe']))
        
        return woe_mapping, iv, woe_table
    
    def fit_woe_encoder(self, df, target_col='default', columns=None, bins=10):
        """
        Fit WOE encoder on specified columns
        
        Parameters:
        - target_col: Name of binary target column
        - columns: List of columns to encode
        - bins: Number of bins for numerical features
        """
        print("\n" + "=" * 60)
        print("WEIGHT OF EVIDENCE (WOE) ENCODING")
        print("=" * 60)
        
        if columns is None:
            # Default to categorical columns
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            columns = [c for c in columns if c not in ['applicant_id', 'application_date']]
        
        print(f"\nFitting WOE encoder on {len(columns)} columns...")
        print(f"Target column: {target_col}")
        print(f"Target distribution: {df[target_col].value_counts().to_dict()}")
        
        self.woe_mappings = {}
        self.iv_scores = {}
        
        iv_summary = []
        
        for col in columns:
            woe_mapping, iv, woe_table = self.calculate_woe_iv(
                df, col, target_col, bins
            )
            self.woe_mappings[col] = woe_mapping
            self.iv_scores[col] = iv
            
            # Determine predictive power
            if iv < 0.02:
                power = "Not useful"
            elif iv < 0.1:
                power = "Weak"
            elif iv < 0.3:
                power = "Medium"
            elif iv < 0.5:
                power = "Strong"
            else:
                power = "Suspicious"
            
            iv_summary.append({
                'feature': col,
                'iv': iv,
                'predictive_power': power
            })
        
        # Create IV summary DataFrame
        iv_df = pd.DataFrame(iv_summary).sort_values('iv', ascending=False)
        
        print("\n" + "-" * 60)
        print("INFORMATION VALUE (IV) SUMMARY")
        print("-" * 60)
        print(iv_df.to_string(index=False))
        
        return self, iv_df
    
    def transform_woe(self, df, columns=None):
        """Apply WOE transformation"""
        if not self.woe_mappings:
            raise ValueError("WOE encoder not fitted. Call fit_woe_encoder first.")
        
        if columns is None:
            columns = list(self.woe_mappings.keys())
        
        df_woe = df.copy()
        
        for col in columns:
            if col in self.woe_mappings:
                # Create WOE column
                df_woe[f'{col}_woe'] = df_woe[col].astype(str).map(self.woe_mappings[col])
                # Fill unknown categories with 0 (neutral WOE)
                df_woe[f'{col}_woe'] = df_woe[f'{col}_woe'].fillna(0)
        
        woe_columns = [f'{col}_woe' for col in columns if col in self.woe_mappings]
        print(f"\nWOE transformation complete. Created {len(woe_columns)} WOE columns.")
        
        return df_woe, woe_columns
    
    def get_iv_scores(self):
        """Return IV scores sorted by value"""
        return pd.DataFrame([
            {'feature': k, 'iv': v} 
            for k, v in self.iv_scores.items()
        ]).sort_values('iv', ascending=False)
    
    # =========================================================================
    # 3. TARGET ENCODING WITH LEAKAGE PREVENTION
    # =========================================================================
    
    def fit_target_encoder(self, df, target_col='default', columns=None, 
                           n_folds=5, smoothing=10):
        """
        Fit target encoder with K-Fold cross-validation to prevent leakage
        
        The encoding uses smoothing to handle categories with few samples:
        encoded = (count * mean_category + smoothing * global_mean) / (count + smoothing)
        
        Parameters:
        - target_col: Name of target column
        - columns: Columns to encode
        - n_folds: Number of folds for cross-validation
        - smoothing: Smoothing parameter (higher = more regularization)
        """
        print("\n" + "=" * 60)
        print("TARGET ENCODING (WITH LEAKAGE PREVENTION)")
        print("=" * 60)
        
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            columns = [c for c in columns if c not in ['applicant_id', 'application_date']]
        
        self.global_mean = df[target_col].mean()
        self.target_encodings = {}
        
        print(f"\nFitting target encoder on {len(columns)} columns...")
        print(f"Target column: {target_col}")
        print(f"Global mean (default rate): {self.global_mean:.4f}")
        print(f"Number of folds: {n_folds}")
        print(f"Smoothing parameter: {smoothing}")
        
        for col in columns:
            # Calculate statistics for each category
            stats = df.groupby(col)[target_col].agg(['mean', 'count'])
            
            # Apply smoothing
            smoothed_mean = (
                stats['count'] * stats['mean'] + smoothing * self.global_mean
            ) / (stats['count'] + smoothing)
            
            self.target_encodings[col] = {
                'mapping': smoothed_mean.to_dict(),
                'global_mean': self.global_mean,
                'smoothing': smoothing
            }
            
            print(f"  - {col}: {len(smoothed_mean)} categories encoded")
        
        return self
    
    def transform_target_encoding_cv(self, df, target_col='default', columns=None,
                                      n_folds=5, smoothing=10):
        """
        Apply target encoding with K-Fold CV to prevent data leakage
        
        For each fold:
        - Use out-of-fold data to calculate target statistics
        - Apply encoding to in-fold data
        
        This prevents the target from leaking into the features.
        """
        print("\n" + "-" * 60)
        print("Applying K-Fold Target Encoding...")
        print("-" * 60)
        
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            columns = [c for c in columns if c not in ['applicant_id', 'application_date']]
        
        df_encoded = df.copy()
        global_mean = df[target_col].mean()
        
        # Initialize encoded columns
        for col in columns:
            df_encoded[f'{col}_target_enc'] = np.nan
        
        # K-Fold encoding
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        for fold, (train_idx, val_idx) in enumerate(kf.split(df)):
            print(f"  Processing fold {fold + 1}/{n_folds}...")
            
            for col in columns:
                # Calculate target statistics on training fold
                train_stats = df.iloc[train_idx].groupby(col)[target_col].agg(['mean', 'count'])
                
                # Apply smoothing
                smoothed_mean = (
                    train_stats['count'] * train_stats['mean'] + smoothing * global_mean
                ) / (train_stats['count'] + smoothing)
                
                # Apply to validation fold
                df_encoded.loc[val_idx, f'{col}_target_enc'] = (
                    df.iloc[val_idx][col].map(smoothed_mean)
                )
        
        # Fill any remaining NaN with global mean
        for col in columns:
            df_encoded[f'{col}_target_enc'] = df_encoded[f'{col}_target_enc'].fillna(global_mean)
        
        target_enc_columns = [f'{col}_target_enc' for col in columns]
        print(f"\nTarget encoding complete. Created {len(target_enc_columns)} columns.")
        
        return df_encoded, target_enc_columns
    
    def transform_target_encoding(self, df, columns=None):
        """
        Apply pre-fitted target encoding (for new/test data)
        Uses the mappings learned during fitting
        """
        if not self.target_encodings:
            raise ValueError("Target encoder not fitted. Call fit_target_encoder first.")
        
        if columns is None:
            columns = list(self.target_encodings.keys())
        
        df_encoded = df.copy()
        
        for col in columns:
            if col in self.target_encodings:
                encoding = self.target_encodings[col]
                df_encoded[f'{col}_target_enc'] = (
                    df_encoded[col].map(encoding['mapping'])
                    .fillna(encoding['global_mean'])
                )
        
        return df_encoded
    
    # =========================================================================
    # MAIN PIPELINE
    # =========================================================================
    
    def run_full_encoding_pipeline(self, df, target_col='default', 
                                    onehot_columns=None,
                                    woe_columns=None,
                                    target_enc_columns=None):
        """
        Run complete feature encoding pipeline
        
        Returns encoded dataframe and summary of all encodings
        """
        print("\n" + "=" * 60)
        print("STARTING FEATURE ENCODING PIPELINE")
        print("=" * 60)
        print(f"Input shape: {df.shape}")
        
        # Default column selections
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_cols = [c for c in categorical_cols 
                          if c not in ['applicant_id', 'application_date']]
        
        if onehot_columns is None:
            # Use normalized categorical columns for one-hot
            onehot_columns = [c for c in categorical_cols 
                            if '_normalized' in c and df[c].nunique() <= 10]
        
        if woe_columns is None:
            # Use original categorical columns for WOE
            woe_columns = [c for c in categorical_cols 
                         if '_normalized' not in c and df[c].nunique() <= 20]
        
        if target_enc_columns is None:
            # Use all categorical columns for target encoding
            target_enc_columns = [c for c in categorical_cols if df[c].nunique() <= 20]
        
        encoding_summary = {
            'onehot': {},
            'woe': {},
            'target_encoding': {}
        }
        
        # Step 1: One-Hot Encoding
        print("\n\n>>> STEP 1: ONE-HOT ENCODING")
        print("-" * 40)
        if onehot_columns:
            df, onehot_features = self.fit_transform_onehot(df, columns=onehot_columns)
            encoding_summary['onehot'] = {
                'original_columns': onehot_columns,
                'new_columns': onehot_features
            }
        else:
            print("No columns selected for one-hot encoding")
        
        # Step 2: WOE Encoding
        print("\n\n>>> STEP 2: WOE ENCODING")
        print("-" * 40)
        if woe_columns:
            # Filter to columns still in df
            woe_columns = [c for c in woe_columns if c in df.columns]
            if woe_columns:
                self.fit_woe_encoder(df, target_col=target_col, columns=woe_columns)
                df, woe_features = self.transform_woe(df, columns=woe_columns)
                encoding_summary['woe'] = {
                    'columns': woe_columns,
                    'woe_columns': woe_features,
                    'iv_scores': self.iv_scores
                }
        else:
            print("No columns selected for WOE encoding")
        
        # Step 3: Target Encoding with CV
        print("\n\n>>> STEP 3: TARGET ENCODING (K-FOLD CV)")
        print("-" * 40)
        if target_enc_columns:
            # Filter to columns still in df
            target_enc_columns = [c for c in target_enc_columns if c in df.columns]
            if target_enc_columns:
                df, target_features = self.transform_target_encoding_cv(
                    df, target_col=target_col, columns=target_enc_columns
                )
                encoding_summary['target_encoding'] = {
                    'columns': target_enc_columns,
                    'encoded_columns': target_features
                }
        else:
            print("No columns selected for target encoding")
        
        print("\n\n" + "=" * 60)
        print("FEATURE ENCODING PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Output shape: {df.shape}")
        
        return df, encoding_summary


def main():
    """Main execution function"""
    
    # Load the cleaned dataset
    print("Loading cleaned credit risk dataset...")
    df = pd.read_csv('data/credit_risk_dataset_cleaned.csv')
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Initialize encoder
    encoder = FeatureEncoder()
    
    # Define columns for each encoding type
    onehot_columns = [
        'gender_normalized',
        'education_normalized', 
        'marital_status_normalized',
        'residence_type_normalized',
        'employment_type_normalized',
        'loan_purpose_normalized',
        'loan_risk_category'
    ]
    
    woe_columns = [
        'gender',
        'education',
        'marital_status',
        'residence_type',
        'employment_type',
        'loan_purpose',
        'city',
        'industry'
    ]
    
    target_enc_columns = [
        'city',
        'industry',
        'employment_type',
        'loan_purpose'
    ]
    
    # Run full encoding pipeline
    df_encoded, summary = encoder.run_full_encoding_pipeline(
        df,
        target_col='default',
        onehot_columns=onehot_columns,
        woe_columns=woe_columns,
        target_enc_columns=target_enc_columns
    )
    
    # Save encoded dataset
    output_path = 'data/credit_risk_dataset_encoded.csv'
    df_encoded.to_csv(output_path, index=False)
    print(f"\nEncoded dataset saved to: {output_path}")
    
    # Print encoding summary
    print("\n" + "=" * 60)
    print("ENCODING SUMMARY")
    print("=" * 60)
    
    print("\n1. ONE-HOT ENCODING:")
    if summary['onehot']:
        print(f"   Original columns: {len(summary['onehot']['original_columns'])}")
        print(f"   New binary columns: {len(summary['onehot']['new_columns'])}")
    
    print("\n2. WOE ENCODING:")
    if summary['woe']:
        print(f"   Columns encoded: {len(summary['woe']['columns'])}")
        print("\n   Top features by Information Value (IV):")
        iv_df = encoder.get_iv_scores()
        print(iv_df.head(10).to_string(index=False))
    
    print("\n3. TARGET ENCODING:")
    if summary['target_encoding']:
        print(f"   Columns encoded: {len(summary['target_encoding']['columns'])}")
        print(f"   Using 5-fold CV for leakage prevention")
    
    # Final dataset info
    print("\n" + "=" * 60)
    print("FINAL DATASET INFO")
    print("=" * 60)
    print(f"Total records: {len(df_encoded)}")
    print(f"Total features: {len(df_encoded.columns)}")
    print(f"\nFeature types:")
    print(df_encoded.dtypes.value_counts())
    
    # List new encoding columns
    new_cols = [c for c in df_encoded.columns if c not in df.columns]
    print(f"\nNew encoded columns ({len(new_cols)}):")
    
    onehot_cols = [c for c in new_cols if not c.endswith('_woe') and not c.endswith('_target_enc')]
    woe_cols = [c for c in new_cols if c.endswith('_woe')]
    target_cols = [c for c in new_cols if c.endswith('_target_enc')]
    
    print(f"\n  One-Hot columns ({len(onehot_cols)}):")
    for col in onehot_cols[:5]:
        print(f"    - {col}")
    if len(onehot_cols) > 5:
        print(f"    ... and {len(onehot_cols) - 5} more")
    
    print(f"\n  WOE columns ({len(woe_cols)}):")
    for col in woe_cols:
        print(f"    - {col}")
    
    print(f"\n  Target Encoded columns ({len(target_cols)}):")
    for col in target_cols:
        print(f"    - {col}")
    
    return df_encoded, encoder


if __name__ == "__main__":
    df_encoded, encoder = main()
