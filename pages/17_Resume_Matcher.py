import streamlit as st
import pandas as pd
import psycopg2
from PyPDF2 import PdfReader

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Resume Matcher",
    layout="wide"
)

st.title("📄 AI Resume Matcher")

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

if uploaded_file:

    st.success(
        "Resume Uploaded Successfully"
    )

    # =========================
    # PDF TEXT EXTRACTION
    # =========================

    reader = PdfReader(uploaded_file)

    resume_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            resume_text += text

    st.subheader("📄 Resume Text")

    st.text_area(
        "Extracted Text",
        resume_text,
        height=250
    )

    # =========================
    # SKILL EXTRACTION
    # =========================

    skills_library = [
        "python",
        "sql",
        "power bi",
        "tableau",
        "excel",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "statistics",
        "data analysis",
        "data visualization",
        "etl",
        "aws",
        "azure",
        "spark",
        "hadoop",
        "postgresql",
        "mysql",
        "streamlit",
        "scikit-learn",
        "nlp",
        "cnn",
        "data science"
    ]

    resume_lower = resume_text.lower()

    detected_skills = []

    for skill in skills_library:

        if skill in resume_lower:
            detected_skills.append(skill)

    st.subheader("🎯 Detected Skills")

    if detected_skills:

        col1, col2, col3 = st.columns(3)

        for i, skill in enumerate(detected_skills):

            if i % 3 == 0:
                col1.success(skill.title())

            elif i % 3 == 1:
                col2.success(skill.title())

            else:
                col3.success(skill.title())

    else:

        st.warning(
            "No skills detected."
        )

    # =========================
    # LOAD JOBS
    # =========================

    st.divider()

    st.subheader(
        "🤖 AI Job Recommendations"
    )

    conn = psycopg2.connect(
        host="localhost",
        database="job_market_db",
        user="postgres",
        password="shruti65"
    )

    jobs = pd.read_sql(
        """
        SELECT *
        FROM jobs
        LIMIT 500
        """,
        conn
    )

    conn.close()

    # =========================
    # MATCHING ENGINE
    # =========================

    results = []

    for _, job in jobs.iterrows():

        score = 0

        title = str(
            job["title"]
        ).lower()

        description = str(
            job["description"]
        ).lower()

        job_text = (
            title + " " + description
        )

        for skill in detected_skills:

            if skill.lower() in job_text:
                score += 1

        if len(detected_skills) > 0:

            match_score = round(
                (
                    score /
                    len(detected_skills)
                ) * 100,
                2
            )

        else:

            match_score = 0

        results.append(
            {
                "title": job["title"],
                "company": job["company"],
                "country": job["country"],
                "score": match_score,
                "url": job["redirect_url"]
            }
        )

    # =========================
    # TOP MATCHES
    # =========================

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        "score",
        ascending=False
    )

    top_jobs = results_df.head(10)

    st.metric(
        "Recommended Jobs",
        len(top_jobs)
    )

    st.divider()

    for _, row in top_jobs.iterrows():

        st.subheader(
            row["title"]
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"🏢 Company: {row['company']}"
            )

            st.write(
                f"🌍 Country: {row['country']}"
            )

        with col2:

            st.write(
                f"🎯 Match Score: {row['score']}%"
            )

            st.progress(
                min(
                    int(row["score"]),
                    100
                )
            )

        if pd.notna(
            row["url"]
        ):

            st.link_button(
                "🚀 Apply Now",
                row["url"]
            )

        st.divider()

    # =========================
    # TOP MATCH TABLE
    # =========================

    with st.expander(
        "📊 View Recommendation Table"
    ):

        st.dataframe(
            top_jobs,
            use_container_width=True
        )