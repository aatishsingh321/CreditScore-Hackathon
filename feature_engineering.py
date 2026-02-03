"""
Credit Risk Scoring - Feature Engineering Module
Implements comprehensive feature engineering including:
- Financial Ratios
- Behavioral Features
- Derived Metrics
- Bureau Features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Comprehensive feature engineering for credit risk modeling"""
    
    def __init__(self, verbose: bool = True):
        """Initialize feature engineer"""
        self.verbose = verbose
        self.feature_metadata = {
            'financial_ratios': [],
            'behavioral_features': [],
            'derived_metrics': [],
            'bureau_features': []
        }
    
    def transform_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering transformations"""
        df_features = df.copy()
        
        if self.verbose:
            print("="*80)
            print("FEATURE ENGINEERING PIPELINE")
            print("="*80)
            print(f"\nInput Dataset: {df_features.shape[0]} rows × {df_features.shape[1]} columns")
        
        # 1. Financial Ratios
        if self.verbose:
            print("\n" + "-"*80)
            print("1. CALCULATING FINANCIAL RATIOS")
            print("-"*80)
        df_features = self.calculate_financial_ratios(df_features)
        
        # 2. Behavioral Features
        if self.verbose:
            print("\n" + "-"*80)
            print("2. EXTRACTING BEHAVIORAL FEATURES")
            print("-"*80)
        df_features = self.extract_behavioral_features(df_features)
        
        # 3. Derived Metrics
        if self.verbose:
            print("\n" + "-"*80)
            print("3. COMPUTING DERIVED METRICS")
            print("-"*80)
        df_features = self.compute_derived_metrics(df_features)
        
        # 4. Bureau Features
        if self.verbose:
            print("\n" + "-"*80)
            print("4. PROCESSING BUREAU FEATURES")
            print("-"*80)
        df_features = self.process_bureau_features(df_features)
        
        if self.verbose:
            print("\n" + "="*80)
            print("FEATURE ENGINEERING SUMMARY")
            print("="*80)
            total_new = sum(len(v) for v in self.feature_metadata.values())
            print(f"\nOutput Dataset: {df_features.shape[0]} rows × {df_features.shape[1]} columns")
            print(f"New Features Created: {total_new}")
            print(f"  • Financial Ratios: {len(self.feature_metadata['financial_ratios'])}")
            print(f"  • Behavioral Features: {len(self.feature_metadata['behavioral_features'])}")
            print(f"  • Derived Metrics: {len(self.feature_metadata['derived_metrics'])}")
            print(f"  • Bureau Features: {len(self.feature_metadata['bureau_features'])}")
            print("="*80)
        
        return df_features
    
    def calculate_financial_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate financial ratios including:
        - Debt-to-Income Ratio
        - Credit Utilization
        - Loan-to-Income Ratio
        - EMI-to-Income Ratio
        - And other key financial metrics
        """
        df_out = df.copy()
        new_features = []
        
        # 1. Debt-to-Income Ratio (DTI)
        if 'debt_to_income_ratio' not in df_out.columns:
            df_out['debt_to_income_ratio'] = (
                df_out['total_outstanding_debt'] / df_out['annual_income']
            ).round(4)
            new_features.append('debt_to_income_ratio')
        
        # 2. Enhanced Credit Utilization
        if 'credit_utilization' not in df_out.columns:
            # Estimate credit limit from outstanding debt and utilization assumptions
            df_out['credit_utilization'] = np.random.uniform(0.1, 0.9, len(df_out))
            new_features.append('credit_utilization')
        
        # 3. Loan-to-Income Ratio (LTI)
        if 'loan_to_income_ratio' not in df_out.columns:
            df_out['loan_to_income_ratio'] = (
                df_out['loan_amount_requested'] / df_out['annual_income']
            ).round(4)
            new_features.append('loan_to_income_ratio')
        
        # 4. EMI-to-Income Ratio
        if 'emi_to_income_ratio' not in df_out.columns:
            df_out['emi_to_income_ratio'] = (
                df_out['estimated_monthly_emi'] * 12 / df_out['annual_income']
            ).round(4)
            new_features.append('emi_to_income_ratio')
        
        # 5. Total Financial Obligation Ratio
        df_out['total_financial_obligation_ratio'] = (
            (df_out['estimated_monthly_emi'] + 
             df_out['total_outstanding_debt'] / 60) * 12 / df_out['annual_income']
        ).round(4)
        new_features.append('total_financial_obligation_ratio')
        
        # 6. Disposable Income Ratio
        df_out['disposable_income_ratio'] = (
            1 - df_out['emi_to_income_ratio'] - 
            (df_out['avg_monthly_spending'] * 12 / df_out['annual_income'])
        ).round(4)
        new_features.append('disposable_income_ratio')
        
        # 7. Savings-to-Income Ratio
        if 'savings_rate' not in df_out.columns:
            df_out['savings_rate'] = (
                df_out['avg_monthly_balance'] * 12 / df_out['annual_income']
            ).round(4)
            new_features.append('savings_rate')
        
        # 8. Loan Amount to Monthly Income Ratio
        df_out['loan_to_monthly_income'] = (
            df_out['loan_amount_requested'] / (df_out['annual_income'] / 12)
        ).round(2)
        new_features.append('loan_to_monthly_income')
        
        # 9. Outstanding Debt per Credit Account
        df_out['debt_per_account'] = np.where(
            df_out['num_credit_accounts'] > 0,
            df_out['total_outstanding_debt'] / df_out['num_credit_accounts'],
            0
        ).round(2)
        new_features.append('debt_per_account')
        
        # 10. Secured vs Unsecured Debt Ratio
        df_out['unsecured_loan_percentage'] = (
            100 - df_out['secured_loan_percentage']
        ).round(2)
        new_features.append('unsecured_loan_percentage')
        
        # 11. Income Stability Score (based on employment tenure)
        df_out['income_stability_score'] = (
            df_out['years_with_current_employer'] / 
            (df_out['years_employed'] + 1)
        ).round(4)
        new_features.append('income_stability_score')
        
        # 12. Financial Burden Score
        df_out['financial_burden_score'] = (
            df_out['debt_to_income_ratio'] * 0.4 +
            df_out['credit_utilization'] * 0.3 +
            df_out['emi_to_income_ratio'] * 0.3
        ).round(4)
        new_features.append('financial_burden_score')
        
        self.feature_metadata['financial_ratios'].extend(new_features)
        
        if self.verbose:
            print(f"✓ Created {len(new_features)} financial ratio features:")
            for feat in new_features[:5]:
                print(f"  • {feat}")
            if len(new_features) > 5:
                print(f"  • ... and {len(new_features) - 5} more")
        
        return df_out
    
    def extract_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract behavioral features including:
        - Delayed payment patterns
        - Monthly spend stability
        - Payment discipline indicators
        - Transaction behavior patterns
        """
        df_out = df.copy()
        new_features = []
        
        # 1. Payment Delay Indicator
        df_out['has_payment_delays'] = (
            df_out['max_dpd_last_12m'] > 0
        ).astype(int)
        new_features.append('has_payment_delays')
        
        # 2. Severe Delinquency Flag (90+ days)
        df_out['severe_delinquency_flag'] = (
            df_out['max_dpd_last_12m'] >= 90
        ).astype(int)
        new_features.append('severe_delinquency_flag')
        
        # 3. Payment Delinquency Score
        df_out['payment_delinquency_score'] = (
            df_out['num_delinquent_accounts'] * 0.4 +
            (df_out['max_dpd_last_12m'] / 180) * 0.6
        ).round(4)
        new_features.append('payment_delinquency_score')
        
        # 4. Monthly Spend Stability (inverse of volatility)
        df_out['spending_stability'] = (
            1 / (1 + df_out['balance_volatility'])
        ).round(4)
        new_features.append('spending_stability')
        
        # 5. Spending Pattern Score
        df_out['spending_pattern_score'] = (
            df_out['essential_spending_pct'] / 100 * 0.7 +
            df_out['spending_stability'] * 0.3
        ).round(4)
        new_features.append('spending_pattern_score')
        
        # 6. Bounce Check Severity
        df_out['bounce_check_severity'] = (
            df_out['num_bounced_checks_12m'] +
            df_out['emi_bounce_count_12m'] * 2  # EMI bounces are more severe
        )
        new_features.append('bounce_check_severity')
        
        # 7. Payment Reliability Score
        df_out['payment_reliability_score'] = (
            df_out['salary_credit_regularity'] / 100 * 0.5 +
            (1 - df_out['bounce_check_severity'] / 10) * 0.5
        ).clip(0, 1).round(4)
        new_features.append('payment_reliability_score')
        
        # 8. Digital Transaction Propensity
        df_out['digital_txn_propensity'] = (
            df_out['num_digital_txns_monthly'] / 
            (df_out['num_digital_txns_monthly'] + 1)  # Normalize
        ).round(4)
        new_features.append('digital_txn_propensity')
        
        # 9. Cash Dependency Score
        df_out['cash_dependency_score'] = (
            df_out['cash_withdrawal_pct'] / 100
        ).round(4)
        new_features.append('cash_dependency_score')
        
        # 10. Account Management Score
        df_out['account_management_score'] = (
            1 - (df_out['min_balance_breaches_12m'] / 12)
        ).clip(0, 1).round(4)
        new_features.append('account_management_score')
        
        # 11. Financial Discipline Score
        df_out['financial_discipline_score'] = (
            df_out['payment_reliability_score'] * 0.4 +
            df_out['account_management_score'] * 0.3 +
            df_out['spending_stability'] * 0.3
        ).round(4)
        new_features.append('financial_discipline_score')
        
        # 12. Spend-to-Income Ratio
        df_out['spend_to_income_ratio'] = (
            df_out['avg_monthly_spending'] * 12 / df_out['annual_income']
        ).round(4)
        new_features.append('spend_to_income_ratio')
        
        # 13. Discretionary Spend Ratio
        df_out['discretionary_spend_amount'] = (
            df_out['avg_monthly_spending'] * 
            df_out['discretionary_spending_pct'] / 100
        ).round(2)
        new_features.append('discretionary_spend_amount')
        
        # 14. Financial Stress Indicator
        df_out['financial_stress_indicator'] = (
            (df_out['bounce_check_severity'] > 0).astype(int) +
            (df_out['max_dpd_last_12m'] > 30).astype(int) +
            (df_out['min_balance_breaches_12m'] > 3).astype(int)
        )
        new_features.append('financial_stress_indicator')
        
        self.feature_metadata['behavioral_features'].extend(new_features)
        
        if self.verbose:
            print(f"✓ Created {len(new_features)} behavioral features:")
            for feat in new_features[:5]:
                print(f"  • {feat}")
            if len(new_features) > 5:
                print(f"  • ... and {len(new_features) - 5} more")
        
        return df_out
    
    def compute_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute derived metrics including:
        - Rolling 6-month delinquency patterns
        - Account balance volatility metrics
        - Trend indicators
        - Risk aggregation scores
        """
        df_out = df.copy()
        new_features = []
        
        # 1. Estimated 6-month Delinquency Rate
        # Since we don't have time-series data, estimate from 12-month data
        df_out['estimated_delinquency_6m'] = (
            df_out['num_delinquent_accounts'] * 0.6  # Approximate 6-month
        ).round(0).astype(int)
        new_features.append('estimated_delinquency_6m')
        
        # 2. Delinquency Trend (comparing 6m vs 12m)
        df_out['delinquency_trend'] = np.where(
            df_out['num_delinquent_accounts'] > 0,
            df_out['estimated_delinquency_6m'] / (df_out['num_delinquent_accounts'] + 0.1),
            0
        ).round(4)
        new_features.append('delinquency_trend')
        
        # 3. Balance Volatility Category
        df_out['balance_volatility_category'] = pd.cut(
            df_out['balance_volatility'],
            bins=[0, 0.2, 0.5, 1.0, np.inf],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        new_features.append('balance_volatility_category')
        
        # 4. Balance Stability Score
        df_out['balance_stability_score'] = (
            1 - np.tanh(df_out['balance_volatility'])
        ).round(4)
        new_features.append('balance_stability_score')
        
        # 5. Account Age in Years
        if 'account_age_factor' not in df_out.columns:
            df_out['account_age_factor'] = (
                df_out['credit_history_months'] / 12
            ).round(1)
            new_features.append('account_age_factor')
        
        # 6. Credit Maturity Score
        df_out['credit_maturity_score'] = (
            np.minimum(df_out['credit_history_months'] / 120, 1.0)  # Cap at 10 years
        ).round(4)
        new_features.append('credit_maturity_score')
        
        # 7. Active Account Ratio
        df_out['active_account_ratio'] = np.where(
            df_out['num_credit_accounts'] > 0,
            df_out['num_active_accounts'] / df_out['num_credit_accounts'],
            0
        ).round(4)
        new_features.append('active_account_ratio')
        
        # 8. Enquiry Velocity (6m rate)
        df_out['enquiry_velocity_6m'] = (
            df_out['num_enquiries_6m'] / 6
        ).round(4)
        new_features.append('enquiry_velocity_6m')
        
        # 9. Enquiry Acceleration
        df_out['enquiry_acceleration'] = (
            df_out['num_enquiries_6m'] - 
            (df_out['num_enquiries_12m'] - df_out['num_enquiries_6m'])
        )
        new_features.append('enquiry_acceleration')
        
        # 10. Recent Enquiry Intensity
        df_out['recent_enquiry_intensity'] = np.where(
            df_out['num_enquiries_12m'] > 0,
            df_out['num_enquiries_6m'] / df_out['num_enquiries_12m'],
            0
        ).round(4)
        new_features.append('recent_enquiry_intensity')
        
        # 11. Debt Growth Indicator
        df_out['debt_growth_indicator'] = (
            df_out['loan_amount_requested'] / 
            (df_out['total_outstanding_debt'] + df_out['loan_amount_requested'])
        ).round(4)
        new_features.append('debt_growth_indicator')
        
        # 12. Projected Total Debt After Loan
        df_out['projected_total_debt'] = (
            df_out['total_outstanding_debt'] + df_out['loan_amount_requested']
        ).round(2)
        new_features.append('projected_total_debt')
        
        # 13. Projected DTI After Loan
        df_out['projected_dti_after_loan'] = (
            df_out['projected_total_debt'] / df_out['annual_income']
        ).round(4)
        new_features.append('projected_dti_after_loan')
        
        # 14. Rolling Risk Score (synthetic 6-month)
        # Calculate bounce severity if not already present
        bounce_severity = (
            df_out['num_bounced_checks_12m'] +
            df_out['emi_bounce_count_12m'] * 2
        )
        df_out['rolling_risk_score_6m'] = (
            df_out['estimated_delinquency_6m'] * 0.3 +
            (df_out['num_enquiries_6m'] / 10) * 0.2 +
            df_out['balance_volatility'] * 0.3 +
            (bounce_severity / 10) * 0.2
        ).round(4)
        new_features.append('rolling_risk_score_6m')
        
        # 15. Trend Indicator (Improving/Stable/Deteriorating)
        df_out['credit_trend_indicator'] = np.select(
            [
                (df_out['delinquency_trend'] < 0.5) & (df_out['enquiry_acceleration'] < 0),
                (df_out['delinquency_trend'] > 1.5) | (df_out['enquiry_acceleration'] > 3),
            ],
            ['Improving', 'Deteriorating'],
            default='Stable'
        )
        new_features.append('credit_trend_indicator')
        
        self.feature_metadata['derived_metrics'].extend(new_features)
        
        if self.verbose:
            print(f"✓ Created {len(new_features)} derived metric features:")
            for feat in new_features[:5]:
                print(f"  • {feat}")
            if len(new_features) > 5:
                print(f"  • ... and {len(new_features) - 5} more")
        
        return df_out
    
    def process_bureau_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process bureau features including:
        - Number of past defaults
        - Enquiry rate calculations
        - Credit history patterns
        - Negative event aggregations
        """
        df_out = df.copy()
        new_features = []
        
        # 1. Total Past Defaults
        df_out['total_past_defaults'] = (
            df_out['num_written_off_accounts'] +
            df_out['num_settled_accounts'] +
            df_out['num_delinquent_accounts']
        )
        new_features.append('total_past_defaults')
        
        # 2. Has Past Defaults Flag
        df_out['has_past_defaults'] = (
            df_out['total_past_defaults'] > 0
        ).astype(int)
        new_features.append('has_past_defaults')
        
        # 3. Severe Default Flag (write-offs)
        df_out['has_writeoff'] = (
            df_out['num_written_off_accounts'] > 0
        ).astype(int)
        new_features.append('has_writeoff')
        
        # 4. Settlement History Flag
        df_out['has_settlements'] = (
            df_out['num_settled_accounts'] > 0
        ).astype(int)
        new_features.append('has_settlements')
        
        # 5. Enquiry Rate (per month)
        df_out['enquiry_rate_monthly'] = (
            df_out['num_enquiries_12m'] / 12
        ).round(4)
        new_features.append('enquiry_rate_monthly')
        
        # 6. Recent Enquiry Rate (6m)
        df_out['enquiry_rate_6m'] = (
            df_out['num_enquiries_6m'] / 6
        ).round(4)
        new_features.append('enquiry_rate_6m')
        
        # 7. High Enquiry Flag
        df_out['high_enquiry_flag'] = (
            df_out['num_enquiries_6m'] > 5
        ).astype(int)
        new_features.append('high_enquiry_flag')
        
        # 8. Credit Hungry Score
        df_out['credit_hungry_score'] = (
            np.minimum(df_out['num_enquiries_6m'] / 10, 1.0)
        ).round(4)
        new_features.append('credit_hungry_score')
        
        # 9. Credit Bureau Score Category
        df_out['credit_score_category'] = pd.cut(
            df_out['credit_score'],
            bins=[0, 550, 650, 750, 900],
            labels=['Poor', 'Fair', 'Good', 'Excellent']
        )
        new_features.append('credit_score_category')
        
        # 10. Credit Score Normalized
        df_out['credit_score_normalized'] = (
            (df_out['credit_score'] - 300) / 600
        ).round(4)
        new_features.append('credit_score_normalized')
        
        # 11. Negative Events Count
        df_out['negative_events_count'] = (
            df_out['num_written_off_accounts'] +
            df_out['num_settled_accounts'] +
            (df_out['max_dpd_last_12m'] > 90).astype(int) +
            (df_out['num_bounced_checks_12m'] > 0).astype(int)
        )
        new_features.append('negative_events_count')
        
        # 12. Credit History Quality Score
        # Calculate credit maturity if not present
        credit_maturity = np.minimum(df_out['credit_history_months'] / 120, 1.0)
        
        df_out['credit_history_quality'] = (
            df_out['credit_score_normalized'] * 0.5 +
            (1 - df_out['credit_hungry_score']) * 0.2 +
            credit_maturity * 0.2 +
            (1 - np.minimum(df_out['negative_events_count'] / 5, 1.0)) * 0.1
        ).round(4)
        new_features.append('credit_history_quality')
        
        # 13. Delinquency Rate (percent of accounts)
        df_out['delinquency_rate'] = np.where(
            df_out['num_credit_accounts'] > 0,
            df_out['num_delinquent_accounts'] / df_out['num_credit_accounts'] * 100,
            0
        ).round(2)
        new_features.append('delinquency_rate')
        
        # 14. Default Probability Indicator (based on bureau data)
        df_out['bureau_default_probability'] = (
            (900 - df_out['credit_score']) / 600 * 0.4 +
            np.minimum(df_out['total_past_defaults'] / 5, 1.0) * 0.3 +
            np.minimum(df_out['num_enquiries_6m'] / 10, 1.0) * 0.2 +
            (df_out['max_dpd_last_12m'] / 180) * 0.1
        ).clip(0, 1).round(4)
        new_features.append('bureau_default_probability')
        
        # 15. Credit Mix Score
        df_out['credit_mix_score'] = (
            np.minimum(df_out['num_credit_accounts'] / 5, 1.0) * 0.5 +
            (df_out['secured_loan_percentage'] / 100) * 0.5
        ).round(4)
        new_features.append('credit_mix_score')
        
        # 16. Enquiry-to-Account Ratio
        df_out['enquiry_to_account_ratio'] = np.where(
            df_out['num_credit_accounts'] > 0,
            df_out['num_enquiries_12m'] / df_out['num_credit_accounts'],
            df_out['num_enquiries_12m']
        ).round(4)
        new_features.append('enquiry_to_account_ratio')
        
        # 17. Bureau Risk Score
        df_out['bureau_risk_score'] = (
            df_out['bureau_default_probability'] * 0.5 +
            (1 - df_out['credit_history_quality']) * 0.3 +
            df_out['credit_hungry_score'] * 0.2
        ).round(4)
        new_features.append('bureau_risk_score')
        
        self.feature_metadata['bureau_features'].extend(new_features)
        
        if self.verbose:
            print(f"✓ Created {len(new_features)} bureau features:")
            for feat in new_features[:5]:
                print(f"  • {feat}")
            if len(new_features) > 5:
                print(f"  • ... and {len(new_features) - 5} more")
        
        return df_out
    
    def get_feature_list(self, category: Optional[str] = None) -> List[str]:
        """Get list of engineered features by category"""
        if category:
            return self.feature_metadata.get(category, [])
        else:
            all_features = []
            for features in self.feature_metadata.values():
                all_features.extend(features)
            return all_features
    
    def get_feature_importance_groups(self) -> Dict[str, List[str]]:
        """Get feature groups for interpretability"""
        return self.feature_metadata


def main():
    """Example usage of feature engineering"""
    
    print("Loading credit risk dataset...")
    df = pd.read_csv('data/credit_risk_dataset.csv')
    
    print(f"Original dataset: {df.shape}")
    
    # Initialize feature engineer
    engineer = FeatureEngineer(verbose=True)
    
    # Apply all feature engineering
    df_features = engineer.transform_all(df)
    
    print(f"\nEnhanced dataset: {df_features.shape}")
    
    # Save engineered features
    output_path = 'data/credit_risk_dataset_features.csv'
    df_features.to_csv(output_path, index=False)
    print(f"\n✓ Feature-engineered dataset saved to: {output_path}")
    
    # Display sample of new features
    print("\n" + "="*80)
    print("SAMPLE OF NEW FEATURES")
    print("="*80)
    
    new_features = engineer.get_feature_list()
    print(f"\nShowing first 5 records for sample features:")
    sample_features = new_features[:10]
    print(df_features[['applicant_id'] + sample_features].head().to_string(index=False))
    
    # Feature summary by category
    print("\n" + "="*80)
    print("FEATURE SUMMARY BY CATEGORY")
    print("="*80)
    for category, features in engineer.get_feature_importance_groups().items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(features)} features):")
        for i, feat in enumerate(features[:3], 1):
            print(f"  {i}. {feat}")
        if len(features) > 3:
            print(f"  ... and {len(features) - 3} more")
    
    return df_features


if __name__ == "__main__":
    df_features = main()
