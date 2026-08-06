import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(
    page_title="AI Recommendations",
    layout="wide"
)

st.title("🤖 AI Job Recommendations")

if "user_id" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()

conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)

# User Preferences

pref = pd.read_sql("""
SELECT *
FROM applicant_preferences
WHERE applicant_id=%s
""",
conn,
params=(
    st.session_state["user_id"],
))
if pref.empty:
    
    st.info(
        "No preferences found."
    )

else:

    country = pref.iloc[0]["country"]
    role = pref.iloc[0]["job_role"]

    st.success(
        f"Recommendations for {role} in {country}"
    )

    jobs = pd.read_sql("""
    SELECT *
    FROM jobs
    WHERE country=%s
    """,
    conn,
    params=(country,))
    recommended = jobs[
        jobs["title"]
        .str.contains(
            role.split()[0],
            case=False,
            na=False
        )
    ]

    for _, job in recommended.head(20).iterrows():

        st.subheader(
            job["title"]
        )

        st.write(
            f"🏢 {job['company']}"
        )

        st.write(
            f"🌍 {job['country']}"
        )

        if pd.notna(
            job["redirect_url"]
        ):

            st.link_button(
                "Apply",
                job["redirect_url"]
            )

        st.divider()

conn.close()