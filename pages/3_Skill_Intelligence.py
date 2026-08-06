import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Skill Intelligence",
    layout="wide"
)

st.title("📈 Skill Intelligence Dashboard")

skills_df = pd.read_csv(
    "data/processed/job_skills.csv"
)

skill_counts = (
    skills_df["skill"]
    .value_counts()
    .reset_index()
)

skill_counts.columns = [
    "Skill",
    "Count"
]

# KPI

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Skill Mentions",
    len(skills_df)
)

col2.metric(
    "Unique Skills",
    skills_df["skill"].nunique()
)

col3.metric(
    "Top Skill",
    skill_counts.iloc[0]["Skill"]
)

st.divider()

# TREEMAP

st.subheader("Skill Demand Treemap")

fig = px.treemap(
    skill_counts,
    path=["Skill"],
    values="Count"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# HORIZONTAL BAR CHART

st.subheader("Top 10 Skills")

fig = px.bar(
    skill_counts.head(10),
    x="Count",
    y="Skill",
    orientation="h",
    color="Count",
    text="Count"
)

fig.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    ),
    xaxis_title="Job Mentions",
    yaxis_title="Skill"
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# BAR CHART

st.subheader("Top 20 Skills")

fig = px.bar(
    skill_counts.head(20),
    x="Skill",
    y="Count",
    color="Count"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# TABLE

st.subheader("Skill Ranking")

st.dataframe(
    skill_counts,
    width="stretch"
)