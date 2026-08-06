import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Salary Intelligence",
    layout="wide"
)

st.title("💰 Salary Intelligence Dashboard")

# Load data
df = pd.read_csv("data/processed/jobs_clean.csv")

# Clean salary columns
df["salary_min"] = pd.to_numeric(
    df["salary_min"],
    errors="coerce"
)

df["salary_max"] = pd.to_numeric(
    df["salary_max"],
    errors="coerce"
)

df["avg_salary"] = (
    df["salary_min"].fillna(0) +
    df["salary_max"].fillna(0)
) / 2

salary_df = df[df["avg_salary"] > 0]

# ==========================
# SIDEBAR FILTERS
# ==========================

st.sidebar.header("Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    sorted(salary_df["country"].unique()),
    default=sorted(salary_df["country"].unique())
)

salary_range = st.sidebar.slider(
    "Salary Range (€)",
    int(salary_df["avg_salary"].min()),
    int(salary_df["avg_salary"].max()),
    (
        int(salary_df["avg_salary"].min()),
        int(salary_df["avg_salary"].max())
    )
)

# Apply filters

salary_df = salary_df[
    salary_df["country"].isin(selected_countries)
]

salary_df = salary_df[
    (salary_df["avg_salary"] >= salary_range[0])
    &
    (salary_df["avg_salary"] <= salary_range[1])
]

# ==========================
# KPI CARDS
# ==========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Jobs With Salary",
    len(salary_df)
)

col2.metric(
    "Average Salary",
    f"€{salary_df['avg_salary'].mean():,.0f}"
)

col3.metric(
    "Highest Salary",
    f"€{salary_df['avg_salary'].max():,.0f}"
)

col4.metric(
    "Countries",
    salary_df["country"].nunique()
)

st.divider()

# ==========================
# SALARY DISTRIBUTION
# ==========================

st.subheader("📊 Salary Distribution")

fig = px.histogram(
    salary_df,
    x="avg_salary",
    nbins=40,
    title="Salary Distribution"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================
# BOXPLOT
# ==========================

st.subheader("📦 Salary Spread by Country")

fig = px.box(
    salary_df,
    x="country",
    y="avg_salary",
    color="country"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================
# TOP PAYING COUNTRIES
# ==========================

st.subheader("🏆 Top Paying Countries")

country_salary = (
    salary_df
    .groupby("country")["avg_salary"]
    .mean()
    .reset_index()
    .sort_values(
        by="avg_salary",
        ascending=False
    )
)

fig = px.bar(
    country_salary,
    x="country",
    y="avg_salary",
    color="avg_salary",
    title="Average Salary by Country"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================
# DATA TABLE
# ==========================

st.subheader("📋 Salary Data")

st.dataframe(
    salary_df[
        [
            "title",
            "company",
            "country",
            "avg_salary"
        ]
    ],
    width="stretch"
)