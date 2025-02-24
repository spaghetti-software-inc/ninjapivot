import rpy2.robjects as ro
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri

# Activate automatic conversion of pandas objects if needed
pandas2ri.activate()
rpy2.robjects.numpy2ri.activate()

# Load required R libraries
base = importr('base')
stats = importr('stats')
MASS = importr('MASS')
kernlab = importr('kernlab')
caret = importr('caret')

# R script as a multiline string
r_script = """
# Load the iris dataset
data(iris)

# Create a reproducible 70/30 train/test split
set.seed(123)
train_idx <- sample(seq_len(nrow(iris)), size = 0.7 * nrow(iris))
train <- iris[train_idx, ]
test  <- iris[-train_idx, ]

# Candidate Model 1: Baseline Model (Majority Class Prediction)
majority_class <- names(sort(table(train$Species), decreasing = TRUE))[1]
baseline_preds <- rep(majority_class, nrow(test))
baseline_accuracy <- mean(baseline_preds == test$Species)
cat("Baseline Accuracy:", baseline_accuracy, "\n")

# Candidate Model 2: Linear Discriminant Analysis (LDA)
lda_model <- lda(Species ~ ., data = train)
lda_preds <- predict(lda_model, newdata = test)$class
lda_accuracy <- mean(lda_preds == test$Species)
cat("LDA Accuracy:", lda_accuracy, "\n")

# Candidate Model 3: Gaussian Process Classifier using kernlab's gausspr() with RBF kernel
gp_model <- gausspr(Species ~ ., data = train, kernel = "rbfdot")
gp_preds <- predict(gp_model, newdata = test)
gp_accuracy <- mean(gp_preds == test$Species)
cat("Gaussian Process Accuracy:", gp_accuracy, "\n")

# Combine the results into a data frame and print it
results <- data.frame(
  Model = c("Baseline", "LDA", "Gaussian Process"),
  Accuracy = c(baseline_accuracy, lda_accuracy, gp_accuracy)
)
print(results)
"""

# Execute the R script using rpy2
ro.r(r_script)
