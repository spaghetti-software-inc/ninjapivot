import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.pandas2ri as pandas2ri

pandas2ri.activate()

r_lm = ro.r['lm']
r_summary = ro.r['summary']
r_str = ro.r['str']



# Create your pandas DataFrame
df = pd.DataFrame({
    'x': [1, 2, 3],
    'y': [4, 5, 6],
    'z': ['a', 'b', 'c']  # Non-numeric column
})

# Convert to an R dataframe
rdf = ro.conversion.py2rpy(df)

# Assign the R dataframe to a variable 'df' in R's global environment
ro.globalenv['df'] = rdf

# Run the R command to subset numeric columns and compute the correlation matrix
cor_result = ro.r("cor(df[sapply(df, is.numeric)])")

# Print the correlation matrix
print(cor_result)