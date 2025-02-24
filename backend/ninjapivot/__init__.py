import os
import sys
import asyncio
import random
import json
import uuid
from pathlib import Path
from io import BytesIO

from datetime import datetime

import pandas as pd
import numpy as np
from scipy.stats import pearsonr

from matplotlib import pyplot as plt

from tabulate import tabulate

from rich.traceback import install
install()
from rich import print

from loguru import logger

# For clustering analysis, we use scikit-learn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

CACHE_DIR = Path("./cache")

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the pairwise Pearson correlation matrix for a DataFrame.
    """
    df_corr = df.copy()
    # Convert non-numeric (categorical) columns to numeric codes
    for col in df_corr.columns:
        if not pd.api.types.is_numeric_dtype(df_corr[col]):
            df_corr[col] = df_corr[col].astype('category').cat.codes

    cols = df_corr.columns
    corr_matrix = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)

    for i, col1 in enumerate(cols):
        for j, col2 in enumerate(cols):
            if i <= j:
                r, _ = pearsonr(df_corr[col1], df_corr[col2])
                corr_matrix.loc[col1, col2] = r
                corr_matrix.loc[col2, col1] = r
                
    return corr_matrix

def get_regression_results(df: pd.DataFrame, output_dir: Path, B: int = 100) -> (str, list):
    """
    For each column in the DataFrame, treat it as the target (y) and use the remaining columns as predictors.
    Fits a linear regression model using least squares, computes R² and RMSE, and creates a scatter plot
    of observed vs. predicted values. Additionally, bootstrap resampling (B iterations) is used to draw
    multiple regression lines on the same plot.
    
    Returns:
      - A LaTeX-formatted table with regression metrics.
      - A list of tuples (target, filename) for each regression plot.
    """
    # Convert non-numeric columns to numeric codes
    df_numeric = df.copy()
    for col in df_numeric.columns:
        if not pd.api.types.is_numeric_dtype(df_numeric[col]):
            df_numeric[col] = df_numeric[col].astype('category').cat.codes

    metrics = []
    regression_plots = []
    
    for target in df_numeric.columns:
        y = df_numeric[target].values
        # Use remaining columns as predictors
        X = df_numeric.drop(columns=target).values
        # Add an intercept term
        X = np.column_stack([np.ones(X.shape[0]), X])
        
        # Full sample regression
        beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        y_pred = X @ beta
        
        # Compute performance metrics
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        
        metrics.append([target, r_squared, rmse])
        
        # Create regression plot: observed vs. predicted
        plt.figure(figsize=(6, 6))
        plt.scatter(y, y_pred, alpha=0.7, edgecolor='k', label='Observed Predictions')
        # Plot the ideal reference line
        plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Ideal')
        
        # Bootstrap resampling: overlay multiple regression lines
        for _ in range(B):
            indices = np.random.choice(len(y), size=len(y), replace=True)
            X_boot = X[indices, :]
            y_boot = y[indices]
            beta_boot, _, _, _ = np.linalg.lstsq(X_boot, y_boot, rcond=None)
            y_pred_boot = X @ beta_boot
            slope, intercept = np.polyfit(y, y_pred_boot, 1)
            x_line = np.array([y.min(), y.max()])
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, color='gray', alpha=0.1, linewidth=1)
        
        plt.xlabel('Observed')
        plt.ylabel('Predicted')
        plt.title(f'Regression for {target}')
        plt.legend()
        
        plot_filename = f"regression_{target}.png"
        plot_path = output_dir / plot_filename
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
        regression_plots.append((target, plot_filename))
    
    # Create a DataFrame for metrics and convert to a LaTeX table
    metrics_df = pd.DataFrame(metrics, columns=["Target", "R-squared", "RMSE"])
    regression_table_latex = tabulate(metrics_df, headers='keys', tablefmt='latex', showindex=False)
    
    return regression_table_latex, regression_plots

def get_clustering_analysis(df: pd.DataFrame, output_dir: Path, n_clusters: int = 3) -> (str, str):
    """
    Performs clustering analysis on the DataFrame. Non-numeric columns are converted to numeric codes.
    A KMeans algorithm (with n_clusters) is applied, and the results are summarized by:
      - A LaTeX table showing the number of samples in each cluster and the cluster centers.
      - A scatter plot of the data in two dimensions (obtained via PCA) with points colored by cluster.
      
    Returns:
      - A LaTeX-formatted table with clustering results.
      - The filename of the clustering plot.
    """
    # Convert non-numeric columns to numeric codes
    df_numeric = df.copy()
    for col in df_numeric.columns:
        if not pd.api.types.is_numeric_dtype(df_numeric[col]):
            df_numeric[col] = df_numeric[col].astype('category').cat.codes

    # Fit KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(df_numeric)
    df_numeric['Cluster'] = clusters

    # Summarize clusters: counts per cluster and cluster centers
    cluster_counts = df_numeric['Cluster'].value_counts().sort_index()
    centers = kmeans.cluster_centers_
    centers_df = pd.DataFrame(centers, columns=df_numeric.columns[:-1])
    centers_df.insert(0, "Cluster", range(n_clusters))
    
    # Create a summary table combining cluster counts and centers
    summary_table = pd.DataFrame({
        "Cluster": range(n_clusters),
        "Count": [cluster_counts[i] for i in range(n_clusters)]
    }).merge(centers_df, on="Cluster")
    
    clustering_table_latex = tabulate(summary_table, headers='keys', tablefmt='latex', showindex=False)
    
    # Use PCA to reduce data to 2 dimensions for visualization
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(df_numeric.drop(columns="Cluster"))
    
    plt.figure(figsize=(6, 6))
    scatter = plt.scatter(pca_result[:, 0], pca_result[:, 1], c=clusters, cmap='viridis', alpha=0.7, edgecolor='k')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title('Clustering Analysis (PCA Projection)')
    plt.colorbar(scatter, label='Cluster')
    
    clustering_plot_filename = "clustering.png"
    clustering_plot_path = output_dir / clustering_plot_filename
    plt.savefig(clustering_plot_path, bbox_inches='tight')
    plt.close()
    
    return clustering_table_latex, clustering_plot_filename

def run_analysis(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    Runs a complete analysis on the given DataFrame:
      - Computes the correlation matrix.
      - Generates a scatter plot matrix.
      - Performs linear regression for each column as target and evaluates performance,
        generating corresponding regression plots with bootstrap lines.
      - Performs clustering analysis and generates a summary table and PCA plot.
    """
    # Correlation matrix
    corr_matrix = get_correlation_matrix(df)
    corr_matrix_latex = tabulate(corr_matrix, headers='keys', tablefmt='latex')
    
    # Scatter plot matrix
    scatter_plot_matrix = pd.plotting.scatter_matrix(df, alpha=0.5, figsize=(10, 10), diagonal='kde')
    scatter_plot_matrix_path = output_dir / "scatter_plot_matrix.png"
    plt.savefig(scatter_plot_matrix_path, bbox_inches='tight')
    plt.close()
    
    # Regression analysis with bootstrap plots
    regression_results_latex, regression_plots = get_regression_results(df, output_dir)
    
    # Clustering analysis
    clustering_table_latex, clustering_plot_filename = get_clustering_analysis(df, output_dir)
    
    return {
        "correlation_matrix": corr_matrix_latex,
        "scatter_plot_matrix": "scatter_plot_matrix.png",
        "regression_results": regression_results_latex,
        "regression_plots": regression_plots,
        "clustering_table": clustering_table_latex,
        "clustering_plot": clustering_plot_filename
    }

def gen_latex_document(job_id: str, df: pd.DataFrame) -> Path:
    """
    Generates a LaTeX document that includes:
      - A preview of the data.
      - The correlation matrix.
      - The scatter plot matrix.
      - The regression analysis results with bootstrap plots.
      - The clustering analysis results (summary table and PCA plot).
    """
    output_dir = CACHE_DIR / job_id  
    output_dir.mkdir(parents=True, exist_ok=True)

    df_head_latex = tabulate(df.head(), headers='keys', tablefmt='latex')
    
    # Run the analysis
    analysis_results = run_analysis(df, output_dir)
    
    ########################################################################################
    # Generate the LaTeX file
    tex = f"""\\documentclass[12pt,letterpaper]{{article}}
\\usepackage[includehead,headheight=10mm,margin=1cm]{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{fontspec}}
\\usepackage{{xcolor}}
\\usepackage{{array}}
\\usepackage{{longtable}}
\\usepackage{{fancyhdr}}
"""
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tex += f"""\\usepackage[pdfproducer={{diamoro.cx}},pdfsubject={{report ID {job_id} {report_timestamp}}}]{{hyperref}}
\\pagestyle{{fancy}}
\\fancyhead{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\fancyhead[RO,LE]{{www.ninjapivot.com}}
\\pagenumbering{{gobble}}
\\graphicspath{{{{{output_dir}/}}}}
\\begin{{document}}
"""
    
    tex += "\\section{Data Preview}\n"
    tex += "\\begin{center}\n"
    tex += df_head_latex + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Correlation Matrix}\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["correlation_matrix"] + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Scatter Plot Matrix}\n"
    tex += '\\centering{\\includegraphics[width=8in]{{%s}}}\n' % analysis_results["scatter_plot_matrix"]
    
    tex += "\\section{Regression Analysis}\n"
    tex += "For each target variable, a linear regression model was fit using the remaining columns as predictors. "
    tex += "The table below shows performance metrics (R\\textsuperscript{2} and RMSE):\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["regression_results"] + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Regression Plots with Bootstrap Lines}\n"
    for target, plot_file in analysis_results["regression_plots"]:
        tex += f"\\subsection*{{Regression Plot for {target}}}\n"
        tex += '\\centering{\\includegraphics[width=0.8\\textwidth]{%s}}\n' % plot_file
    
    tex += "\\section{Clustering Analysis}\n"
    tex += "The clustering analysis was performed using KMeans (with 3 clusters). The table below summarizes the cluster counts and centers:\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["clustering_table"] + "\n"
    tex += "\\end{center}\n"
    tex += '\\centering{\\includegraphics[width=0.8\\textwidth]{%s}}\n' % analysis_results["clustering_plot"]
    
    tex += "\\end{document}\n"
    
    tex_path = output_dir / "main.tex"
    pdf_path = output_dir / "main.pdf"
    
    with open(tex_path, "w") as f:
        f.write(tex)

    logger.info(f"Generating PDF report: {pdf_path}")
    cwd = Path.cwd()
    os.chdir(output_dir)
    os.system("latexmk -lualatex -output-directory=./ ./main.tex")
    os.chdir(cwd)

    return pdf_path
