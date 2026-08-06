import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Visa Analytics",
    layout="wide"
)

st.title("🛂 Visa Sponsorship Analytics")

df = pd.read_csv(
    "data/processed/jobs_visa.csv"
)

visa_jobs = df[
    df["visa_flag"] == 1
]

# KPI

col1, col2 = st.columns(2)

col1.metric(
    "Visa Sponsored Jobs",
    len(visa_jobs)
)

col2.metric(
    "Countries",
    visa_jobs["country"].nunique()
)

st.divider()

# Jobs by Country

st.subheader("Visa Jobs by Country")

country_counts = (
    visa_jobs["country"]
    .value_counts()
    .reset_index()
)

country_counts.columns = [
    "Country",
    "Jobs"
]

fig = px.bar(
    country_counts,
    x="Country",
    y="Jobs",
    color="Jobs"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# Companies

st.subheader("Companies Offering Visa Support")

company_counts = (
    visa_jobs["company"]
    .value_counts()
    .head(15)
    .reset_index()
)

company_counts.columns = [
    "Company",
    "Jobs"
]

fig = px.bar(
    company_counts,
    x="Jobs",
    y="Company",
    orientation="h",
    color="Jobs"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# Table

st.subheader("Visa Sponsorship Opportunities")

st.dataframe(
    visa_jobs[
        [
            "title",
            "company",
            "country",
            "location"
        ]
    ],
    width="stretch"
)