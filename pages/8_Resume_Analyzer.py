import streamlit as st
import pdfplumber

st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer Pro")

st.write(
    "Upload your resume and get ATS score, role match analysis, missing skills, and improvement recommendations."
)

# ==========================================
# TARGET ROLE
# ==========================================

target_role = st.selectbox(
    "🎯 Target Role",
    [
        "Data Analyst",
        "Data Scientist",
        "Data Engineer",
        "Business Intelligence Analyst"
    ]
)

# ==========================================
# UPLOAD PDF
# ==========================================

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

skills = [
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

role_skills = {
    "Data Analyst":
        ["SQL", "Excel", "Power BI", "Python"],

    "Data Scientist":
        ["Python", "Machine Learning", "Pandas"],

    "Data Engineer":
        ["SQL", "Databricks", "Azure"],

    "Business Intelligence Analyst":
        ["Power BI", "SQL", "Excel"]
}

roadmap = {
    "Python":
        "Learn Pandas, NumPy and build analytics projects.",

    "SQL":
        "Master joins, CTEs, window functions and optimization.",

    "Power BI":
        "Create executive dashboards and learn DAX.",

    "Excel":
        "Master Pivot Tables, Power Query and advanced formulas.",

    "Tableau":
        "Build interactive visualizations and dashboards.",

    "Azure":
        "Learn Azure Data Factory and Synapse Analytics.",

    "AWS":
        "Learn S3, Glue and Redshift.",

    "Databricks":
        "Learn Spark and Delta Lake.",

    "Snowflake":
        "Learn cloud data warehousing.",

    "Machine Learning":
        "Learn Scikit-Learn and predictive modeling.",

    "Pandas":
        "Master data cleaning and feature engineering.",

    "NumPy":
        "Learn numerical computing.",

    "Git":
        "Learn version control and collaboration.",

    "AI":
        "Learn Generative AI and Prompt Engineering.",

    "Data Analysis":
        "Study statistics, EDA and business analytics."
}

# ==========================================
# ANALYZE
# ==========================================

if uploaded_file:

    resume_text = ""

    with pdfplumber.open(uploaded_file) as pdf:

        for page in pdf.pages:

            resume_text += (
                page.extract_text() or ""
            )

    resume_text = resume_text.lower()

    found_skills = []

    for skill in skills:

        if skill.lower() in resume_text:

            found_skills.append(skill)

    missing_skills = [
        skill
        for skill in skills
        if skill not in found_skills
    ]

    # ==========================================
    # ATS SCORE
    # ==========================================

    ats_score = int(
        (len(found_skills) / len(skills))
        * 100
    )

    if ats_score >= 80:
        strength = "Excellent"

    elif ats_score >= 60:
        strength = "Good"

    elif ats_score >= 40:
        strength = "Average"

    else:
        strength = "Needs Improvement"

    # ==========================================
    # ROLE MATCH
    # ==========================================

    required_skills = role_skills[target_role]

    matched = len(
        [
            skill
            for skill in required_skills
            if skill in found_skills
        ]
    )

    role_match = int(
        (matched / len(required_skills))
        * 100
    )

    # ==========================================
    # DASHBOARD
    # ==========================================

    st.success(
        "Resume Analysis Complete"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📊 ATS Score",
        f"{ats_score}%"
    )

    col2.metric(
        "💪 Resume Strength",
        strength
    )

    col3.metric(
        "🎯 Role Match",
        f"{role_match}%"
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader(
            "✅ Skills Detected"
        )

        if found_skills:

            for skill in found_skills:

                st.success(skill)

        else:

            st.warning(
                "No tracked skills found."
            )

        st.subheader(
            "📌 Missing Skills"
        )

        for skill in missing_skills:

            st.error(skill)

    with right:

        st.subheader(
            "💡 Resume Improvement Suggestions"
        )

        if len(missing_skills) > 0:

            st.info(
                f"""
                To improve your resume and ATS score,
                consider adding projects, certifications,
                or experience related to:

                {", ".join(missing_skills[:5])}
                """
            )

        else:

            st.success(
                "Excellent! Your resume contains all tracked skills."
            )

        st.subheader(
            "🧭 Learning Roadmap"
        )

        for skill in missing_skills[:5]:

            recommendation = roadmap.get(
                skill,
                "Learn this skill through projects and practical experience."
            )

            st.info(
                f"{skill}: {recommendation}"
            )

    st.divider()

    st.subheader(
        "📈 Career Recommendation"
    )

    if role_match >= 80:

        st.success(
            f"Your resume is strongly aligned with the {target_role} role."
        )

    elif role_match >= 60:

        st.warning(
            f"Your resume is partially aligned with the {target_role} role. Focus on missing skills."
        )

    else:

        st.error(
            f"Your resume needs significant improvement for the {target_role} role."
        )