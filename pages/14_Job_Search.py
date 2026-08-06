import streamlit as st
import pandas as pd
import psycopg2
import subprocess
import sys
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Job Search",
    layout="wide"
)

st.title("🔍 Job Search")

# =========================
# LOGIN CHECK
# =========================

if "user_id" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()

# =========================
# LIVE JOB INGESTION
# =========================

col_title, col_fetch = st.columns([3, 1])

with col_fetch:

    if st.button(
        "🔄 Fetch Latest Jobs from All Platforms"
    ):

        with st.spinner(
            "Fetching latest jobs from "
            "Adzuna, LinkedIn, Indeed, "
            "Glassdoor, Arbeitnow..."
        ):

            subprocess.run(
                [sys.executable, "src/pipeline.py"]
            )

        st.success(
            "Latest jobs fetched from all platforms!"
        )
        st.rerun()

st.markdown("---")

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
# SEARCH & FILTERS
# =========================

col1, col2 = st.columns([2, 1])

with col1:
    search = st.text_input(
        "Search Job Role, Title or Company",
        placeholder=(
            "e.g. Data Analyst, Data Scientist, "
            "Python..."
        )
    )

with col2:
    # Country Filter
    countries_df = pd.read_sql("""
        SELECT DISTINCT country
        FROM jobs
        WHERE is_released = TRUE
        ORDER BY country
    """, conn)

    selected_country = st.selectbox(
        "Filter by Country",
        ["All Countries"]
        + countries_df["country"].tolist()
    )

# Source & Date Filters
col3, col4 = st.columns(2)

with col3:
    # Source Platform Filter
    try:
        sources_df = pd.read_sql("""
            SELECT DISTINCT source
            FROM jobs
            WHERE is_released = TRUE
            AND source IS NOT NULL
            ORDER BY source
        """, conn)

        source_list = sources_df["source"].tolist()
    except Exception:
        source_list = []

    selected_source = st.selectbox(
        "🌐 Filter by Platform",
        ["All Platforms"] + source_list
    )

with col4:
    # Date Freshness Filter
    date_filter = st.selectbox(
        "📅 Posted Within",
        [
            "All Time",
            "Today",
            "Last 3 Days",
            "Last 7 Days",
            "Last 14 Days",
            "Last 30 Days"
        ]
    )

# =========================
# QUERY JOBS (NEWEST FIRST)
# =========================

query = """
SELECT *
FROM jobs
WHERE is_released = TRUE
"""

params = []

if search:
    query += (
        " AND (title ILIKE %s "
        "OR company ILIKE %s "
        "OR search_term ILIKE %s)"
    )
    search_param = f"%{search}%"
    params.extend([
        search_param,
        search_param,
        search_param
    ])

if selected_country != "All Countries":
    query += " AND country = %s"
    params.append(selected_country)

if selected_source != "All Platforms":
    query += " AND source = %s"
    params.append(selected_source)

# Date filter
date_map = {
    "Today": 1,
    "Last 3 Days": 3,
    "Last 7 Days": 7,
    "Last 14 Days": 14,
    "Last 30 Days": 30
}

if date_filter in date_map:
    days = date_map[date_filter]
    cutoff = (
        datetime.now() - timedelta(days=days)
    ).strftime("%Y-%m-%d")
    query += " AND created >= %s"
    params.append(cutoff)

query += " ORDER BY created DESC LIMIT 200"

jobs = pd.read_sql(
    query, conn,
    params=params if params else None
)

st.write(
    f"### 📋 Jobs Found: **{len(jobs)}** "
    f"*(Sorted by Newest First)*"
)

# Source breakdown badges
if not jobs.empty and "source" in jobs.columns:
    source_counts = jobs["source"].value_counts()
    badges = " | ".join([
        f"**{src}**: {cnt}"
        for src, cnt in source_counts.items()
    ])
    st.caption(f"📊 Sources: {badges}")

st.divider()

# =========================
# SOURCE BADGES
# =========================

SOURCE_BADGES = {
    "LinkedIn": "🔵 LinkedIn",
    "Indeed": "🟣 Indeed",
    "Glassdoor": "🟢 Glassdoor",
    "Adzuna": "🟠 Adzuna",
    "Arbeitnow": "🔴 Arbeitnow",
    "ZipRecruiter": "🟡 ZipRecruiter",
    "JSearch": "⚪ JSearch"
}

# =========================
# DISPLAY JOBS
# =========================

if jobs.empty:

    st.info(
        "No matching jobs found. "
        "Try adjusting your search term or filter."
    )

else:

    for index, job in jobs.iterrows():

        st.subheader(
            job["title"]
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"🏢 **Company**: {job['company']}"
            )

            st.write(
                f"🌍 **Country**: {job['country']}"
            )

            if pd.notna(job.get("location")):
                st.write(
                    f"📍 **Location**: "
                    f"{job['location']}"
                )

            if pd.notna(job.get("created")):
                st.caption(
                    f"📅 **Posted Date**: "
                    f"{str(job['created'])[:16]}"
                )

        with col2:

            # Source badge
            source = job.get("source", "Unknown")
            badge = SOURCE_BADGES.get(
                source,
                f"🔘 {source}"
            )
            st.write(f"🌐 **Source**: {badge}")

            if (
                pd.notna(job.get("salary_min"))
                and pd.notna(job.get("salary_max"))
            ):
                if (
                    job["salary_min"] > 0
                    and job["salary_max"] > 0
                ):
                    st.write(
                        f"💰 **Salary Range**: "
                        f"€{job['salary_min']:,.0f}"
                        f" - "
                        f"€{job['salary_max']:,.0f}"
                    )

            if pd.notna(job.get("redirect_url")):

                st.link_button(
                    "🚀 Apply Now — Opens Application Page",
                    job["redirect_url"]
                )

        # Action Buttons Row
        col_btn1, col_btn2 = st.columns([1, 5])

        with col_btn1:
            if st.button(
                "❤️ Save Job",
                key=(
                    f"save_{index}_"
                    f"{job.get('title', '')[:10]}"
                )
            ):

                cur = conn.cursor()

                cur.execute("""
                INSERT INTO saved_jobs
                (
                    applicant_id,
                    job_title,
                    company,
                    country,
                    job_url
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    st.session_state["user_id"],
                    job["title"],
                    job["company"],
                    job["country"],
                    job.get("redirect_url", "")
                ))

                conn.commit()
                cur.close()

                st.success(
                    "Job Saved Successfully"
                )

        with col_btn2:
            if st.button(
                "📌 Apply",
                key=(
                    f"apply_{index}_"
                    f"{job.get('title', '')[:10]}"
                )
            ):

                cur = conn.cursor()

                cur.execute("""
                INSERT INTO applications
                (
                    applicant_id,
                    job_title,
                    company,
                    country,
                    job_url,
                    status
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    st.session_state["user_id"],
                    job["title"],
                    job["company"],
                    job["country"],
                    job.get("redirect_url", ""),
                    "Applied"
                ))

                conn.commit()
                cur.close()

                st.success(
                    "Application Added Successfully"
                )

        st.divider()

conn.close()