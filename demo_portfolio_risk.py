"""
Demonstration of Portfolio Risk Overview Dashboard
Shows comprehensive visualization of predicted risk scores including:
- Histogram of risk score distribution
- Risk category analysis
- Segmented risk views
- Comprehensive dashboard
"""

import pandas as pd
import numpy as np
from portfolio_risk_dashboard import PortfolioRiskDashboard
import os
import warnings
warnings.filterwarnings('ignore')


def main():
    print("=" * 80)
    print("PORTFOLIO RISK OVERVIEW DASHBOARD DEMO")
    print("=" * 80)
    
    # ============================================================================
    # STEP 1: Initialize Dashboard
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Initializing Portfolio Risk Dashboard")
    print("=" * 80)
    
    dashboard = PortfolioRiskDashboard()
    print("✓ Dashboard initialized with default styling")
    
    # ============================================================================
    # STEP 2: Load Prediction Data
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Loading Prediction Data")
    print("=" * 80)
    
    predictions_file = "models/validation_predictions.csv"
    full_data_file = "data/credit_risk_dataset_features.csv"
    
    # Check if files exist
    if not os.path.exists(predictions_file):
        print(f"❌ Error: {predictions_file} not found!")
        return
    
    if not os.path.exists(full_data_file):
        print(f"⚠ Warning: {full_data_file} not found. Loading predictions only.")
        full_data_file = None
    
    # Load data
    portfolio_data = dashboard.load_predictions(predictions_file, full_data_file)
    
    print(f"\n📊 Data loaded:")
    print(f"   Records: {len(portfolio_data):,}")
    print(f"   Columns: {portfolio_data.shape[1]}")
    print(f"\n   Available columns:")
    print(f"   {portfolio_data.columns.tolist()[:10]}...")
    
    # ============================================================================
    # STEP 3: Generate Risk Summary Statistics
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Generating Risk Summary Statistics")
    print("=" * 80)
    
    summary = dashboard.generate_risk_summary()
    
    print(f"\n📈 PORTFOLIO STATISTICS:")
    print(f"   Total Portfolio:      {summary['total_portfolio']:,}")
    print(f"   Mean Risk Score:      {summary['mean_risk']:.4f}")
    print(f"   Median Risk Score:    {summary['median_risk']:.4f}")
    print(f"   Std Deviation:        {summary['std_risk']:.4f}")
    print(f"   Score Range:          [{summary['min_risk']:.4f}, {summary['max_risk']:.4f}]")
    
    print(f"\n📊 RISK DISTRIBUTION:")
    print(f"   Low Risk:             {summary['low_risk_count']:,} ({summary['low_risk_pct']:.1f}%)")
    print(f"   Medium Risk:          {summary['medium_risk_count']:,} ({summary['medium_risk_pct']:.1f}%)")
    print(f"   High Risk:            {summary['high_risk_count']:,} ({summary['high_risk_pct']:.1f}%)")
    
    # ============================================================================
    # STEP 4: Create Main Risk Histogram
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Creating Risk Score Histogram")
    print("=" * 80)
    
    print("\n📊 Generating histogram with 50 bins...")
    dashboard.plot_risk_histogram(
        bins=50,
        save_path="visualizations/risk_histogram.png",
        show=False
    )
    print("✓ Main histogram created")
    
    # ============================================================================
    # STEP 5: Create Risk Categories Bar Chart
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Creating Risk Categories Chart")
    print("=" * 80)
    
    print("\n📊 Generating risk categories bar chart...")
    dashboard.plot_risk_categories(
        save_path="visualizations/risk_categories.png",
        show=False
    )
    print("✓ Risk categories chart created")
    
    # ============================================================================
    # STEP 6: Create Segmented Views (if full data available)
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 6: Creating Segmented Risk Views")
    print("=" * 80)
    
    if full_data_file and 'city' in portfolio_data.columns:
        print("\n📊 Generating risk by city...")
        dashboard.plot_risk_by_segment(
            segment_col='city',
            top_n=10,
            save_path="visualizations/risk_by_city.png",
            show=False
        )
        print("✓ Risk by city chart created")
        
        print("\n📊 Generating risk by loan purpose...")
        if 'loan_purpose' in portfolio_data.columns:
            dashboard.plot_risk_by_segment(
                segment_col='loan_purpose',
                top_n=8,
                save_path="visualizations/risk_by_loan_purpose.png",
                show=False
            )
            print("✓ Risk by loan purpose chart created")
        
        print("\n📊 Generating risk by employment type...")
        if 'employment_type' in portfolio_data.columns:
            dashboard.plot_risk_by_segment(
                segment_col='employment_type',
                top_n=8,
                save_path="visualizations/risk_by_employment.png",
                show=False
            )
            print("✓ Risk by employment type chart created")
    else:
        print("⚠ Skipping segmented views (full data not available)")
    
    # ============================================================================
    # STEP 7: Create Risk Heatmap
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 7: Creating Risk Heatmap")
    print("=" * 80)
    
    if full_data_file and 'gender' in portfolio_data.columns and 'employment_type' in portfolio_data.columns:
        print("\n📊 Generating risk heatmap (gender vs employment type)...")
        dashboard.plot_risk_heatmap(
            row_col='gender',
            col_col='employment_type',
            save_path="visualizations/risk_heatmap.png",
            show=False
        )
        print("✓ Risk heatmap created")
    else:
        print("⚠ Skipping heatmap (required columns not available)")
    
    # ============================================================================
    # STEP 8: Create Comprehensive Dashboard
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 8: Creating Comprehensive Dashboard")
    print("=" * 80)
    
    print("\n📊 Generating comprehensive multi-panel dashboard...")
    dashboard.plot_comprehensive_dashboard(
        figsize=(16, 10),
        save_path="visualizations/portfolio_dashboard.png",
        show=False
    )
    print("✓ Comprehensive dashboard created")
    
    # ============================================================================
    # STEP 9: Detailed Risk Analysis
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 9: Detailed Risk Analysis")
    print("=" * 80)
    
    # Decile analysis
    print("\n📊 RISK SCORE DECILE ANALYSIS:")
    portfolio_data['decile'] = pd.qcut(
        portfolio_data['predicted_probability'], 
        q=10, 
        labels=False,
        duplicates='drop'
    ) + 1
    
    decile_stats = portfolio_data.groupby('decile')['predicted_probability'].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(4)
    
    print(decile_stats.to_string())
    
    # Risk concentration
    print(f"\n📊 RISK CONCENTRATION:")
    high_risk_threshold = 0.6
    high_risk_pct = (portfolio_data['predicted_probability'] >= high_risk_threshold).sum() / len(portfolio_data) * 100
    print(f"   Applicants with risk ≥ {high_risk_threshold}: {high_risk_pct:.1f}%")
    
    very_high_risk_threshold = 0.75
    very_high_risk_pct = (portfolio_data['predicted_probability'] >= very_high_risk_threshold).sum() / len(portfolio_data) * 100
    print(f"   Applicants with risk ≥ {very_high_risk_threshold}: {very_high_risk_pct:.1f}%")
    
    # ============================================================================
    # STEP 10: Print Comprehensive Summary Report
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 10: Comprehensive Summary Report")
    print("=" * 80)
    print()
    
    dashboard.print_summary_report()
    
    # ============================================================================
    # STEP 11: Export Summary to CSV
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 11: Exporting Summary Data")
    print("=" * 80)
    
    # Export summary statistics
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv("visualizations/portfolio_risk_summary.csv", index=False)
    print("✓ Summary statistics exported to: visualizations/portfolio_risk_summary.csv")
    
    # Export risk categories breakdown
    category_breakdown = portfolio_data['risk_category'].value_counts().reset_index()
    category_breakdown.columns = ['Risk_Category', 'Count']
    category_breakdown['Percentage'] = (category_breakdown['Count'] / len(portfolio_data) * 100).round(2)
    category_breakdown.to_csv("visualizations/risk_categories_breakdown.csv", index=False)
    print("✓ Risk categories exported to: visualizations/risk_categories_breakdown.csv")
    
    # Export decile analysis
    decile_stats.to_csv("visualizations/risk_decile_analysis.csv")
    print("✓ Decile analysis exported to: visualizations/risk_decile_analysis.csv")
    
    # ============================================================================
    # Summary of Generated Files
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ PORTFOLIO RISK OVERVIEW COMPLETE")
    print("=" * 80)
    
    print("\n📁 Generated Visualizations:")
    viz_files = [
        "visualizations/risk_histogram.png",
        "visualizations/risk_categories.png",
        "visualizations/portfolio_dashboard.png"
    ]
    
    if os.path.exists("visualizations/risk_by_city.png"):
        viz_files.extend([
            "visualizations/risk_by_city.png",
            "visualizations/risk_by_loan_purpose.png",
            "visualizations/risk_by_employment.png"
        ])
    
    if os.path.exists("visualizations/risk_heatmap.png"):
        viz_files.append("visualizations/risk_heatmap.png")
    
    for i, file in enumerate(viz_files, 1):
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"   {i}. {file} ({size:.1f} KB)")
    
    print("\n📁 Generated Data Files:")
    data_files = [
        "visualizations/portfolio_risk_summary.csv",
        "visualizations/risk_categories_breakdown.csv",
        "visualizations/risk_decile_analysis.csv"
    ]
    
    for i, file in enumerate(data_files, 1):
        if os.path.exists(file):
            print(f"   {i}. {file}")
    
    print("\n" + "=" * 80)
    
    # Key insights
    print("\n💡 KEY INSIGHTS:")
    print(f"   • Portfolio has {summary['total_portfolio']:,} applicants")
    print(f"   • Average risk score: {summary['mean_risk']:.3f}")
    print(f"   • {summary['high_risk_pct']:.1f}% of portfolio is high risk")
    print(f"   • Risk scores range from {summary['min_risk']:.3f} to {summary['max_risk']:.3f}")
    
    if summary['high_risk_pct'] > 30:
        print(f"   ⚠ HIGH CONCENTRATION: {summary['high_risk_pct']:.1f}% high-risk applicants")
    elif summary['high_risk_pct'] > 20:
        print(f"   ⚠ MODERATE CONCENTRATION: {summary['high_risk_pct']:.1f}% high-risk applicants")
    else:
        print(f"   ✓ HEALTHY PORTFOLIO: Only {summary['high_risk_pct']:.1f}% high-risk applicants")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Create visualizations directory if it doesn't exist
    os.makedirs("visualizations", exist_ok=True)
    main()
