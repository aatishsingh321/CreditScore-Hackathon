"""
Credit Risk Monitoring & Compliance Framework
Implements:
- Real-time portfolio risk monitoring
- Fairness and bias detection
- Regulatory compliance checks
- Explainable AI (XAI) for transparent decisions
- Model performance tracking
- Alert system for risk thresholds
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class PortfolioMonitor:
    """
    Real-time portfolio risk monitoring dashboard
    
    Tracks:
    - Portfolio risk metrics over time
    - Default rates by segment
    - Risk distribution changes
    - Model performance drift
    - Alert conditions
    """
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.thresholds = {
            'high_risk_pct': 20.0,  # Max % of high-risk applicants
            'mean_risk_increase': 0.05,  # Max mean risk increase
            'default_rate': 0.25,  # Max acceptable default rate
            'auc_drop': 0.05  # Max AUC drop from baseline
        }
    
    def calculate_portfolio_metrics(self, predictions_df: pd.DataFrame) -> Dict:
        """
        Calculate current portfolio metrics
        
        Args:
            predictions_df: DataFrame with predictions
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'timestamp': datetime.now(),
            'total_applications': len(predictions_df),
            'mean_risk': predictions_df['predicted_probability'].mean(),
            'median_risk': predictions_df['predicted_probability'].median(),
            'std_risk': predictions_df['predicted_probability'].std(),
            'high_risk_count': (predictions_df['predicted_probability'] >= 0.6).sum(),
            'high_risk_pct': (predictions_df['predicted_probability'] >= 0.6).sum() / len(predictions_df) * 100,
            'low_risk_pct': (predictions_df['predicted_probability'] < 0.3).sum() / len(predictions_df) * 100,
        }
        
        # Calculate actual default rate if available
        if 'actual' in predictions_df.columns:
            metrics['actual_default_rate'] = predictions_df['actual'].mean()
            metrics['predicted_default_rate'] = (predictions_df['predicted_probability'] >= 0.5).mean()
        
        return metrics
    
    def check_alerts(self, current_metrics: Dict) -> List[Dict]:
        """
        Check for alert conditions
        
        Args:
            current_metrics: Current portfolio metrics
            
        Returns:
            List of triggered alerts
        """
        alerts = []
        
        # High risk concentration alert
        if current_metrics['high_risk_pct'] > self.thresholds['high_risk_pct']:
            alerts.append({
                'type': 'HIGH_RISK_CONCENTRATION',
                'severity': 'HIGH',
                'message': f"High-risk portfolio concentration: {current_metrics['high_risk_pct']:.1f}% (threshold: {self.thresholds['high_risk_pct']}%)",
                'timestamp': current_metrics['timestamp']
            })
        
        # Mean risk increase alert (if history exists)
        if len(self.metrics_history) > 0:
            baseline_risk = self.metrics_history[0]['mean_risk']
            risk_increase = current_metrics['mean_risk'] - baseline_risk
            
            if risk_increase > self.thresholds['mean_risk_increase']:
                alerts.append({
                    'type': 'RISK_INCREASE',
                    'severity': 'MEDIUM',
                    'message': f"Mean risk increased by {risk_increase:.3f} from baseline (threshold: {self.thresholds['mean_risk_increase']})",
                    'timestamp': current_metrics['timestamp']
                })
        
        # Default rate alert
        if 'actual_default_rate' in current_metrics:
            if current_metrics['actual_default_rate'] > self.thresholds['default_rate']:
                alerts.append({
                    'type': 'HIGH_DEFAULT_RATE',
                    'severity': 'CRITICAL',
                    'message': f"Default rate: {current_metrics['actual_default_rate']:.2%} exceeds threshold ({self.thresholds['default_rate']:.2%})",
                    'timestamp': current_metrics['timestamp']
                })
        
        return alerts
    
    def update_metrics(self, predictions_df: pd.DataFrame):
        """Update metrics and check alerts"""
        metrics = self.calculate_portfolio_metrics(predictions_df)
        self.metrics_history.append(metrics)
        
        new_alerts = self.check_alerts(metrics)
        self.alerts.extend(new_alerts)
        
        return metrics, new_alerts
    
    def plot_monitoring_dashboard(self, save_path: Optional[str] = None, show: bool = True):
        """
        Create comprehensive monitoring dashboard
        
        Args:
            save_path: Path to save plot
            show: Whether to display plot
        """
        if len(self.metrics_history) == 0:
            print("No metrics history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Extract time series data
        timestamps = [m['timestamp'] for m in self.metrics_history]
        mean_risks = [m['mean_risk'] for m in self.metrics_history]
        high_risk_pcts = [m['high_risk_pct'] for m in self.metrics_history]
        
        # Plot 1: Mean Risk Over Time
        axes[0, 0].plot(range(len(timestamps)), mean_risks, marker='o', linewidth=2)
        axes[0, 0].set_xlabel('Time Period', fontweight='bold')
        axes[0, 0].set_ylabel('Mean Risk Score', fontweight='bold')
        axes[0, 0].set_title('Portfolio Mean Risk Trend', fontweight='bold')
        axes[0, 0].grid(alpha=0.3)
        
        # Plot 2: High Risk Percentage
        axes[0, 1].plot(range(len(timestamps)), high_risk_pcts, marker='s', color='red', linewidth=2)
        axes[0, 1].axhline(y=self.thresholds['high_risk_pct'], color='orange', linestyle='--', label='Threshold')
        axes[0, 1].set_xlabel('Time Period', fontweight='bold')
        axes[0, 1].set_ylabel('High Risk %', fontweight='bold')
        axes[0, 1].set_title('High Risk Concentration', fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)
        
        # Plot 3: Alert Summary
        alert_counts = {}
        for alert in self.alerts:
            alert_type = alert['type']
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        if alert_counts:
            axes[1, 0].bar(alert_counts.keys(), alert_counts.values(), color='orange', alpha=0.7)
            axes[1, 0].set_xlabel('Alert Type', fontweight='bold')
            axes[1, 0].set_ylabel('Count', fontweight='bold')
            axes[1, 0].set_title('Alert Summary', fontweight='bold')
            axes[1, 0].tick_params(axis='x', rotation=45)
        else:
            axes[1, 0].text(0.5, 0.5, 'No Alerts', ha='center', va='center', fontsize=14)
            axes[1, 0].set_title('Alert Summary', fontweight='bold')
        
        # Plot 4: Current Status
        axes[1, 1].axis('off')
        latest = self.metrics_history[-1]
        status_text = f"""
        CURRENT PORTFOLIO STATUS
        {'='*30}
        Total Applications: {latest['total_applications']:,}
        Mean Risk: {latest['mean_risk']:.4f}
        High Risk %: {latest['high_risk_pct']:.1f}%
        Low Risk %: {latest['low_risk_pct']:.1f}%
        
        ALERTS: {len(self.alerts)} total
        """
        axes[1, 1].text(0.1, 0.5, status_text, fontsize=11, family='monospace', 
                       verticalalignment='center')
        
        plt.tight_layout()
        fig.suptitle('Portfolio Risk Monitoring Dashboard', fontsize=16, fontweight='bold', y=1.00)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Monitoring dashboard saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()


class FairnessAnalyzer:
    """
    Fairness and bias detection for credit risk models
    
    Ensures:
    - Equal treatment across protected groups
    - No discriminatory patterns
    - Regulatory compliance (Equal Credit Opportunity Act)
    """
    
    def __init__(self):
        self.protected_attributes = ['gender', 'age_group', 'marital_status']
        self.fairness_metrics = {}
    
    def analyze_group_fairness(self, data: pd.DataFrame, 
                               protected_attr: str,
                               prediction_col: str = 'predicted_probability') -> Dict:
        """
        Analyze fairness across protected groups
        
        Args:
            data: DataFrame with predictions and demographics
            protected_attr: Protected attribute to analyze
            prediction_col: Column with predictions
            
        Returns:
            Dictionary with fairness metrics
        """
        if protected_attr not in data.columns:
            print(f"Warning: {protected_attr} not found in data")
            return {}
        
        # Group statistics
        group_stats = data.groupby(protected_attr)[prediction_col].agg([
            ('count', 'count'),
            ('mean_risk', 'mean'),
            ('median_risk', 'median'),
            ('std_risk', 'std')
        ]).round(4)
        
        # Statistical parity difference (SPD)
        # SPD = P(positive | group=A) - P(positive | group=B)
        high_risk_rates = data.groupby(protected_attr).apply(
            lambda x: (x[prediction_col] >= 0.6).mean()
        )
        spd = high_risk_rates.max() - high_risk_rates.min()
        
        # Disparate impact ratio
        # DIR = P(positive | group=unprivileged) / P(positive | group=privileged)
        dir_ratio = high_risk_rates.min() / high_risk_rates.max() if high_risk_rates.max() > 0 else 0
        
        metrics = {
            'protected_attribute': protected_attr,
            'group_stats': group_stats,
            'high_risk_rates': high_risk_rates,
            'statistical_parity_difference': spd,
            'disparate_impact_ratio': dir_ratio,
            'is_fair': (spd < 0.1 and dir_ratio > 0.8),  # 80% rule
            'compliance_status': 'PASS' if (spd < 0.1 and dir_ratio > 0.8) else 'REVIEW'
        }
        
        return metrics
    
    def comprehensive_fairness_audit(self, data: pd.DataFrame) -> Dict:
        """
        Run comprehensive fairness audit
        
        Args:
            data: DataFrame with predictions and demographics
            
        Returns:
            Complete fairness audit results
        """
        audit_results = {
            'timestamp': datetime.now(),
            'total_records': len(data),
            'attributes_analyzed': [],
            'overall_compliance': True
        }
        
        for attr in self.protected_attributes:
            if attr in data.columns or attr == 'age_group':
                # Create age groups if needed
                if attr == 'age_group' and 'age' in data.columns:
                    data['age_group'] = pd.cut(data['age'], 
                                               bins=[0, 30, 50, 100], 
                                               labels=['Young', 'Middle', 'Senior'])
                
                if attr in data.columns:
                    metrics = self.analyze_group_fairness(data, attr)
                    audit_results['attributes_analyzed'].append(attr)
                    audit_results[attr] = metrics
                    
                    if not metrics.get('is_fair', False):
                        audit_results['overall_compliance'] = False
        
        return audit_results
    
    def plot_fairness_report(self, audit_results: Dict, 
                            save_path: Optional[str] = None, 
                            show: bool = True):
        """
        Create visual fairness report
        
        Args:
            audit_results: Results from comprehensive_fairness_audit
            save_path: Path to save plot
            show: Whether to display plot
        """
        n_attrs = len(audit_results['attributes_analyzed'])
        if n_attrs == 0:
            print("No fairness metrics to plot")
            return
        
        fig, axes = plt.subplots(1, n_attrs, figsize=(6*n_attrs, 5))
        if n_attrs == 1:
            axes = [axes]
        
        for idx, attr in enumerate(audit_results['attributes_analyzed']):
            metrics = audit_results[attr]
            
            # Plot mean risk by group
            group_stats = metrics['group_stats']
            groups = group_stats.index
            mean_risks = group_stats['mean_risk']
            
            colors = ['green' if metrics['is_fair'] else 'orange'] * len(groups)
            axes[idx].bar(range(len(groups)), mean_risks, color=colors, alpha=0.7, edgecolor='black')
            axes[idx].set_xticks(range(len(groups)))
            axes[idx].set_xticklabels(groups, rotation=45)
            axes[idx].set_ylabel('Mean Risk Score', fontweight='bold')
            axes[idx].set_title(f'{attr.replace("_", " ").title()}\n({metrics["compliance_status"]})', 
                               fontweight='bold')
            axes[idx].grid(axis='y', alpha=0.3)
            
            # Add counts on bars
            for i, (count, risk) in enumerate(zip(group_stats['count'], mean_risks)):
                axes[idx].text(i, risk, f'n={int(count)}\n{risk:.3f}', 
                              ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        fig.suptitle('Fairness Analysis Report', fontsize=16, fontweight='bold', y=1.02)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Fairness report saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def generate_compliance_report(self, audit_results: Dict) -> str:
        """
        Generate text-based compliance report
        
        Args:
            audit_results: Fairness audit results
            
        Returns:
            Formatted report string
        """
        lines = [
            "=" * 80,
            "REGULATORY COMPLIANCE REPORT - FAIRNESS & BIAS ANALYSIS",
            "=" * 80,
            "",
            f"Generated: {audit_results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Records Analyzed: {audit_results['total_records']:,}",
            f"Overall Compliance Status: {'✓ PASS' if audit_results['overall_compliance'] else '⚠ REVIEW REQUIRED'}",
            "",
            "=" * 80,
            "DETAILED ANALYSIS BY PROTECTED ATTRIBUTE",
            "=" * 80,
        ]
        
        for attr in audit_results['attributes_analyzed']:
            metrics = audit_results[attr]
            
            lines.extend([
                "",
                f"Attribute: {attr.replace('_', ' ').title()}",
                "-" * 80,
                f"Statistical Parity Difference: {metrics['statistical_parity_difference']:.4f}",
                f"Disparate Impact Ratio: {metrics['disparate_impact_ratio']:.4f}",
                f"Compliance Status: {metrics['compliance_status']}",
                f"Fair (80% rule): {'✓ YES' if metrics['is_fair'] else '✗ NO'}",
                "",
                "Group Statistics:",
            ])
            
            group_stats = metrics['group_stats']
            for group in group_stats.index:
                lines.append(f"  {group}: Mean={group_stats.loc[group, 'mean_risk']:.4f}, "
                           f"n={int(group_stats.loc[group, 'count'])}")
            
            lines.extend([
                "",
                "High-Risk Rates by Group:",
            ])
            
            for group, rate in metrics['high_risk_rates'].items():
                lines.append(f"  {group}: {rate:.2%}")
        
        lines.extend([
            "",
            "=" * 80,
            "COMPLIANCE NOTES",
            "=" * 80,
            "",
            "• Statistical Parity Difference (SPD) < 0.1 indicates fair treatment",
            "• Disparate Impact Ratio (DIR) > 0.8 satisfies the 80% rule (EEOC guideline)",
            "• All protected attributes should meet both criteria for full compliance",
            "• Manual review recommended for any attributes flagged for REVIEW",
            "",
            "=" * 80,
        ])
        
        return "\n".join(lines)


class ExplainabilityEngine:
    """
    Explainable AI for transparent credit decisions
    
    Provides:
    - Feature importance explanations
    - Individual prediction explanations
    - Reason codes for decisions
    - Adverse action notices
    """
    
    def __init__(self, model=None, feature_names: List[str] = None):
        self.model = model
        self.feature_names = feature_names
    
    def get_feature_importance(self, importance_type: str = 'gain') -> pd.DataFrame:
        """
        Extract feature importance from model
        
        Args:
            importance_type: Type of importance ('gain', 'split', 'weight')
            
        Returns:
            DataFrame with feature importances
        """
        if self.model is None:
            print("No model loaded")
            return pd.DataFrame()
        
        try:
            # LightGBM model
            if hasattr(self.model, 'feature_importance'):
                importance = self.model.feature_importance(importance_type=importance_type)
                importance_df = pd.DataFrame({
                    'feature': self.model.feature_name(),
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                return importance_df
        except Exception as e:
            print(f"Error extracting feature importance: {e}")
            return pd.DataFrame()
    
    def generate_reason_codes(self, prediction: float, 
                             feature_values: Dict,
                             top_n: int = 5) -> List[str]:
        """
        Generate reason codes for a prediction
        
        Args:
            prediction: Predicted risk score
            feature_values: Dictionary of feature values
            top_n: Number of top reasons to return
            
        Returns:
            List of reason codes
        """
        reasons = []
        
        # Risk level determination
        if prediction >= 0.6:
            risk_level = "HIGH RISK"
        elif prediction >= 0.3:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        
        reasons.append(f"Overall Risk Assessment: {risk_level} (Score: {prediction:.3f})")
        
        # Feature-based reasons (simplified)
        if 'credit_score' in feature_values:
            score = feature_values['credit_score']
            if score < 600:
                reasons.append(f"Low credit score ({score})")
            elif score > 750:
                reasons.append(f"Excellent credit score ({score})")
        
        if 'debt_to_income_ratio' in feature_values:
            dti = feature_values['debt_to_income_ratio']
            if dti > 0.4:
                reasons.append(f"High debt-to-income ratio ({dti:.2%})")
        
        if 'total_past_defaults' in feature_values:
            defaults = feature_values['total_past_defaults']
            if defaults > 0:
                reasons.append(f"History of defaults ({int(defaults)} previous defaults)")
        
        if 'years_employed' in feature_values:
            years = feature_values['years_employed']
            if years < 1:
                reasons.append("Limited employment history")
            elif years > 10:
                reasons.append(f"Stable employment history ({int(years)} years)")
        
        return reasons[:top_n]
    
    def generate_adverse_action_notice(self, applicant_id: str,
                                       prediction: float,
                                       reasons: List[str]) -> str:
        """
        Generate adverse action notice for declined applications
        
        Args:
            applicant_id: Applicant identifier
            prediction: Risk prediction
            reasons: List of reason codes
            
        Returns:
            Formatted adverse action notice
        """
        notice = f"""
{'='*80}
ADVERSE ACTION NOTICE
{'='*80}

Date: {datetime.now().strftime('%Y-%m-%d')}
Applicant ID: {applicant_id}
Decision: APPLICATION REQUIRES ADDITIONAL REVIEW

Risk Score: {prediction:.3f} (High Risk Threshold: 0.60)

PRIMARY FACTORS AFFECTING YOUR APPLICATION:

"""
        for i, reason in enumerate(reasons, 1):
            notice += f"  {i}. {reason}\n"
        
        notice += f"""
{'='*80}
YOUR RIGHTS UNDER THE EQUAL CREDIT OPPORTUNITY ACT
{'='*80}

You have the right to:
• Receive a written statement of reasons for adverse action
• Know the specific reasons for denial or unfavorable terms
• Request additional information about the decision
• File a complaint if you believe discrimination has occurred

If you have questions or wish to appeal this decision, please contact:
Credit Review Department
Email: creditreview@example.com
Phone: 1-800-XXX-XXXX

This notice is provided in compliance with the Equal Credit Opportunity Act (15 U.S.C. § 1691 et seq.)
{'='*80}
"""
        return notice


class ComplianceMonitor:
    """
    Integrated compliance monitoring system
    
    Combines:
    - Portfolio monitoring
    - Fairness analysis
    - Explainability
    - Regulatory reporting
    """
    
    def __init__(self):
        self.portfolio_monitor = PortfolioMonitor()
        self.fairness_analyzer = FairnessAnalyzer()
        self.explainability_engine = ExplainabilityEngine()
    
    def run_compliance_check(self, predictions_df: pd.DataFrame,
                            full_data_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Run comprehensive compliance check
        
        Args:
            predictions_df: Predictions data
            full_data_df: Full dataset with demographics
            
        Returns:
            Complete compliance report
        """
        results = {
            'timestamp': datetime.now(),
            'portfolio_metrics': None,
            'fairness_audit': None,
            'alerts': [],
            'overall_status': 'COMPLIANT'
        }
        
        # Portfolio monitoring
        metrics, alerts = self.portfolio_monitor.update_metrics(predictions_df)
        results['portfolio_metrics'] = metrics
        results['alerts'] = alerts
        
        # Fairness analysis
        if full_data_df is not None:
            # Merge predictions with full data
            data_with_predictions = full_data_df.merge(predictions_df, on='applicant_id', how='inner')
            audit_results = self.fairness_analyzer.comprehensive_fairness_audit(data_with_predictions)
            results['fairness_audit'] = audit_results
            
            if not audit_results['overall_compliance']:
                results['overall_status'] = 'REVIEW_REQUIRED'
        
        # Check critical alerts
        if any(a['severity'] == 'CRITICAL' for a in alerts):
            results['overall_status'] = 'ALERT'
        
        return results
    
    def generate_compliance_dashboard(self, save_dir: str = 'compliance'):
        """
        Generate comprehensive compliance dashboard
        
        Args:
            save_dir: Directory to save outputs
        """
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        # Portfolio monitoring dashboard
        self.portfolio_monitor.plot_monitoring_dashboard(
            save_path=f"{save_dir}/portfolio_monitoring.png",
            show=False
        )
        
        print(f"✓ Compliance dashboard generated in {save_dir}/")


if __name__ == "__main__":
    print("Monitoring & Compliance Framework")
    print("=" * 80)
    print("\nComponents:")
    print("1. PortfolioMonitor - Real-time risk monitoring")
    print("2. FairnessAnalyzer - Bias detection and fairness metrics")
    print("3. ExplainabilityEngine - Transparent decision explanations")
    print("4. ComplianceMonitor - Integrated compliance system")
