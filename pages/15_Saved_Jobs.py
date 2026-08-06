import streamlit as st
import pandas as pd
import psycopg2

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Saved Jobs",
    layout="wide"
)

st.title("❤️ Saved Jobs")

# =========================
# LOGIN CHECK
# =========================

if "user_id" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()

# =========================
# DATABASE CONNECTION
# =========================

conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)

# =========================
# LOAD SAVED JOBS
# =========================

query = """
SELECT
    id,
    job_title,
    company,
    country,
    job_url,
    saved_at
FROM saved_jobs
WHERE applicant_id=%s
ORDER BY saved_at DESC
"""

saved_jobs = pd.read_sql(
    query,
    conn,
    params=(
        st.session_state["user_id"],
    )
)

# =========================
# HEADER
# =========================

st.metric(
    "Total Saved Jobs",
    len(saved_jobs)
)

st.divider()

# =========================
# NO JOBS
# =========================

if saved_jobs.empty:

    st.info(
        "No saved jobs found. Go to Job Search and save some jobs."
    )

# =========================
# DISPLAY JOBS
# =========================

else:

    for _, job in saved_jobs.iterrows():

        st.subheader(
            job["job_title"]
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"🏢 Company: {job['company']}"
            )

            st.write(
                f"🌍 Country: {job['country']}"
            )

        with col2:

            st.write(
                f"📅 Saved: {job['saved_at']}"
            )

        if pd.notna(job["job_url"]):

            st.link_button(
                "🚀 Open Job",
                job["job_url"]
            )

        # Delete Saved Job
        if st.button(
            "🗑 Remove",
            key=f"delete_{job['id']}"
        ):

            cur = conn.cursor()

            cur.execute(
                """
                DELETE FROM saved_jobs
                WHERE id=%s
                """,
                (job["id"],)
            )

            conn.commit()

            cur.close()

            st.success(
                "Job removed successfully"
            )

            st.rerun()

        st.divider()

# =========================
# RAW DATA VIEW
# =========================

with st.expander(
    "📊 View Saved Jobs Table"
):

    st.dataframe(
        saved_jobs,
        use_container_width=True
    )

conn.close()