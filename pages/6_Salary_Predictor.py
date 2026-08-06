import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="Salary Predictor",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI Salary Predictor")

# ==========================
# LOAD MODEL
# ==========================

model = joblib.load("models/salary_model.pkl")
model_columns = joblib.load("models/model_columns.pkl")

# ==========================
# LOAD DATA
# ==========================

df = pd.read_csv("data/processed/jobs_clean.csv")

countries = sorted(df["country"].dropna().unique())
categories = sorted(df["job_category"].dropna().unique())

# ==========================
# USER INPUT
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    selected_country = st.selectbox(
        "Select Country",
        countries
    )

with col2:
    selected_category = st.selectbox(
    "Select Job Category",
    categories
)

with col3:
    experience = st.slider(
        "Years of Experience",
        min_value=0,
        max_value=20,
        value=2
    )

# ==========================
# PREDICT
# ==========================

if st.button("Predict Salary"):

    input_df = pd.DataFrame(
        0,
        index=[0],
        columns=model_columns
    )

    country_col = f"country_{selected_country}"
    category_col = f"job_category_{selected_category}"

    if country_col in input_df.columns:
        input_df[country_col] = 1

    if category_col in input_df.columns:
        input_df[category_col] = 1

    input_df["experience"] = experience

    prediction = model.predict(input_df)[0]

    st.success(
        f"Predicted Salary: €{prediction:,.0f}"
    )

    st.metric(
        "Expected Salary",
        f"€{prediction:,.0f}"
    )