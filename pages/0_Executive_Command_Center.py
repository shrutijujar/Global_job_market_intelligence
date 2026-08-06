import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess

st.set_page_config(
    page_title="Executive Command Center",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

from database.queries import load_jobs

@st.cache_data(ttl=21600)
def load_data():

    jobs = load_jobs()

    skills = pd.read_csv(
        "data/processed/job_skills.csv"
    )

    return jobs, skills

df, skills_df = load_data()

# =========================
# DATA PREP
# =========================

df["salary_min"] = pd.to_numeric(
    df["salary_min"],
    errors="coerce"
)

df["salary_max"] = pd.to_numeric(
    df["salary_max"],
    errors="coerce"
)

df["avg_salary"] = (
    df["salary_min"].fillna(0)
    + df["salary_max"].fillna(0)
) / 2

salary_df = df[
    (df["salary_min"] > 0)
    & (df["salary_max"] > 0)
].copy()

salary_df["avg_salary"] = (
    salary_df["salary_min"]
    + salary_df["salary_max"]
) / 2

# =========================
# SIDEBAR
# =========================

st.sidebar.header("🌍 Dashboard Filters")

# Fast Refresh
if st.sidebar.button("🔄 Refresh Dashboard"):

    st.cache_data.clear()

    st.success(
        "Dashboard Refreshed Successfully!"
    )

    st.rerun()

# Fetch Latest Jobs
if st.sidebar.button("🌍 Fetch Latest Jobs"):

    with st.spinner(
        "Fetching latest jobs from Adzuna..."
    ):

        import subprocess

        subprocess.run(
            ["python", "src/pipeline.py"]
        )

    st.cache_data.clear()

    st.success(
        "Latest jobs fetched successfully!"
    )

    st.rerun()
selected_skill = st.sidebar.selectbox(
    "Top Skill",
    ["All"] + sorted(
        skills_df["skill"]
        .dropna()
        .unique()
        .tolist()
    )
)
countries = sorted(
    df["country"]
    .dropna()
    .unique()
)

selected_countries = st.sidebar.multiselect(
    "Country",
    countries
)

if selected_countries:
    df = df[
        df["country"]
        .isin(selected_countries)
    ]

job_titles = sorted(
    df["title"]
    .dropna()
    .unique()
)

selected_roles = st.sidebar.multiselect(
    "Job Role",
    job_titles[:500]
)

if selected_roles:
    df = df[
        df["title"]
        .isin(selected_roles)
    ]

# =========================
# TITLE
# =========================

st.title(
    "🌍 Executive Command Center"
)

st.markdown(
    """
    ### Real-Time European Data & AI Job Market Intelligence Platform
    """
)
tab1, tab2, tab3 = st.tabs([
    "📊 Market Overview",
    "💰 Salary Intelligence",
    "🚀 Skills Intelligence"
])
st.caption(
    "Live European Job Market Analytics Dashboard"
)

# =========================
# KPI ROW
# =========================
latest_job_date = df["created"].max()

if pd.notna(latest_job_date):
    latest_job_date = str(latest_job_date)[:16]
else:
    latest_job_date = "N/A"

median_salary = 0

if len(salary_df) > 0:
    median_salary = int(
        salary_df["avg_salary"]
        .median()
    )

visa_jobs = len(
    df[
        df["description"]
        .str.contains(
            "visa|sponsorship|work permit",
            case=False,
            na=False
        )
    ]
)

c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

c1.metric(
    "Jobs",
    f"{len(df):,}"
)

c2.metric(
    "Countries",
    df["country"].nunique()
)

c3.metric(
    "Companies",
    df["company"].nunique()
)

c4.metric(
    "Median Salary",
    f"€{median_salary:,.0f}"
)

c5.metric(
    "Visa Jobs",
    visa_jobs
)

c6.metric(
    "Last Updated",
    latest_job_date
)
st.divider()

# =========================
# MAP + SALARY
# =========================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🌍 Jobs by Country")

    country_jobs = (
        df.groupby("country")
        .size()
        .reset_index(name="jobs")
        .sort_values(
            "jobs",
            ascending=False
        )
    )

    fig_country = px.funnel(
        country_jobs,
        x="jobs",
        y="country"
    )

    st.plotly_chart(
        fig_country,
        width="stretch"
    )
with col2:

    st.subheader("💰 Salary by Country")

    salary_country = (
        salary_df
        .groupby("country")["avg_salary"]
        .median()
        .reset_index()
        .sort_values(
            "avg_salary",
            ascending=False
        )
    )

    fig_salary = px.bar(
        salary_country,
        x="country",
        y="avg_salary",
        color="avg_salary"
    )

    st.plotly_chart(
        fig_salary,
        width="stretch"
    )

# =========================
# SKILLS + COMPANIES
# =========================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🚀 Top Skills Demand")

    top_skills = (
        skills_df["skill"]
        .value_counts()
        .head(15)
        .reset_index()
    )

    top_skills.columns = [
        "skill",
        "count"
    ]

    fig_skills = px.treemap(
        top_skills,
        path=["skill"],
        values="count"
    )

    st.plotly_chart(
        fig_skills,
        width="stretch"
    )

with col2:

    st.subheader("🏢 Top Hiring Companies")

    companies = (
        df["company"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    companies.columns = [
        "company",
        "jobs"
    ]

    fig_company = px.scatter(
        companies,
        x="jobs",
        y="company",
        size="jobs",
        hover_name="company"
    )

    st.plotly_chart(
        fig_company,
        width="stretch"
    )

# =========================
# VISA + SALARY DIST
# =========================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🛂 Visa Sponsorship")

    non_visa_jobs = (
        len(df) - visa_jobs
    )

    visa_df = pd.DataFrame({
        "Type": [
            "Visa Sponsored",
            "Other Jobs"
        ],
        "Count": [
            visa_jobs,
            non_visa_jobs
        ]
    })

    fig_visa = px.pie(
        visa_df,
        names="Type",
        values="Count",
        hole=0.6
    )

    st.plotly_chart(
        fig_visa,
        width="stretch"
    )

with col2:

    st.subheader("📊 Salary Distribution")

    fig_box = px.box(
        salary_df,
        y="avg_salary"
    )

    st.plotly_chart(
        fig_box,
        width="stretch"
    )
# =========================
# HIRING TRENDS
# =========================

st.divider()

st.subheader("📈 Hiring Trends")

country_trend = (
    df.groupby("country")
    .size()
    .reset_index(name="jobs")
    .sort_values(
        "jobs",
        ascending=False
    )
)

fig_trend = px.area(
    country_trend,
    x="country",
    y="jobs",
    title="Hiring Demand by Country"
)

st.plotly_chart(
    fig_trend,
    width="stretch"
)
# =========================
# AI INSIGHTS
# =========================

st.divider()

st.subheader("🤖 AI Market Insights")

top_country = (
    df["country"]
    .value_counts()
    .idxmax()
)

top_company = (
    df["company"]
    .value_counts()
    .idxmax()
)

top_skill = (
    skills_df["skill"]
    .value_counts()
    .idxmax()
)

highest_salary_country = (
    salary_df
    .groupby("country")["avg_salary"]
    .median()
    .idxmax()
)

a1, a2, a3, a4 = st.columns(4)

a1.info(
    f"🌍 Highest Demand\n\n{top_country}"
)

a2.success(
    f"🚀 Top Skill\n\n{top_skill}"
)

a3.warning(
    f"🏢 Top Company\n\n{top_company}"
)

a4.error(
    f"💰 Highest Salary\n\n{highest_salary_country}"
)

# =========================
# JOB SEARCH
# =========================

st.divider()

st.subheader("🔍 Search Jobs")

search_job = st.text_input(
    "Search Job Title"
)

if search_job:

    search_results = df[
        df["title"]
        .str.contains(
            search_job,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        search_results[
            [
                "title",
                "company",
                "country",
                "salary_min",
                "salary_max"
            ]
        ].head(50),
        use_container_width=True
    )
st.subheader("🔥 Latest Jobs")

latest_jobs = (
    df.sort_values(
        "created",
        ascending=False
    )
    [
        [
            "created",
            "title",
            "company",
            "country",
            "salary_min",
            "salary_max"
        ]
    ]
    .head(25)
)

st.dataframe(
    latest_jobs,
    width="stretch"
)