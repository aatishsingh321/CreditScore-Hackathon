"""
Portfolio Risk Overview Dashboard
Implements:
- Histogram of predicted risk scores
- Risk score distribution analysis
- Portfolio segmentation views
- Risk concentration metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')


class PortfolioRiskDashboard:
    """
    Comprehensive portfolio risk visualization and analysis
    
    Creates interactive dashboards for:
    - Risk score distributions
    - Portfolio segmentation
    - Risk concentration analysis
    - Comparative risk views
    """
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize dashboard
        
        Args:
            style: Matplotlib style (default: seaborn-v0_8-darkgrid)
        """
        # Set style
        try:
            plt.style.use(style)
        except:
            plt.style.use('seaborn-v0_8')
        
        # Set color palette
        self.colors = {
            'low_risk': '#2ecc71',      # Green
            'medium_risk': '#f39c12',   # Orange
            'high_risk': '#e74c3c',     # Red
            'primary': '#3498db',       # Blue
            'secondary': '#9b59b6'      # Purple
        }
        
        self.predictions = None
        self.portfolio_data = None
        
    def load_predictions(self, predictions_file: str, 
                        full_data_file: Optional[str] = None) -> pd.DataFrame:
        """
        Load prediction data and optionally join with full dataset
        
        Args:
            predictions_file: Path to predictions CSV
            full_data_file: Optional path to full dataset for segmentation
            
        Returns:
            DataFrame with predictions and attributes
        """
        # Load predictions
        self.predictions = pd.read_csv(predictions_file)
        print(f"✓ Loaded {len(self.predictions)} predictions")
        
        # Join with full data if provided
        if full_data_file:
            full_data = pd.read_csv(full_data_file)
            
            # Merge on applicant_id
            self.portfolio_data = self.predictions.merge(
                full_data, 
                on='applicant_id', 
                how='left'
            )
            print(f"✓ Joined with full dataset: {self.portfolio_data.shape[1]} columns")
        else:
            self.portfolio_data = self.predictions.copy()
        
        # Add risk categories
        self.portfolio_data['risk_category'] = pd.cut(
            self.portfolio_data['predicted_probability'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        return self.portfolio_data
    
    def plot_risk_histogram(self, 
                           bins: int = 50,
                           figsize: Tuple[int, int] = (12, 6),
                           save_path: Optional[str] = None,
                           show: bool = True) -> plt.Figure:
        """
        Create histogram of predicted risk scores
        
        Args:
            bins: Number of histogram bins
            figsize: Figure size (width, height)
            save_path: Path to save plot
            show: Whether to display plot
            
        Returns:
            Matplotlib figure
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        risk_scores = self.portfolio_data['predicted_probability']
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot histogram
        n, bins_edges, patches = ax.hist(
            risk_scores, 
            bins=bins, 
            edgecolor='black',
            alpha=0.7,
            color=self.colors['primary']
        )
        
        # Color bars by risk level
        for i, patch in enumerate(patches):
            bin_center = (bins_edges[i] + bins_edges[i+1]) / 2
            if bin_center < 0.3:
                patch.set_facecolor(self.colors['low_risk'])
            elif bin_center < 0.6:
                patch.set_facecolor(self.colors['medium_risk'])
            else:
                patch.set_facecolor(self.colors['high_risk'])
        
        # Add vertical lines for risk thresholds
        ax.axvline(x=0.3, color='black', linestyle='--', linewidth=2, 
                   label='Low/Medium Threshold', alpha=0.7)
        ax.axvline(x=0.6, color='black', linestyle='--', linewidth=2, 
                   label='Medium/High Threshold', alpha=0.7)
        
        # Add mean and median lines
        mean_score = risk_scores.mean()
        median_score = risk_scores.median()
        ax.axvline(x=mean_score, color='blue', linestyle='-', linewidth=2, 
                   label=f'Mean: {mean_score:.3f}', alpha=0.8)
        ax.axvline(x=median_score, color='purple', linestyle='-', linewidth=2, 
                   label=f'Median: {median_score:.3f}', alpha=0.8)
        
        # Labels and title
        ax.set_xlabel('Predicted Risk Score (Default Probability)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Applicants', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Risk Score Distribution', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(alpha=0.3)
        
        # Add statistics text box
        stats_text = (
            f"Total Applicants: {len(risk_scores):,}\n"
            f"Mean Risk: {mean_score:.3f}\n"
            f"Median Risk: {median_score:.3f}\n"
            f"Std Dev: {risk_scores.std():.3f}\n"
            f"Min: {risk_scores.min():.3f}\n"
            f"Max: {risk_scores.max():.3f}"
        )
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.5), fontsize=9, family='monospace')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Histogram saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_risk_categories(self,
                            figsize: Tuple[int, int] = (10, 6),
                            save_path: Optional[str] = None,
                            show: bool = True) -> plt.Figure:
        """
        Create bar chart of risk categories
        
        Args:
            figsize: Figure size
            save_path: Path to save plot
            show: Whether to display plot
            
        Returns:
            Matplotlib figure
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        # Count by category
        category_counts = self.portfolio_data['risk_category'].value_counts().sort_index()
        category_pcts = (category_counts / len(self.portfolio_data) * 100).round(2)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Bar colors
        colors = [self.colors['low_risk'], self.colors['medium_risk'], self.colors['high_risk']]
        
        # Plot bars
        bars = ax.bar(
            category_counts.index, 
            category_counts.values,
            color=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8
        )
        
        # Add value labels on bars
        for i, (bar, count, pct) in enumerate(zip(bars, category_counts.values, category_pcts.values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count:,}\n({pct}%)',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Labels and title
        ax.set_xlabel('Risk Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Applicants', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Distribution by Risk Category', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Risk categories chart saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_risk_by_segment(self,
                            segment_col: str,
                            top_n: int = 10,
                            figsize: Tuple[int, int] = (12, 6),
                            save_path: Optional[str] = None,
                            show: bool = True) -> plt.Figure:
        """
        Plot risk distribution by segment (e.g., city, loan purpose)
        
        Args:
            segment_col: Column name for segmentation
            top_n: Number of top segments to show
            figsize: Figure size
            save_path: Path to save plot
            show: Whether to display plot
            
        Returns:
            Matplotlib figure
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        if segment_col not in self.portfolio_data.columns:
            raise ValueError(f"Column '{segment_col}' not found in data")
        
        # Calculate average risk by segment
        segment_risk = self.portfolio_data.groupby(segment_col).agg({
            'predicted_probability': ['mean', 'count']
        }).round(4)
        segment_risk.columns = ['avg_risk', 'count']
        
        # Filter to top N by count and sort by risk
        segment_risk = segment_risk.nlargest(top_n, 'count').sort_values('avg_risk', ascending=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Color bars by risk level
        colors_mapped = segment_risk['avg_risk'].apply(
            lambda x: self.colors['low_risk'] if x < 0.3 
            else self.colors['medium_risk'] if x < 0.6 
            else self.colors['high_risk']
        )
        
        # Horizontal bar chart
        bars = ax.barh(
            range(len(segment_risk)),
            segment_risk['avg_risk'],
            color=colors_mapped,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        
        # Set y-ticks
        ax.set_yticks(range(len(segment_risk)))
        ax.set_yticklabels(segment_risk.index, fontsize=10)
        
        # Add value labels
        for i, (idx, row) in enumerate(segment_risk.iterrows()):
            ax.text(row['avg_risk'] + 0.01, i, 
                   f"{row['avg_risk']:.3f} (n={int(row['count'])})",
                   va='center', fontsize=9)
        
        # Labels and title
        ax.set_xlabel('Average Risk Score', fontsize=12, fontweight='bold')
        ax.set_ylabel(segment_col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_title(f'Average Risk Score by {segment_col.replace("_", " ").title()}', 
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.set_xlim(0, max(segment_risk['avg_risk']) * 1.15)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Segment risk chart saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_risk_heatmap(self,
                         row_col: str,
                         col_col: str,
                         figsize: Tuple[int, int] = (12, 8),
                         save_path: Optional[str] = None,
                         show: bool = True) -> plt.Figure:
        """
        Create heatmap of risk scores by two dimensions
        
        Args:
            row_col: Column for rows
            col_col: Column for columns
            figsize: Figure size
            save_path: Path to save plot
            show: Whether to display plot
            
        Returns:
            Matplotlib figure
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        # Create pivot table
        heatmap_data = self.portfolio_data.pivot_table(
            values='predicted_probability',
            index=row_col,
            columns=col_col,
            aggfunc='mean'
        )
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot heatmap
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn_r',
            cbar_kws={'label': 'Average Risk Score'},
            linewidths=0.5,
            ax=ax
        )
        
        # Labels and title
        ax.set_xlabel(col_col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_ylabel(row_col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_title(f'Risk Score Heatmap: {row_col.replace("_", " ").title()} vs {col_col.replace("_", " ").title()}',
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Heatmap saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_comprehensive_dashboard(self,
                                    figsize: Tuple[int, int] = (16, 10),
                                    save_path: Optional[str] = None,
                                    show: bool = True) -> plt.Figure:
        """
        Create comprehensive dashboard with multiple views
        
        Args:
            figsize: Figure size
            save_path: Path to save plot
            show: Whether to display plot
            
        Returns:
            Matplotlib figure
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        risk_scores = self.portfolio_data['predicted_probability']
        
        # Create figure with subplots
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Main Histogram (top left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        n, bins_edges, patches = ax1.hist(
            risk_scores, bins=50, edgecolor='black', alpha=0.7
        )
        for i, patch in enumerate(patches):
            bin_center = (bins_edges[i] + bins_edges[i+1]) / 2
            if bin_center < 0.3:
                patch.set_facecolor(self.colors['low_risk'])
            elif bin_center < 0.6:
                patch.set_facecolor(self.colors['medium_risk'])
            else:
                patch.set_facecolor(self.colors['high_risk'])
        
        ax1.axvline(x=0.3, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
        ax1.axvline(x=0.6, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
        ax1.set_xlabel('Risk Score', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('Portfolio Risk Distribution', fontweight='bold', fontsize=12)
        ax1.grid(alpha=0.3)
        
        # 2. Risk Categories (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        category_counts = self.portfolio_data['risk_category'].value_counts().sort_index()
        colors = [self.colors['low_risk'], self.colors['medium_risk'], self.colors['high_risk']]
        ax2.bar(range(len(category_counts)), category_counts.values, color=colors, 
                edgecolor='black', alpha=0.8)
        ax2.set_xticks(range(len(category_counts)))
        ax2.set_xticklabels(['Low', 'Medium', 'High'], fontsize=9)
        ax2.set_ylabel('Count', fontweight='bold')
        ax2.set_title('Risk Categories', fontweight='bold', fontsize=12)
        ax2.grid(axis='y', alpha=0.3)
        for i, count in enumerate(category_counts.values):
            ax2.text(i, count, f'{count}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Box Plot (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        bp = ax3.boxplot(risk_scores, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor(self.colors['primary'])
        bp['boxes'][0].set_alpha(0.7)
        ax3.set_ylabel('Risk Score', fontweight='bold')
        ax3.set_title('Score Distribution', fontweight='bold', fontsize=12)
        ax3.grid(alpha=0.3)
        
        # 4. Cumulative Distribution (bottom middle)
        ax4 = fig.add_subplot(gs[1, 1])
        sorted_scores = np.sort(risk_scores)
        cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores) * 100
        ax4.plot(sorted_scores, cumulative, color=self.colors['primary'], linewidth=2)
        ax4.axhline(y=50, color='red', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Risk Score', fontweight='bold')
        ax4.set_ylabel('Cumulative %', fontweight='bold')
        ax4.set_title('Cumulative Distribution', fontweight='bold', fontsize=12)
        ax4.grid(alpha=0.3)
        
        # 5. Statistics Table (bottom right)
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('off')
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Portfolio', f'{len(risk_scores):,}'],
            ['Mean Risk', f'{risk_scores.mean():.4f}'],
            ['Median Risk', f'{risk_scores.median():.4f}'],
            ['Std Deviation', f'{risk_scores.std():.4f}'],
            ['Min Score', f'{risk_scores.min():.4f}'],
            ['Max Score', f'{risk_scores.max():.4f}'],
            ['Low Risk %', f'{(self.portfolio_data["risk_category"]=="Low Risk").sum()/len(risk_scores)*100:.1f}%'],
            ['Medium Risk %', f'{(self.portfolio_data["risk_category"]=="Medium Risk").sum()/len(risk_scores)*100:.1f}%'],
            ['High Risk %', f'{(self.portfolio_data["risk_category"]=="High Risk").sum()/len(risk_scores)*100:.1f}%']
        ]
        
        table = ax5.table(cellText=stats_data, cellLoc='left', loc='center',
                         colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header row
        for i in range(2):
            table[(0, i)].set_facecolor('#3498db')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(stats_data)):
            for j in range(2):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#ecf0f1')
        
        ax5.set_title('Portfolio Statistics', fontweight='bold', fontsize=12, pad=20)
        
        # Overall title
        fig.suptitle('Portfolio Risk Overview Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Comprehensive dashboard saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def generate_risk_summary(self) -> Dict:
        """
        Generate portfolio risk summary statistics
        
        Returns:
            Dictionary with summary metrics
        """
        if self.portfolio_data is None:
            raise ValueError("No data loaded. Call load_predictions() first.")
        
        risk_scores = self.portfolio_data['predicted_probability']
        
        summary = {
            'total_portfolio': len(risk_scores),
            'mean_risk': risk_scores.mean(),
            'median_risk': risk_scores.median(),
            'std_risk': risk_scores.std(),
            'min_risk': risk_scores.min(),
            'max_risk': risk_scores.max(),
            'percentile_25': risk_scores.quantile(0.25),
            'percentile_75': risk_scores.quantile(0.75),
            'low_risk_count': (self.portfolio_data['risk_category'] == 'Low Risk').sum(),
            'medium_risk_count': (self.portfolio_data['risk_category'] == 'Medium Risk').sum(),
            'high_risk_count': (self.portfolio_data['risk_category'] == 'High Risk').sum(),
            'low_risk_pct': (self.portfolio_data['risk_category'] == 'Low Risk').sum() / len(risk_scores) * 100,
            'medium_risk_pct': (self.portfolio_data['risk_category'] == 'Medium Risk').sum() / len(risk_scores) * 100,
            'high_risk_pct': (self.portfolio_data['risk_category'] == 'High Risk').sum() / len(risk_scores) * 100
        }
        
        return summary
    
    def print_summary_report(self):
        """Print formatted summary report"""
        summary = self.generate_risk_summary()
        
        print("=" * 80)
        print("PORTFOLIO RISK SUMMARY REPORT")
        print("=" * 80)
        
        print(f"\n📊 PORTFOLIO OVERVIEW:")
        print(f"   Total Applicants:     {summary['total_portfolio']:,}")
        
        print(f"\n📈 RISK SCORE STATISTICS:")
        print(f"   Mean Risk:            {summary['mean_risk']:.4f}")
        print(f"   Median Risk:          {summary['median_risk']:.4f}")
        print(f"   Std Deviation:        {summary['std_risk']:.4f}")
        print(f"   Min Risk:             {summary['min_risk']:.4f}")
        print(f"   Max Risk:             {summary['max_risk']:.4f}")
        print(f"   25th Percentile:      {summary['percentile_25']:.4f}")
        print(f"   75th Percentile:      {summary['percentile_75']:.4f}")
        
        print(f"\n🎯 RISK CATEGORIES:")
        print(f"   Low Risk:             {summary['low_risk_count']:,} ({summary['low_risk_pct']:.1f}%)")
        print(f"   Medium Risk:          {summary['medium_risk_count']:,} ({summary['medium_risk_pct']:.1f}%)")
        print(f"   High Risk:            {summary['high_risk_count']:,} ({summary['high_risk_pct']:.1f}%)")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    print("Portfolio Risk Dashboard Module")
    print("=" * 80)
    print("\nUsage Example:")
    print("""
    from portfolio_risk_dashboard import PortfolioRiskDashboard
    
    # Create dashboard
    dashboard = PortfolioRiskDashboard()
    
    # Load data
    dashboard.load_predictions(
        'models/validation_predictions.csv',
        'data/credit_risk_dataset_features.csv'
    )
    
    # Create visualizations
    dashboard.plot_risk_histogram(save_path='risk_histogram.png')
    dashboard.plot_risk_categories(save_path='risk_categories.png')
    dashboard.plot_comprehensive_dashboard(save_path='dashboard.png')
    
    # Print summary
    dashboard.print_summary_report()
    """)
