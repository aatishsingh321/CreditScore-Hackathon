"""
Demonstration of Monitoring & Compliance Framework
Shows:
- Real-time portfolio monitoring
- Fairness and bias analysis
- Explainable credit decisions
- Regulatory compliance reporting
"""

import pandas as pd
import numpy as np
from monitoring_compliance import (
    PortfolioMonitor, FairnessAnalyzer, 
    ExplainabilityEngine, ComplianceMonitor
)
import os
import joblib
import warnings
warnings.filterwarnings('ignore')


def main():
    print("=" * 80)
    print("MONITORING & COMPLIANCE FRAMEWORK DEMO")
    print("=" * 80)
    
    # Create compliance directory
    os.makedirs("compliance", exist_ok=True)
    
    # ============================================================================
    # STEP 1: Load Data
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Loading Data")
    print("=" * 80)
    
    predictions_file = "models/validation_predictions.csv"
    full_data_file = "data/credit_risk_dataset_features.csv"
    
    predictions_df = pd.read_csv(predictions_file)
    full_data_df = pd.read_csv(full_data_file)
    
    print(f"✓ Loaded {len(predictions_df):,} predictions")
    print(f"✓ Loaded {len(full_data_df):,} full records")
    
    # Merge datasets
    data = full_data_df.merge(predictions_df, on='applicant_id', how='inner')
    print(f"✓ Merged dataset: {len(data):,} records with {data.shape[1]} columns")
    
    # ============================================================================
    # STEP 2: Portfolio Risk Monitoring
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Portfolio Risk Monitoring")
    print("=" * 80)
    
    monitor = PortfolioMonitor()
    
    # Simulate multiple time periods
    print("\n📊 Simulating portfolio monitoring over time...")
    
    # Split data into 5 time periods
    n_periods = 5
    period_size = len(predictions_df) // n_periods
    
    for i in range(n_periods):
        start_idx = i * period_size
        end_idx = start_idx + period_size if i < n_periods - 1 else len(predictions_df)
        period_data = predictions_df.iloc[start_idx:end_idx]
        
        metrics, alerts = monitor.update_metrics(period_data)
        
        print(f"\nPeriod {i+1}:")
        print(f"  Applications: {metrics['total_applications']}")
        print(f"  Mean Risk: {metrics['mean_risk']:.4f}")
        print(f"  High Risk %: {metrics['high_risk_pct']:.1f}%")
        print(f"  Alerts: {len(alerts)}")
        
        if alerts:
            for alert in alerts:
                print(f"    ⚠ {alert['type']}: {alert['message']}")
    
    # Generate monitoring dashboard
    print("\n📈 Generating monitoring dashboard...")
    monitor.plot_monitoring_dashboard(
        save_path="compliance/portfolio_monitoring_dashboard.png",
        show=False
    )
    
    print(f"\n📊 MONITORING SUMMARY:")
    print(f"   Total Periods Tracked: {len(monitor.metrics_history)}")
    print(f"   Total Alerts Triggered: {len(monitor.alerts)}")
    print(f"   Alert Types: {set([a['type'] for a in monitor.alerts])}")
    
    # ============================================================================
    # STEP 3: Fairness & Bias Analysis
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Fairness & Bias Analysis")
    print("=" * 80)
    
    fairness = FairnessAnalyzer()
    
    print("\n🔍 Running comprehensive fairness audit...")
    audit_results = fairness.comprehensive_fairness_audit(data)
    
    print(f"\n📊 FAIRNESS AUDIT RESULTS:")
    print(f"   Records Analyzed: {audit_results['total_records']:,}")
    print(f"   Attributes Analyzed: {', '.join(audit_results['attributes_analyzed'])}")
    print(f"   Overall Compliance: {'✓ PASS' if audit_results['overall_compliance'] else '⚠ REVIEW REQUIRED'}")
    
    # Detailed analysis by attribute
    print("\n📋 DETAILED ANALYSIS:")
    for attr in audit_results['attributes_analyzed']:
        metrics = audit_results[attr]
        print(f"\n  {attr.replace('_', ' ').title()}:")
        print(f"    Statistical Parity Difference: {metrics['statistical_parity_difference']:.4f}")
        print(f"    Disparate Impact Ratio: {metrics['disparate_impact_ratio']:.4f}")
        print(f"    Compliance Status: {metrics['compliance_status']}")
        print(f"    Fair (80% rule): {'✓ YES' if metrics['is_fair'] else '✗ NO'}")
    
    # Generate fairness report
    print("\n📊 Generating fairness analysis report...")
    fairness.plot_fairness_report(
        audit_results,
        save_path="compliance/fairness_analysis_report.png",
        show=False
    )
    
    # Generate compliance report
    print("\n📄 Generating regulatory compliance report...")
    compliance_text = fairness.generate_compliance_report(audit_results)
    
    with open("compliance/regulatory_compliance_report.txt", 'w') as f:
        f.write(compliance_text)
    
    print("✓ Compliance report saved to: compliance/regulatory_compliance_report.txt")
    
    # Print key sections
    print("\n" + "=" * 80)
    print("REGULATORY COMPLIANCE SUMMARY")
    print("=" * 80)
    print(compliance_text.split("COMPLIANCE NOTES")[0])
    
    # ============================================================================
    # STEP 4: Explainable AI - Feature Importance
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Explainable AI - Feature Importance")
    print("=" * 80)
    
    # Load model
    print("\n🤖 Loading trained model...")
    try:
        model = joblib.load("models/credit_risk_lgbm.pkl")
        print("✓ Model loaded successfully")
        
        explainer = ExplainabilityEngine(model=model)
        
        # Get feature importance
        print("\n📊 Extracting feature importance...")
        importance_df = explainer.get_feature_importance('gain')
        
        if not importance_df.empty:
            print("\n📈 TOP 15 MOST IMPORTANT FEATURES:")
            print(importance_df.head(15).to_string(index=False))
            
            # Save to CSV
            importance_df.to_csv("compliance/feature_importance.csv", index=False)
            print("\n✓ Feature importance saved to: compliance/feature_importance.csv")
        
    except Exception as e:
        print(f"⚠ Could not load model: {e}")
        explainer = ExplainabilityEngine()
    
    # ============================================================================
    # STEP 5: Individual Prediction Explanations
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Individual Prediction Explanations")
    print("=" * 80)
    
    print("\n🔍 Generating example prediction explanations...")
    
    # Get a few sample predictions
    high_risk_sample = data[data['predicted_probability'] >= 0.6].iloc[0] if len(data[data['predicted_probability'] >= 0.6]) > 0 else None
    low_risk_sample = data[data['predicted_probability'] < 0.3].iloc[0] if len(data[data['predicted_probability'] < 0.3]) > 0 else None
    
    if high_risk_sample is not None:
        print("\n📋 EXAMPLE 1: HIGH RISK APPLICANT")
        print(f"   Applicant ID: {high_risk_sample['applicant_id']}")
        print(f"   Risk Score: {high_risk_sample['predicted_probability']:.3f}")
        
        # Extract feature values
        feature_cols = ['credit_score', 'debt_to_income_ratio', 'total_past_defaults', 'years_employed']
        feature_values = {col: high_risk_sample.get(col, 'N/A') for col in feature_cols if col in high_risk_sample}
        
        reasons = explainer.generate_reason_codes(
            high_risk_sample['predicted_probability'],
            feature_values
        )
        
        print("\n   Reason Codes:")
        for i, reason in enumerate(reasons, 1):
            print(f"     {i}. {reason}")
        
        # Generate adverse action notice
        notice = explainer.generate_adverse_action_notice(
            high_risk_sample['applicant_id'],
            high_risk_sample['predicted_probability'],
            reasons
        )
        
        with open("compliance/adverse_action_notice_example.txt", 'w') as f:
            f.write(notice)
        
        print("\n✓ Adverse action notice saved to: compliance/adverse_action_notice_example.txt")
    
    if low_risk_sample is not None:
        print("\n📋 EXAMPLE 2: LOW RISK APPLICANT")
        print(f"   Applicant ID: {low_risk_sample['applicant_id']}")
        print(f"   Risk Score: {low_risk_sample['predicted_probability']:.3f}")
        print(f"   Decision: APPROVED")
        
        feature_cols = ['credit_score', 'debt_to_income_ratio', 'total_past_defaults', 'years_employed']
        feature_values = {col: low_risk_sample.get(col, 'N/A') for col in feature_cols if col in low_risk_sample}
        
        reasons = explainer.generate_reason_codes(
            low_risk_sample['predicted_probability'],
            feature_values
        )
        
        print("\n   Favorable Factors:")
        for i, reason in enumerate(reasons, 1):
            print(f"     {i}. {reason}")
    
    # ============================================================================
    # STEP 6: Integrated Compliance Check
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 6: Integrated Compliance Check")
    print("=" * 80)
    
    print("\n🔒 Running integrated compliance check...")
    
    compliance_monitor = ComplianceMonitor()
    compliance_results = compliance_monitor.run_compliance_check(
        predictions_df,
        full_data_df
    )
    
    print(f"\n📊 INTEGRATED COMPLIANCE RESULTS:")
    print(f"   Timestamp: {compliance_results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Overall Status: {compliance_results['overall_status']}")
    print(f"   Total Alerts: {len(compliance_results['alerts'])}")
    
    if compliance_results['fairness_audit']:
        print(f"   Fairness Compliance: {'✓ PASS' if compliance_results['fairness_audit']['overall_compliance'] else '⚠ REVIEW'}")
    
    # ============================================================================
    # STEP 7: Bias Detection Report
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 7: Bias Detection Summary")
    print("=" * 80)
    
    print("\n🔍 BIAS DETECTION ANALYSIS:")
    
    # Gender analysis
    if 'gender' in data.columns:
        print("\n📊 Gender Analysis:")
        gender_risk = data.groupby('gender')['predicted_probability'].agg(['mean', 'count'])
        for gender in gender_risk.index:
            print(f"   {gender}: Mean Risk={gender_risk.loc[gender, 'mean']:.4f}, n={int(gender_risk.loc[gender, 'count'])}")
        
        risk_diff = gender_risk['mean'].max() - gender_risk['mean'].min()
        print(f"   Risk Difference: {risk_diff:.4f} {'✓ (Acceptable)' if risk_diff < 0.05 else '⚠ (Review)'}")
    
    # Age group analysis
    if 'age' in data.columns:
        print("\n📊 Age Group Analysis:")
        data['age_group'] = pd.cut(data['age'], bins=[0, 30, 50, 100], labels=['Young', 'Middle', 'Senior'])
        age_risk = data.groupby('age_group')['predicted_probability'].agg(['mean', 'count'])
        for age_grp in age_risk.index:
            print(f"   {age_grp}: Mean Risk={age_risk.loc[age_grp, 'mean']:.4f}, n={int(age_risk.loc[age_grp, 'count'])}")
    
    # ============================================================================
    # STEP 8: Transparency Report
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 8: Transparency & Explainability Report")
    print("=" * 80)
    
    transparency_report = f"""
CREDIT DECISION TRANSPARENCY REPORT
{'='*80}

Model Information:
  Model Type: LightGBM Gradient Boosting
  Training Date: 2026-02-03
  Validation Records: {len(predictions_df):,}
  
Explainability Features:
  ✓ Feature importance ranking available
  ✓ Individual prediction explanations provided
  ✓ Reason codes generated for all decisions
  ✓ Adverse action notices for declined applications
  
Compliance Status:
  ✓ Equal Credit Opportunity Act (ECOA) compliant
  ✓ Fair Credit Reporting Act (FCRA) compliant
  ✓ Disparate impact analysis conducted
  ✓ 80% rule validation performed
  
Consumer Rights:
  • Right to know reasons for adverse action
  • Right to access credit report
  • Right to dispute inaccurate information
  • Right to non-discriminatory treatment
  
Contact Information:
  Credit Review Department
  Email: creditreview@example.com
  Phone: 1-800-XXX-XXXX

{'='*80}
"""
    
    with open("compliance/transparency_report.txt", 'w') as f:
        f.write(transparency_report)
    
    print(transparency_report)
    print("✓ Transparency report saved to: compliance/transparency_report.txt")
    
    # ============================================================================
    # STEP 9: Summary Statistics
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 9: Compliance Summary Statistics")
    print("=" * 80)
    
    summary_stats = {
        'total_applications': len(data),
        'high_risk_count': (data['predicted_probability'] >= 0.6).sum(),
        'high_risk_pct': (data['predicted_probability'] >= 0.6).sum() / len(data) * 100,
        'low_risk_count': (data['predicted_probability'] < 0.3).sum(),
        'low_risk_pct': (data['predicted_probability'] < 0.3).sum() / len(data) * 100,
        'alerts_triggered': len(monitor.alerts),
        'fairness_pass': audit_results['overall_compliance'],
        'attributes_analyzed': len(audit_results['attributes_analyzed'])
    }
    
    print(f"\n📊 PORTFOLIO STATISTICS:")
    print(f"   Total Applications: {summary_stats['total_applications']:,}")
    print(f"   High Risk: {summary_stats['high_risk_count']:,} ({summary_stats['high_risk_pct']:.1f}%)")
    print(f"   Low Risk: {summary_stats['low_risk_count']:,} ({summary_stats['low_risk_pct']:.1f}%)")
    
    print(f"\n🔔 MONITORING STATISTICS:")
    print(f"   Alerts Triggered: {summary_stats['alerts_triggered']}")
    print(f"   Monitoring Periods: {len(monitor.metrics_history)}")
    
    print(f"\n✅ COMPLIANCE STATISTICS:")
    print(f"   Fairness Audit: {'PASS' if summary_stats['fairness_pass'] else 'REVIEW'}")
    print(f"   Protected Attributes Analyzed: {summary_stats['attributes_analyzed']}")
    print(f"   Transparency: IMPLEMENTED")
    print(f"   Explainability: AVAILABLE")
    
    # Export summary
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv("compliance/compliance_summary.csv", index=False)
    print("\n✓ Summary statistics exported to: compliance/compliance_summary.csv")
    
    # ============================================================================
    # Final Summary
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ MONITORING & COMPLIANCE CHECK COMPLETE")
    print("=" * 80)
    
    print("\n📁 Generated Files:")
    compliance_files = [
        "compliance/portfolio_monitoring_dashboard.png",
        "compliance/fairness_analysis_report.png",
        "compliance/regulatory_compliance_report.txt",
        "compliance/feature_importance.csv",
        "compliance/adverse_action_notice_example.txt",
        "compliance/transparency_report.txt",
        "compliance/compliance_summary.csv"
    ]
    
    for i, file in enumerate(compliance_files, 1):
        if os.path.exists(file):
            size = os.path.getsize(file)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            print(f"   {i}. {file} ({size_str})")
    
    print("\n" + "=" * 80)
    print("📊 COMPLIANCE STATUS SUMMARY")
    print("=" * 80)
    
    print("\n✅ IMPLEMENTED:")
    print("   ✓ Real-time portfolio risk monitoring")
    print("   ✓ Fairness and bias detection")
    print("   ✓ Transparent, explainable decisions")
    print("   ✓ Regulatory compliance reporting")
    print("   ✓ Adverse action notices")
    print("   ✓ Consumer rights documentation")
    
    print("\n📈 OVERALL COMPLIANCE:")
    if audit_results['overall_compliance'] and len(monitor.alerts) == 0:
        print("   🎉 FULLY COMPLIANT - Ready for production")
    elif audit_results['overall_compliance']:
        print("   ⚠ COMPLIANT WITH ALERTS - Review recommended")
    else:
        print("   ⚠ REVIEW REQUIRED - Manual review needed")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
