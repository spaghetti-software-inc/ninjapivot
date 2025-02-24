from setuptools import setup, find_packages

setup(
    name='ninjapivot',
    version='1.0.0',
    packages=find_packages(where='ninjapivot'),
    package_dir={'ninjapivot': 'ninjapivot'},
    install_requires=[
        'uvicorn',
        'fastapi',
        'beautifulsoup4',         # Replace with desired version or omit for latest
        'tomlkit',
        'duckdb',
        'ntplib',
        'pandas',
        'matplotlib',
        'scipy',
        'pyarrow',
        'fastparquet',
        'openai',
        'pydantic',
        'tabulate',
        'rich',
        'textual',
        'loguru',
        'pyzmq',
        'html5lib',
        'pyquery',
        'plotext',
        'textual-plotext',
        'tiktoken',
        'blp',
        'pandas-market-calendars',
        'keyring',
        'yfinance',
        'QuantLib',
    ],
    
    
    author_email = 'info@softwarespaghetti.com',
    description  = 'automated data analysis and visualization',
    url          ='https://github.com/spaghetti-software-inc/dxdy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
