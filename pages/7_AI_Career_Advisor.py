import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="AI Career Advisor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Career Advisor Pro")

st.write(
    "Get personalized career guidance, salary prediction, skill gap analysis, and hiring insights."
)

# ==========================================
# LOAD DATA
# ==========================================

jobs_df = pd.read_csv(
    "data/processed/jobs_clean.csv"
)

skills_df = pd.read_csv(
    "data/processed/job_skills.csv"
)

# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load(
    "models/salary_model.pkl"
)

model_columns = joblib.load(
    "models/model_columns.pkl"
)

# ==========================================
# INPUTS
# ==========================================

countries = sorted(
    jobs_df["country"].dropna().unique()
)

selected_country = st.selectbox(
    "🌍 Target Country",
    countries
)

target_role = st.selectbox(
    "🎯 Target Role",
    sorted(
        jobs_df["title"]
        .dropna()
        .unique()
    )
)

user_skills = st.multiselect(
    "🛠 Select Your Current Skills",
    [
        "Python",
        "SQL",
        "Power BI",
        "Excel",
        "Tableau",
        "Azure",
        "AWS",
        "Databricks",
        "Snowflake",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "Git",
        "AI",
        "Data Analysis"
    ]
)

# ==========================================
# GENERATE ADVICE
# ==========================================

if st.button("🚀 Generate Career Advice"):

    # ----------------------------
    # SALARY PREDICTION
    # ----------------------------

    input_df = pd.DataFrame(
        0,
        index=[0],
        columns=model_columns
    )

    country_col = f"country_{selected_country}"
    title_col = f"title_{target_role}"

    if country_col in input_df.columns:
        input_df[country_col] = 1

    if title_col in input_df.columns:
        input_df[title_col] = 1

    predicted_salary = model.predict(
        input_df
    )[0]

    # ----------------------------
    # COUNTRY DATA
    # ----------------------------

    country_jobs = jobs_df[
        jobs_df["country"] == selected_country
    ]

    top_companies = (
        country_jobs["company"]
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    top_roles = (
        country_jobs["title"]
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    top_skills = (
        skills_df["skill"]
        .value_counts()
        .head(15)
        .index
        .tolist()
    )

    missing_skills = [
        skill
        for skill in top_skills
        if skill not in user_skills
    ]

    # ----------------------------
    # VISA ANALYSIS
    # ----------------------------

    visa_jobs = jobs_df[
        jobs_df["description"]
        .str.contains(
            "visa|sponsorship|work permit|relocation",
            case=False,
            na=False
        )
    ]

    visa_rate = round(
        (len(visa_jobs) / len(jobs_df)) * 100,
        2
    )

    # ----------------------------
    # ROADMAP
    # ----------------------------

    roadmap = {
        "Python": "Learn Pandas, NumPy, Matplotlib and build analytics projects.",
        "SQL": "Master joins, CTEs, window functions and query optimization.",
        "Power BI": "Create executive dashboards and DAX measures.",
        "Excel": "Learn Pivot Tables, Power Query and advanced formulas.",
        "Tableau": "Build interactive dashboards and storytelling reports.",
        "Azure": "Learn Azure Data Factory, Synapse and cloud analytics.",
        "AWS": "Learn S3, Glue, Athena and Redshift.",
        "Databricks": "Learn Spark, Delta Lake and ETL pipelines.",
        "Snowflake": "Learn cloud warehousing and data modeling.",
        "Machine Learning": "Learn Scikit-Learn and predictive modeling.",
        "Pandas": "Master data cleaning and feature engineering.",
        "NumPy": "Learn numerical computing and arrays.",
        "Git": "Learn version control and collaboration workflows.",
        "AI": "Learn Generative AI, Prompt Engineering and LLMs.",
        "Data Analysis": "Learn statistics, EDA and business analytics."
    }

    # ==========================================
    # OUTPUT
    # ==========================================

    st.success("Career Analysis Complete")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Expected Salary",
        f"€{predicted_salary:,.0f}"
    )

    col2.metric(
        "🛂 Visa Sponsorship Chance",
        f"{visa_rate}%"
    )

    col3.metric(
        "📚 Missing Skills",
        len(missing_skills)
    )

    st.divider()

    left, right = st.columns(2)

    # ==========================================
    # LEFT SIDE
    # ==========================================

    with left:

        st.subheader("🎯 Recommended Roles")

        for role in top_roles:
            st.write("✅", role)

        st.subheader("🏢 Top Hiring Companies")

        for company in top_companies:
            st.write("🏢", company)

    # ==========================================
    # RIGHT SIDE
    # ==========================================

    with right:

        st.subheader("📚 Skill Gap Analysis")

        if len(missing_skills) == 0:

            st.success(
                "Excellent! Your selected skills already cover most in-demand skills."
            )

        else:

            for skill in missing_skills[:5]:
                st.write("📌", skill)

        st.subheader("🧭 Learning Roadmap")

        if len(missing_skills) == 0:

            st.info(
                "Focus on advanced analytics projects, ML, cloud platforms and portfolio building."
            )

        else:

            for skill in missing_skills[:5]:

                recommendation = roadmap.get(
                    skill,
                    "Learn this skill through projects, certifications and hands-on practice."
                )

                st.info(
                    f"{skill}: {recommendation}"
                )