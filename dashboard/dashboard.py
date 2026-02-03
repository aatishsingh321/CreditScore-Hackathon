"""
Credit Risk Scoring - Dashboard Visualization
Implements:
- Portfolio Risk Overview (histogram of predicted risk scores)
- Model Performance (AUC & KS values display)
- Feature Importance insights
- Fairness Check (risk score by gender)
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve
from sklearn.calibration import calibration_curve
import os
import warnings
warnings.filterwarnings('ignore')


class CreditRiskDashboard:
    """Dashboard visualization for Credit Risk Model"""
    
    def __init__(self, output_dir='dashboard'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.model = None
        self.features = None
        self.metrics = {}
        
    def load_model_and_data(self, model_path='models/credit_risk_lgbm_optimized.pkl',
                            data_path='data/credit_risk_dataset_encoded.csv'):
        """Load model and data"""
        print("Loading model and data...")
        
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.features = model_data['features']
        self.metrics = model_data.get('metrics', {})
        
        self.df = pd.read_csv(data_path)
        self.X = self.df[self.features]
        self.y = self.df['default']
        self.y_pred = self.model.predict(self.X)
        
        print(f"Loaded {len(self.df)} records")
        return self
    
    def calculate_ks_statistic(self, y_true, y_pred_proba):
        """Calculate KS statistic and curve data"""
        df_ks = pd.DataFrame({
            'y_true': y_true,
            'y_pred': y_pred_proba
        }).sort_values('y_pred', ascending=False).reset_index(drop=True)
        
        df_ks['cum_good'] = (df_ks['y_true'] == 0).cumsum() / (df_ks['y_true'] == 0).sum()
        df_ks['cum_bad'] = (df_ks['y_true'] == 1).cumsum() / (df_ks['y_true'] == 1).sum()
        df_ks['ks'] = abs(df_ks['cum_bad'] - df_ks['cum_good'])
        
        ks_statistic = df_ks['ks'].max() * 100
        ks_idx = df_ks['ks'].idxmax()
        
        return ks_statistic, df_ks, ks_idx
    
    def plot_model_performance(self, save_path=None):
        """
        Create Model Performance Dashboard with AUC-ROC and KS Statistics
        """
        if save_path is None:
            save_path = f'{self.output_dir}/model_performance.png'
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle('Credit Risk Model Performance Dashboard', fontsize=16, fontweight='bold')
        
        # 1. ROC Curve with AUC
        ax1 = axes[0, 0]
        fpr, tpr, thresholds = roc_curve(self.y, self.y_pred)
        auc_score = roc_auc_score(self.y, self.y_pred)
        
        ax1.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC Curve (AUC = {auc_score:.4f})')
        ax1.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
        ax1.fill_between(fpr, tpr, alpha=0.3)
        ax1.set_xlabel('False Positive Rate', fontsize=11)
        ax1.set_ylabel('True Positive Rate', fontsize=11)
        ax1.set_title('ROC Curve', fontsize=13, fontweight='bold')
        ax1.legend(loc='lower right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Add AUC value box
        textstr = f'AUC-ROC: {auc_score:.4f}\nTarget: ≥ 0.80\nStatus: {"✓ PASS" if auc_score >= 0.80 else "✗ FAIL"}'
        props = dict(boxstyle='round', facecolor='lightgreen' if auc_score >= 0.80 else 'lightyellow', alpha=0.8)
        ax1.text(0.55, 0.15, textstr, transform=ax1.transAxes, fontsize=10, verticalalignment='top', bbox=props)
        
        # 2. KS Curve
        ax2 = axes[0, 1]
        ks_stat, df_ks, ks_idx = self.calculate_ks_statistic(self.y.values, self.y_pred)
        
        x_axis = np.arange(len(df_ks)) / len(df_ks)
        ax2.plot(x_axis, df_ks['cum_good'].values, 'g-', linewidth=2, label='Cumulative Good (Non-Default)')
        ax2.plot(x_axis, df_ks['cum_bad'].values, 'r-', linewidth=2, label='Cumulative Bad (Default)')
        
        # Mark KS point
        ks_x = ks_idx / len(df_ks)
        ax2.axvline(x=ks_x, color='blue', linestyle='--', linewidth=1.5, label=f'KS = {ks_stat:.2f}')
        ax2.annotate(f'KS = {ks_stat:.2f}', xy=(ks_x, df_ks.loc[ks_idx, 'cum_bad']), 
                    xytext=(ks_x + 0.1, df_ks.loc[ks_idx, 'cum_bad'] - 0.1),
                    fontsize=10, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='blue'))
        
        ax2.set_xlabel('Population Proportion (sorted by score)', fontsize=11)
        ax2.set_ylabel('Cumulative Distribution', fontsize=11)
        ax2.set_title('KS (Kolmogorov-Smirnov) Curve', fontsize=13, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # Add KS value box
        textstr = f'KS Statistic: {ks_stat:.2f}\nTarget: ≥ 30\nStatus: {"✓ PASS" if ks_stat >= 30 else "✗ FAIL"}'
        props = dict(boxstyle='round', facecolor='lightgreen' if ks_stat >= 30 else 'lightyellow', alpha=0.8)
        ax2.text(0.55, 0.45, textstr, transform=ax2.transAxes, fontsize=10, verticalalignment='top', bbox=props)
        
        # 3. Metrics Summary Panel
        ax3 = axes[1, 0]
        ax3.axis('off')
        
        # Calculate Gini
        gini = 2 * auc_score - 1
        
        # Create metrics table
        metrics_data = [
            ['Metric', 'Value', 'Target', 'Status'],
            ['AUC-ROC', f'{auc_score:.4f}', '≥ 0.80', '✓' if auc_score >= 0.80 else '✗'],
            ['KS Statistic', f'{ks_stat:.2f}', '≥ 30', '✓' if ks_stat >= 30 else '✗'],
            ['Gini Coefficient', f'{gini:.4f}', '-', '-'],
            ['Default Rate', f'{self.y.mean()*100:.2f}%', '-', '-'],
            ['Total Records', f'{len(self.df):,}', '-', '-'],
        ]
        
        table = ax3.table(cellText=metrics_data, loc='center', cellLoc='center',
                         colWidths=[0.3, 0.25, 0.2, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)
        
        # Style header row
        for j in range(4):
            table[(0, j)].set_facecolor('#4472C4')
            table[(0, j)].set_text_props(color='white', fontweight='bold')
        
        # Style status column
        for i in range(1, 6):
            if i < 3:  # AUC and KS rows
                color = '#C6EFCE' if metrics_data[i][3] == '✓' else '#FFC7CE'
                table[(i, 3)].set_facecolor(color)
        
        ax3.set_title('Model Performance Metrics', fontsize=13, fontweight='bold', pad=20)
        
        # 4. Gain/Lift Chart
        ax4 = axes[1, 1]
        
        # Calculate gains
        df_gain = pd.DataFrame({
            'y_true': self.y.values,
            'y_pred': self.y_pred
        }).sort_values('y_pred', ascending=False).reset_index(drop=True)
        
        deciles = np.arange(0.1, 1.1, 0.1)
        gains = []
        for d in deciles:
            n = int(len(df_gain) * d)
            captured = df_gain.iloc[:n]['y_true'].sum()
            total = df_gain['y_true'].sum()
            gains.append(captured / total * 100)
        
        ax4.bar(range(1, 11), [gains[0]] + [gains[i] - gains[i-1] for i in range(1, 10)], 
               color='steelblue', alpha=0.7, label='Model Capture Rate')
        ax4.plot(range(1, 11), gains, 'ro-', linewidth=2, markersize=8, label='Cumulative Gain')
        ax4.plot(range(1, 11), [d*100 for d in deciles], 'k--', linewidth=1, label='Random Model')
        
        ax4.set_xlabel('Decile', fontsize=11)
        ax4.set_ylabel('% of Defaults Captured', fontsize=11)
        ax4.set_title('Cumulative Gains Chart', fontsize=13, fontweight='bold')
        ax4.legend(loc='lower right', fontsize=9)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_xticks(range(1, 11))
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"\n✓ Model Performance Dashboard saved to: {save_path}")
        print(f"\n  AUC-ROC: {auc_score:.4f} {'(✓ PASS)' if auc_score >= 0.80 else '(✗ FAIL)'}")
        print(f"  KS Statistic: {ks_stat:.2f} {'(✓ PASS)' if ks_stat >= 30 else '(✗ FAIL)'}")
        print(f"  Gini: {gini:.4f}")
        
        return {'auc': auc_score, 'ks': ks_stat, 'gini': gini}
    
    def plot_risk_score_distribution(self, save_path=None):
        """Plot histogram of predicted risk scores"""
        if save_path is None:
            save_path = f'{self.output_dir}/risk_score_distribution.png'
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Portfolio Risk Score Distribution', fontsize=14, fontweight='bold')
        
        # 1. Overall distribution
        ax1 = axes[0]
        ax1.hist(self.y_pred, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
        ax1.axvline(self.y_pred.mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {self.y_pred.mean():.3f}')
        ax1.axvline(np.median(self.y_pred), color='green', linestyle='--', linewidth=2,
                   label=f'Median: {np.median(self.y_pred):.3f}')
        ax1.set_xlabel('Predicted Default Probability', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Overall Risk Score Distribution', fontsize=12)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Distribution by actual outcome
        ax2 = axes[1]
        ax2.hist(self.y_pred[self.y == 0], bins=50, alpha=0.6, color='green', 
                label=f'Non-Default (n={sum(self.y==0):,})', density=True)
        ax2.hist(self.y_pred[self.y == 1], bins=50, alpha=0.6, color='red',
                label=f'Default (n={sum(self.y==1):,})', density=True)
        ax2.set_xlabel('Predicted Default Probability', fontsize=11)
        ax2.set_ylabel('Density', fontsize=11)
        ax2.set_title('Risk Score by Actual Outcome', fontsize=12)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Risk Score Distribution saved to: {save_path}")
    
    def plot_feature_importance(self, top_n=15, save_path=None):
        """Plot feature importance bar chart"""
        if save_path is None:
            save_path = f'{self.output_dir}/feature_importance.png'
        
        # Get feature importance
        importance = self.model.feature_importance(importance_type='gain')
        feat_imp = pd.DataFrame({
            'feature': self.features,
            'importance': importance
        }).sort_values('importance', ascending=True).tail(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(feat_imp)))
        bars = ax.barh(feat_imp['feature'], feat_imp['importance'], color=colors)
        
        ax.set_xlabel('Importance (Gain)', fontsize=11)
        ax.set_title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for bar, val in zip(bars, feat_imp['importance']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{val:.0f}', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Feature Importance Chart saved to: {save_path}")
    
    def plot_fairness_analysis(self, save_path=None):
        """Plot fairness analysis by gender"""
        if save_path is None:
            save_path = f'{self.output_dir}/fairness_analysis.png'
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Fairness Analysis: Risk Score by Gender', fontsize=14, fontweight='bold')
        
        # Check for gender column
        if 'gender' in self.df.columns:
            gender_col = 'gender'
        elif 'gender_normalized' in self.df.columns:
            gender_col = 'gender_normalized'
        else:
            print("Warning: No gender column found")
            return
        
        self.df['risk_score'] = self.y_pred
        
        # 1. Average risk score by gender
        ax1 = axes[0]
        gender_risk = self.df.groupby(gender_col)['risk_score'].mean().sort_values()
        colors = ['steelblue', 'coral']
        bars = ax1.bar(gender_risk.index, gender_risk.values, color=colors[:len(gender_risk)])
        ax1.set_ylabel('Average Risk Score', fontsize=11)
        ax1.set_title('Average Risk Score by Gender', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f'{bar.get_height():.3f}', ha='center', fontsize=10)
        
        # 2. Risk score distribution by gender
        ax2 = axes[1]
        for i, (gender, group) in enumerate(self.df.groupby(gender_col)):
            ax2.hist(group['risk_score'], bins=30, alpha=0.5, label=gender,
                    color=colors[i % len(colors)], density=True)
        ax2.set_xlabel('Risk Score', fontsize=11)
        ax2.set_ylabel('Density', fontsize=11)
        ax2.set_title('Risk Score Distribution by Gender', fontsize=12)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Actual vs Predicted default rate by gender
        ax3 = axes[2]
        x = np.arange(len(self.df[gender_col].unique()))
        width = 0.35
        
        actual_rates = self.df.groupby(gender_col)['default'].mean()
        predicted_rates = self.df.groupby(gender_col)['risk_score'].mean()
        
        bars1 = ax3.bar(x - width/2, actual_rates.values, width, label='Actual Default Rate', color='coral')
        bars2 = ax3.bar(x + width/2, predicted_rates.values, width, label='Predicted Risk Score', color='steelblue')
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(actual_rates.index)
        ax3.set_ylabel('Rate / Score', fontsize=11)
        ax3.set_title('Actual vs Predicted by Gender', fontsize=12)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Calculate disparate impact
        if len(gender_risk) >= 2:
            di = gender_risk.min() / gender_risk.max()
            textstr = f'Disparate Impact Ratio: {di:.3f}\n(Acceptable: 0.8-1.2)'
            color = 'lightgreen' if 0.8 <= di <= 1.2 else 'lightyellow'
            props = dict(boxstyle='round', facecolor=color, alpha=0.8)
            ax3.text(0.02, 0.98, textstr, transform=ax3.transAxes, fontsize=9,
                    verticalalignment='top', bbox=props)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Fairness Analysis saved to: {save_path}")
    
    def generate_full_dashboard(self):
        """Generate all dashboard visualizations"""
        print("\n" + "=" * 60)
        print("GENERATING CREDIT RISK DASHBOARD")
        print("=" * 60)
        
        metrics = self.plot_model_performance()
        self.plot_risk_score_distribution()
        self.plot_feature_importance()
        self.plot_fairness_analysis()
        
        print("\n" + "=" * 60)
        print("DASHBOARD GENERATION COMPLETE")
        print("=" * 60)
        print(f"\nAll visualizations saved to: {self.output_dir}/")
        print("\nFiles generated:")
        print(f"  • model_performance.png - AUC-ROC & KS curves")
        print(f"  • risk_score_distribution.png - Portfolio risk histogram")
        print(f"  • feature_importance.png - Top predictive features")
        print(f"  • fairness_analysis.png - Gender bias analysis")
        
        return metrics


def main():
    dashboard = CreditRiskDashboard(output_dir='dashboard')
    dashboard.load_model_and_data()
    metrics = dashboard.generate_full_dashboard()
    return dashboard, metrics


if __name__ == "__main__":
    dashboard, metrics = main()
