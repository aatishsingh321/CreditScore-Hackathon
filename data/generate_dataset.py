"""
Credit Risk Scoring - Synthetic Dataset Generator
Generates realistic data simulating:
- Core Banking System data
- Credit Bureau data  
- Transaction database records
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_APPLICANTS = 10000

def generate_applicant_demographics(n):
    """Generate loan applicant demographic data (Core Banking)"""
    
    genders = np.random.choice(['Male', 'Female'], n, p=[0.6, 0.4])
    ages = np.random.normal(35, 10, n).clip(21, 65).astype(int)
    
    education_levels = np.random.choice(
        ['High School', 'Bachelor', 'Master', 'PhD', 'Other'],
        n, p=[0.25, 0.45, 0.20, 0.05, 0.05]
    )
    
    marital_status = np.random.choice(
        ['Single', 'Married', 'Divorced', 'Widowed'],
        n, p=[0.30, 0.55, 0.12, 0.03]
    )
    
    dependents = np.random.poisson(1.5, n).clip(0, 6)
    
    residence_types = np.random.choice(
        ['Owned', 'Rented', 'Mortgaged', 'Living with Parents'],
        n, p=[0.30, 0.35, 0.25, 0.10]
    )
    
    years_at_residence = np.random.exponential(5, n).clip(0, 30).astype(int)
    
    cities = np.random.choice(
        ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 
         'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Other'],
        n, p=[0.15, 0.15, 0.12, 0.10, 0.10, 0.08, 0.08, 0.07, 0.05, 0.10]
    )
    
    return pd.DataFrame({
        'applicant_id': [f'APP{str(i).zfill(6)}' for i in range(1, n+1)],
        'gender': genders,
        'age': ages,
        'education': education_levels,
        'marital_status': marital_status,
        'dependents': dependents,
        'residence_type': residence_types,
        'years_at_current_residence': years_at_residence,
        'city': cities
    })


def generate_employment_data(n):
    """Generate employment and income data (Core Banking)"""
    
    employment_types = np.random.choice(
        ['Salaried', 'Self-Employed', 'Business Owner', 'Freelancer', 'Retired'],
        n, p=[0.55, 0.20, 0.15, 0.07, 0.03]
    )
    
    industries = np.random.choice(
        ['IT/Software', 'Banking/Finance', 'Healthcare', 'Manufacturing', 
         'Retail', 'Education', 'Government', 'Real Estate', 'Other'],
        n, p=[0.20, 0.15, 0.12, 0.12, 0.10, 0.10, 0.08, 0.05, 0.08]
    )
    
    # Annual income based on employment type
    base_incomes = {
        'Salaried': (400000, 150000),
        'Self-Employed': (600000, 300000),
        'Business Owner': (800000, 500000),
        'Freelancer': (350000, 200000),
        'Retired': (250000, 100000)
    }
    
    annual_incomes = []
    for emp_type in employment_types:
        mean, std = base_incomes[emp_type]
        income = max(100000, np.random.normal(mean, std))
        annual_incomes.append(round(income, -3))
    
    years_employed = np.random.exponential(6, n).clip(0, 35).astype(int)
    years_with_current_employer = np.minimum(
        np.random.exponential(3, n).clip(0, 20).astype(int),
        years_employed
    )
    
    return pd.DataFrame({
        'employment_type': employment_types,
        'industry': industries,
        'annual_income': annual_incomes,
        'years_employed': years_employed,
        'years_with_current_employer': years_with_current_employer
    })


def generate_loan_application_data(n, annual_incomes):
    """Generate loan application details (Core Banking)"""
    
    loan_purposes = np.random.choice(
        ['Home Loan', 'Personal Loan', 'Auto Loan', 'Education Loan', 
         'Business Loan', 'Credit Card', 'Consumer Durable'],
        n, p=[0.25, 0.25, 0.15, 0.10, 0.10, 0.10, 0.05]
    )
    
    # Loan amount based on purpose and income
    loan_amounts = []
    tenures = []
    interest_rates = []
    
    for i, purpose in enumerate(loan_purposes):
        income = annual_incomes[i]
        
        if purpose == 'Home Loan':
            amount = np.random.uniform(2, 8) * income
            tenure = np.random.choice([120, 180, 240, 300, 360])
            rate = np.random.uniform(7.5, 9.5)
        elif purpose == 'Personal Loan':
            amount = np.random.uniform(0.5, 3) * income
            tenure = np.random.choice([12, 24, 36, 48, 60])
            rate = np.random.uniform(10.5, 18)
        elif purpose == 'Auto Loan':
            amount = np.random.uniform(1, 4) * income
            tenure = np.random.choice([36, 48, 60, 72, 84])
            rate = np.random.uniform(8, 12)
        elif purpose == 'Education Loan':
            amount = np.random.uniform(1, 5) * income
            tenure = np.random.choice([60, 84, 120, 180])
            rate = np.random.uniform(8, 11)
        elif purpose == 'Business Loan':
            amount = np.random.uniform(2, 10) * income
            tenure = np.random.choice([36, 48, 60, 84, 120])
            rate = np.random.uniform(11, 16)
        elif purpose == 'Credit Card':
            amount = np.random.uniform(0.1, 0.5) * income
            tenure = 12  # Revolving
            rate = np.random.uniform(24, 42)
        else:  # Consumer Durable
            amount = np.random.uniform(0.1, 0.3) * income
            tenure = np.random.choice([6, 9, 12, 18, 24])
            rate = np.random.uniform(12, 18)
        
        loan_amounts.append(round(amount, -3))
        tenures.append(tenure)
        interest_rates.append(round(rate, 2))
    
    application_dates = [
        datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365))
        for _ in range(n)
    ]
    
    return pd.DataFrame({
        'loan_purpose': loan_purposes,
        'loan_amount_requested': loan_amounts,
        'loan_tenure_months': tenures,
        'interest_rate': interest_rates,
        'application_date': application_dates
    })


def generate_credit_bureau_data(n):
    """Generate credit bureau data (Bureau API)"""
    
    # Credit scores (CIBIL-like: 300-900)
    credit_scores = np.random.normal(700, 80, n).clip(300, 900).astype(int)
    
    # Number of existing credit accounts
    num_credit_accounts = np.random.poisson(3, n).clip(0, 15)
    num_active_accounts = np.minimum(
        np.random.poisson(2, n).clip(0, 10),
        num_credit_accounts
    )
    
    # Credit history length in months
    credit_history_months = np.random.exponential(60, n).clip(0, 360).astype(int)
    
    # Delinquency data
    num_delinquent_accounts = np.random.choice(
        [0, 1, 2, 3, 4, 5],
        n, p=[0.60, 0.20, 0.10, 0.05, 0.03, 0.02]
    )
    
    # Days past due in last 12 months
    max_dpd_12m = np.where(
        num_delinquent_accounts > 0,
        np.random.choice([30, 60, 90, 120, 180], n, p=[0.40, 0.25, 0.20, 0.10, 0.05]),
        0
    )
    
    # Number of enquiries
    num_enquiries_6m = np.random.poisson(2, n).clip(0, 15)
    num_enquiries_12m = num_enquiries_6m + np.random.poisson(2, n).clip(0, 10)
    
    # Total outstanding debt
    total_outstanding = np.random.exponential(500000, n).clip(0, 10000000)
    
    # Secured vs Unsecured ratio
    secured_loan_pct = np.random.uniform(0, 1, n)
    
    # Written-off accounts
    num_written_off = np.random.choice(
        [0, 1, 2, 3],
        n, p=[0.85, 0.10, 0.04, 0.01]
    )
    
    # Settlement accounts
    num_settled = np.random.choice(
        [0, 1, 2],
        n, p=[0.90, 0.08, 0.02]
    )
    
    return pd.DataFrame({
        'credit_score': credit_scores,
        'num_credit_accounts': num_credit_accounts,
        'num_active_accounts': num_active_accounts,
        'credit_history_months': credit_history_months,
        'num_delinquent_accounts': num_delinquent_accounts,
        'max_dpd_last_12m': max_dpd_12m,
        'num_enquiries_6m': num_enquiries_6m,
        'num_enquiries_12m': num_enquiries_12m,
        'total_outstanding_debt': total_outstanding.round(-2),
        'secured_loan_percentage': (secured_loan_pct * 100).round(1),
        'num_written_off_accounts': num_written_off,
        'num_settled_accounts': num_settled
    })


def generate_transaction_data(n, annual_incomes):
    """Generate transaction/behavioral data (Transaction Database)"""
    
    # Monthly average balance
    avg_monthly_balance = np.array(annual_incomes) * np.random.uniform(0.05, 0.3, n)
    
    # Balance volatility (std/mean)
    balance_volatility = np.random.exponential(0.3, n).clip(0.05, 2)
    
    # Monthly spending patterns
    avg_monthly_spending = np.array(annual_incomes) / 12 * np.random.uniform(0.4, 0.9, n)
    
    # Spending categories
    essential_spending_pct = np.random.uniform(0.3, 0.7, n)
    discretionary_spending_pct = 1 - essential_spending_pct
    
    # Payment behavior
    num_bounced_checks_12m = np.random.choice(
        [0, 1, 2, 3, 4, 5],
        n, p=[0.70, 0.15, 0.08, 0.04, 0.02, 0.01]
    )
    
    # Salary credits (for salaried)
    salary_credit_regularity = np.random.uniform(0.7, 1.0, n)  # % of months with salary credit
    
    # UPI/Digital transactions
    num_digital_txns_monthly = np.random.poisson(30, n).clip(0, 200)
    
    # Cash withdrawals
    cash_withdrawal_pct = np.random.uniform(0.05, 0.4, n)
    
    # Minimum balance breaches
    min_balance_breaches_12m = np.random.poisson(1, n).clip(0, 12)
    
    # Loan EMI bounce
    emi_bounce_count_12m = np.random.choice(
        [0, 1, 2, 3, 4],
        n, p=[0.75, 0.15, 0.06, 0.03, 0.01]
    )
    
    return pd.DataFrame({
        'avg_monthly_balance': avg_monthly_balance.round(-2),
        'balance_volatility': balance_volatility.round(3),
        'avg_monthly_spending': avg_monthly_spending.round(-2),
        'essential_spending_pct': (essential_spending_pct * 100).round(1),
        'discretionary_spending_pct': (discretionary_spending_pct * 100).round(1),
        'num_bounced_checks_12m': num_bounced_checks_12m,
        'salary_credit_regularity': (salary_credit_regularity * 100).round(1),
        'num_digital_txns_monthly': num_digital_txns_monthly,
        'cash_withdrawal_pct': (cash_withdrawal_pct * 100).round(1),
        'min_balance_breaches_12m': min_balance_breaches_12m,
        'emi_bounce_count_12m': emi_bounce_count_12m
    })


def generate_target_variable(df):
    """
    Generate target variable (default) based on risk factors.
    Target: 1 = Default, 0 = No Default
    """
    
    # Base default probability
    default_prob = np.zeros(len(df))
    
    # Credit Score impact (higher score = lower risk)
    credit_score_factor = (900 - df['credit_score']) / 600
    default_prob += credit_score_factor * 0.15
    
    # Debt-to-Income impact
    dti = df['total_outstanding_debt'] / df['annual_income']
    default_prob += np.clip(dti - 0.3, 0, 1) * 0.10
    
    # Delinquency history
    default_prob += df['num_delinquent_accounts'] * 0.05
    default_prob += (df['max_dpd_last_12m'] / 180) * 0.10
    
    # Written-off and settled accounts
    default_prob += df['num_written_off_accounts'] * 0.08
    default_prob += df['num_settled_accounts'] * 0.04
    
    # Transaction behavior
    default_prob += df['num_bounced_checks_12m'] * 0.03
    default_prob += df['emi_bounce_count_12m'] * 0.05
    default_prob += df['min_balance_breaches_12m'] * 0.02
    
    # Enquiry rate (high enquiries = higher risk)
    default_prob += np.clip(df['num_enquiries_6m'] - 3, 0, 10) * 0.02
    
    # Balance volatility
    default_prob += np.clip(df['balance_volatility'] - 0.5, 0, 1) * 0.05
    
    # Employment stability
    default_prob -= np.clip(df['years_with_current_employer'] / 10, 0, 0.1)
    
    # Clip probability
    default_prob = np.clip(default_prob, 0.02, 0.95)
    
    # Generate binary outcome
    defaults = np.random.binomial(1, default_prob)
    
    return defaults, default_prob


def calculate_derived_features(df):
    """Calculate derived features for modeling"""
    
    # Debt-to-Income Ratio
    df['debt_to_income_ratio'] = (df['total_outstanding_debt'] / df['annual_income']).round(3)
    
    # Loan-to-Income Ratio
    df['loan_to_income_ratio'] = (df['loan_amount_requested'] / df['annual_income']).round(3)
    
    # Credit Utilization (estimated)
    df['credit_utilization'] = np.random.uniform(0.1, 0.9, len(df)).round(3)
    
    # Monthly EMI estimate
    df['estimated_monthly_emi'] = (
        df['loan_amount_requested'] * 
        (df['interest_rate']/100/12) * 
        (1 + df['interest_rate']/100/12)**df['loan_tenure_months'] / 
        ((1 + df['interest_rate']/100/12)**df['loan_tenure_months'] - 1)
    ).round(0)
    
    # EMI-to-Income Ratio
    df['emi_to_income_ratio'] = (df['estimated_monthly_emi'] * 12 / df['annual_income']).round(3)
    
    # Savings Rate (estimated from balance and income)
    df['savings_rate'] = (df['avg_monthly_balance'] * 12 / df['annual_income']).round(3)
    
    # Account Age Factor
    df['account_age_factor'] = (df['credit_history_months'] / 12).round(1)
    
    return df


def main():
    print("Generating Credit Risk Dataset...")
    print(f"Number of applicants: {NUM_APPLICANTS}")
    
    # Generate all data components
    print("\n1. Generating applicant demographics (Core Banking)...")
    demographics = generate_applicant_demographics(NUM_APPLICANTS)
    
    print("2. Generating employment data (Core Banking)...")
    employment = generate_employment_data(NUM_APPLICANTS)
    
    print("3. Generating loan application data (Core Banking)...")
    loan_app = generate_loan_application_data(NUM_APPLICANTS, employment['annual_income'].values)
    
    print("4. Generating credit bureau data (Bureau API)...")
    bureau = generate_credit_bureau_data(NUM_APPLICANTS)
    
    print("5. Generating transaction data (Transaction Database)...")
    transactions = generate_transaction_data(NUM_APPLICANTS, employment['annual_income'].values)
    
    # Combine all data
    print("\n6. Combining datasets...")
    df = pd.concat([demographics, employment, loan_app, bureau, transactions], axis=1)
    
    # Calculate derived features
    print("7. Calculating derived features...")
    df = calculate_derived_features(df)
    
    # Generate target variable
    print("8. Generating target variable (default)...")
    df['default'], df['default_probability'] = generate_target_variable(df)
    
    # Reorder columns
    id_cols = ['applicant_id', 'application_date']
    target_cols = ['default', 'default_probability']
    other_cols = [c for c in df.columns if c not in id_cols + target_cols]
    df = df[id_cols + other_cols + target_cols]
    
    # Save datasets
    print("\n9. Saving datasets...")
    
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    # Full dataset
    df.to_csv('data/credit_risk_dataset.csv', index=False)
    print(f"   - Full dataset saved: data/credit_risk_dataset.csv ({len(df)} records)")
    
    # Split by source for reference
    core_banking_cols = ['applicant_id', 'application_date', 'gender', 'age', 'education', 
                         'marital_status', 'dependents', 'residence_type', 
                         'years_at_current_residence', 'city', 'employment_type', 
                         'industry', 'annual_income', 'years_employed', 
                         'years_with_current_employer', 'loan_purpose', 
                         'loan_amount_requested', 'loan_tenure_months', 'interest_rate']
    
    bureau_cols = ['applicant_id', 'credit_score', 'num_credit_accounts', 
                   'num_active_accounts', 'credit_history_months', 
                   'num_delinquent_accounts', 'max_dpd_last_12m', 
                   'num_enquiries_6m', 'num_enquiries_12m', 
                   'total_outstanding_debt', 'secured_loan_percentage',
                   'num_written_off_accounts', 'num_settled_accounts']
    
    transaction_cols = ['applicant_id', 'avg_monthly_balance', 'balance_volatility',
                        'avg_monthly_spending', 'essential_spending_pct',
                        'discretionary_spending_pct', 'num_bounced_checks_12m',
                        'salary_credit_regularity', 'num_digital_txns_monthly',
                        'cash_withdrawal_pct', 'min_balance_breaches_12m',
                        'emi_bounce_count_12m']
    
    df[core_banking_cols].to_csv('data/core_banking_data.csv', index=False)
    df[bureau_cols].to_csv('data/bureau_data.csv', index=False)
    df[transaction_cols].to_csv('data/transaction_data.csv', index=False)
    
    print("   - Core Banking data saved: data/core_banking_data.csv")
    print("   - Bureau data saved: data/bureau_data.csv")
    print("   - Transaction data saved: data/transaction_data.csv")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    print(f"\nTotal Records: {len(df)}")
    print(f"Total Features: {len(df.columns)}")
    print(f"\nTarget Variable Distribution:")
    print(f"  - Non-Default (0): {(df['default']==0).sum()} ({(df['default']==0).mean()*100:.1f}%)")
    print(f"  - Default (1): {(df['default']==1).sum()} ({(df['default']==1).mean()*100:.1f}%)")
    
    print(f"\nFeature Categories:")
    print(f"  - Demographics: 9 features")
    print(f"  - Employment: 5 features")
    print(f"  - Loan Application: 4 features")
    print(f"  - Credit Bureau: 12 features")
    print(f"  - Transaction/Behavioral: 11 features")
    print(f"  - Derived Features: 7 features")
    
    print("\nSample Records:")
    print(df.head(3).to_string())
    
    print("\n" + "="*60)
    print("Dataset generation complete!")
    print("="*60)
    
    return df


if __name__ == "__main__":
    df = main()
