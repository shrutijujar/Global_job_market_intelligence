import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

df = pd.read_csv("data/processed/jobs_clean.csv")

# Salary preparation
df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

df["avg_salary"] = (
    df["salary_min"].fillna(0) +
    df["salary_max"].fillna(0)
) / 2

df = df[df["avg_salary"] > 0]

# Use BOTH country and title
features = pd.get_dummies(
    df[["country", "title"]]
)

target = df["avg_salary"]

X_train, X_test, y_train, y_test = train_test_split(
    features,
    target,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

score = r2_score(y_test, predictions)

joblib.dump(model, "models/salary_model.pkl")
joblib.dump(features.columns, "models/model_columns.pkl")

print("Model Trained Successfully")
print("Training Rows:", len(df))
print("R2 Score:", round(score, 3))