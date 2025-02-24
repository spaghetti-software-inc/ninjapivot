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
            # Calculate only for upper triangle and mirror the value
            if i <= j:
                r, _ = pearsonr(df_corr[col1], df_corr[col2])
                corr_matrix.loc[col1, col2] = r
                corr_matrix.loc[col2, col1] = r
                
    return corr_matrix

def run_analysis(df: pd.DataFrame, output_dir : Path) -> dict:
    """
    Runs a simple analysis on the given DataFrame:
    - Computes the correlation matrix
    - Generates a scatter plot matrix
    """
    # Compute the correlation matrix
    corr_matrix = get_correlation_matrix(df)
    corr_matrix_latex = tabulate(corr_matrix, headers='keys', tablefmt='latex')
    
    # Generate a scatter plot matrix
    scatter_plot_matrix = pd.plotting.scatter_matrix(df, alpha=0.5, figsize=(10, 10), diagonal='kde')
    
    # save the scatter plot matrix to a file
    scatter_plot_matrix_path = output_dir / "scatter_plot_matrix.png"
    plt.savefig(scatter_plot_matrix_path)
    plt.close()
    
    
    return {
        "correlation_matrix": corr_matrix_latex,
        "scatter_plot_matrix": "scatter_plot_matrix.png"
    }

def gen_latex_document(job_id: str, df: pd.DataFrame) -> Path:
    """
    Generates a LaTeX table from a DataFrame.
    """
    output_dir = CACHE_DIR / job_id  
    output_dir.mkdir(parents=True, exist_ok=True)


    df_head_latex = tabulate(df.head(), headers='keys', tablefmt='latex')
    # print(df_head_latex)
    
    # Run the analysis
    analysis_results = run_analysis(df, output_dir)
    
    
    # print(analysis_results)
    
    

    ########################################################################################
    # Generate the LaTeX file
    tex = f"""\\documentclass[12pt,letterpaper]{{article}}\n"""
    tex += '\\usepackage[includehead,headheight=10mm,margin=1cm]{geometry}\n'
    tex += f"""\\usepackage{{hyperref}}\n"""
    tex += f"""\\usepackage{{graphicx}}\n"""
    tex += f"""\\usepackage{{fontspec}}\n"""
    tex += f"""\\usepackage{{xcolor}}\n"""
    tex += f"""\\usepackage{{array}}\n"""
    tex += '\\usepackage{longtable}\n'
    tex += f"""\\usepackage{{fancyhdr}}\n"""

    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tex += f"""\\usepackage[pdfproducer={{diamoro.cx}},pdfsubject={{report ID {job_id} {report_timestamp}}}]{{hyperref}}\n"""

    tex += f"""\\pagestyle{{fancy}}\n"""
    #tex += f"""\\geometry{{margin=1in}}\n"""
    
    tex += '\\fancyhead{}\n'
    tex += '\\renewcommand{\\headrulewidth}{0pt}' + "\n"

    tex += '\\fancyhead[RO,LE]{\\url{www.ninjapivot.com}}' + "\n"

    tex += '\\pagenumbering{gobble}\n'

    tex += '\\graphicspath{{%s}}' % output_dir + "\n"
    
    tex += "\\begin{document}\n"
    
    tex += "\\section{Data}\n"
    tex += "\\begin{center}\n"
    tex += df_head_latex + "\n"
    tex += "\\end{center}\n"
    
    tex += "\\section{Correlation}\n"
    tex += "\\begin{center}\n"
    tex += analysis_results["correlation_matrix"] + "\n"
    tex += "\\end{center}\n"
    
    tex += '\\centering{\\includegraphics[width=8in]{{%s}}}' % analysis_results["scatter_plot_matrix"] + "\n"    
    
    tex += "\\end{document}\n"
    
    
    
    tex_path = output_dir / "main.tex"
    pdf_path = output_dir / "main.pdf"
    
    with open(tex_path, "w") as f:
        f.write(tex)

    # get the current working directory
    logger.info(f"Generating PDF report: {pdf_path}")
    cwd = Path.cwd()
    os.chdir(output_dir)
    os.system("latexmk -lualatex -output-directory=./ ./main.tex")
    os.chdir(cwd)

    return pdf_path