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

CACHE_DIR =  Path("./cache")

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the pairwise Pearson correlation matrix for a DataFrame.
    """
    # Copy df so that original data remains intact
    df_corr = df.copy()

    # Convert non-numeric (categorical) columns to numeric codes
    for col in df_corr.columns:
        if not pd.api.types.is_numeric_dtype(df_corr[col]):
            df_corr[col] = df_corr[col].astype('category').cat.codes

    # Prepare an empty correlation matrix DataFrame
    cols = df_corr.columns
    corr_matrix = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)

    # Compute pairwise Pearson correlation coefficients using scipy.stats.pearsonr
    for i, col1 in enumerate(cols):
        for j, col2 in enumerate(cols):
            if i <= j:
                r, _ = pearsonr(df_corr[col1], df_corr[col2])
                corr_matrix.loc[col1, col2] = r
                corr_matrix.loc[col2, col1] = r
                
    return corr_matrix

def get_regression_results(df: pd.DataFrame) -> str:
    """
    For each column in the DataFrame, treat it as the target (y) and use all other columns as predictors.
    Compute the regression model using least squares, and record performance metrics (R² and RMSE).
    Returns a LaTeX-formatted table of the results.
    """
    # Convert non-numeric columns to numeric codes
    df_numeric = df.copy()
    for col in df_numeric.columns:
        if not pd.api.types.is_numeric_dtype(df_numeric[col]):
            df_numeric[col] = df_numeric[col].astype('category').cat.codes

    results = []
    for target in df_numeric.columns:
        y = df_numeric[target].values
        # Use remaining columns as predictors
        X = df_numeric.drop(columns=target).values
        # Add an intercept term
        X = np.column_stack([np.ones(X.shape[0]), X])
        
        # Solve the least squares problem (using numpy's lstsq)
        beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        y_pred = X @ beta
        
        # Compute performance metrics
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        
        results.append([target, r_squared, rmse])
    
    # Create a DataFrame and convert it to LaTeX using tabulate
    results_df = pd.DataFrame(results, columns=["Target", "R-squared", "RMSE"])
    regression_table_latex = tabulate(results_df, headers='keys', tablefmt='latex', showindex=False)
    return regression_table_latex

def run_analysis(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    Runs a simple analysis on the given DataFrame:
    - Computes the correlation matrix
    - Generates a scatter plot matrix
    - Performs linear regression for each column as target and evaluates performance
    """
    # Compute the correlation matrix
    corr_matrix = get_correlation_matrix(df)
    corr_matrix_latex = tabulate(corr_matrix, headers='keys', tablefmt='latex')
    
    # Generate a scatter plot matrix
    scatter_plot_matrix = pd.plotting.scatter_matrix(df, alpha=0.5, figsize=(10, 10), diagonal='kde')
    scatter_plot_matrix_path = output_dir / "scatter_plot_matrix.png"
    plt.savefig(scatter_plot_matrix_path)
    plt.close()
    
    # Get regression analysis results as a LaTeX table
    regression_results_latex = get_regression_results(df)
    
    return {
        "correlation_matrix": corr_matrix_latex,
        "scatter_plot_matrix": "scatter_plot_matrix.png",
        "regression_results": regression_results_latex
    }

def gen_latex_document(job_id: str, df: pd.DataFrame) -> Path:
    """
    Generates a LaTeX document that includes:
    - A preview of the data
    - The correlation matrix
    - The scatter plot matrix
    - The regression analysis results
    """
    output_dir = CACHE_DIR / job_id  
    output_dir.mkdir(parents=True, exist_ok=True)

    df_head_latex = tabulate(df.head(), headers='keys', tablefmt='latex')
    
    # Run the analysis
    analysis_results = run_analysis(df, output_dir)
    
    ########################################################################################
    # Generate the LaTeX file
    tex = f"""\\documentclass[12pt,letterpaper]{{article}}\n"""
    tex += '\\usepackage[includehead,headheight=10mm,margin=1cm]{geometry}\n'
    tex += "\\usepackage{graphicx}\n"
    tex += "\\usepackage{fontspec}\n"
    tex += "\\usepackage{xcolor}\n"
    tex += "\\usepackage{array}\n"
    tex += "\\usepackage{longtable}\n"
    tex += "\\usepackage{fancyhdr}\n"
    
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tex += f"""\\usepackage[pdfproducer={{diamoro.cx}},pdfsubject={{report ID {job_id} {report_timestamp}}}]{{hyperref}}\n"""
    tex += "\\pagestyle{fancy}\n"
    tex += '\\fancyhead{}\n'
    tex += '\\renewcommand{\\headrulewidth}{0pt}\n'
    tex += '\\fancyhead[RO,LE]{www.ninjapivot.com}\n'
    tex += '\\pagenumbering{gobble}\n'
    tex += '\\graphicspath{{%s}}\n' % output_dir
    tex += "\\begin{document}\n"
    
    tex += "\\section{Data Preview}\n"
    tex += "\\begin{center}\n"
    tex += df_head_latex + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Correlation Matrix}\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["correlation_matrix"] + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Scatter Plot Matrix}\n"
    tex += "\\begin{center}\n"
    tex += '\\includegraphics[width=8in]{{%s}}\n' % analysis_results["scatter_plot_matrix"]
    tex += "\\end{center}\n"
    
    
    tex += "\\section{Regression Analysis}\n"
    tex += "For each target variable, a linear regression model was fit using the remaining columns as predictors. Performance metrics (R\\textsuperscript{2} and RMSE) are shown below:\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["regression_results"] + "\n"
    tex += "\\end{center}\n"
    
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
