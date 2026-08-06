import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# ==========================
# LOAD DATA
# ==========================

df = pd.read_csv("data/processed/jobs_clean.csv")

# ==========================
# CREATE TARGET SALARY
# ==========================

df["salary"] = (
    df["salary_min"] +
    df["salary_max"]
) / 2

# ==========================
# REMOVE MISSING VALUES
# ==========================

df = df.dropna(
    subset=[
        "country",
        "job_category",
        "experience",
        "salary"
    ]
)

# ==========================
# FEATURES
# ==========================

X = df[
    [
        "country",
        "job_category",
        "experience"
    ]
]

y = df["salary"]

# ==========================
# ONE HOT ENCODING
# ==========================

X = pd.get_dummies(X)

# Save feature names
joblib.dump(
    X.columns.tolist(),
    "models/model_columns.pkl"
)

# ==========================
# TRAIN TEST SPLIT
# ==========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ==========================
# MODEL
# ==========================

model = RandomForestRegressor(
    n_estimators=50,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

# ==========================
# EVALUATION
# ==========================

pred = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    pred
)

print(f"\nMean Absolute Error : €{mae:,.2f}")

# ==========================
# SAVE MODEL
# ==========================

joblib.dump(
    model,
    "models/salary_model.pkl"
)

print("\n✅ New Salary Model Saved Successfully")