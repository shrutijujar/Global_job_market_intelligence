import streamlit as st
import pandas as pd
import psycopg2
import sys
import os

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "src"
))

from admin_utils import (
    get_db_connection,
    release_job_by_index,
    release_all_jobs,
    send_release_emails,
    log_admin_action
)

st.set_page_config(
    page_title="Admin Job Review",
    page_icon="📋",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    .job-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 75, 75, 0.15);
        margin-bottom: 1rem;
    }
    .release-btn {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
    }
    .pending-badge {
        background: #FF9800;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .released-badge {
        background: #4CAF50;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# AUTH CHECK
# =========================

if not st.session_state.get("admin_logged_in"):

    st.warning(
        "Please login as admin first. "
        "Go to **Admin Login** page."
    )

    st.stop()

admin_username = st.session_state["admin_username"]

# =========================
# HEADER
# =========================

st.title("📋 Admin Job Review & Release")

st.caption(
    "Review pending jobs and release them to "
    "the platform. Released jobs become visible "
    "to users and trigger email notifications."
)

st.markdown("---")

# =========================
# TABS
# =========================

tab_pending, tab_released, tab_all = st.tabs([
    "⏳ Pending Jobs",
    "✅ Released Jobs",
    "📊 All Jobs"
])

# =========================
# TAB 1: PENDING JOBS
# =========================

with tab_pending:

    conn = get_db_connection()

    # Count
    pending_count = pd.read_sql("""
        SELECT COUNT(*) as count
        FROM jobs
        WHERE is_released = FALSE
        OR is_released IS NULL
    """, conn).iloc[0]["count"]

    st.metric(
        "Pending Jobs",
        f"{pending_count:,}"
    )

    if pending_count > 0:

        # Bulk release
        col1, col2 = st.columns([3, 1])

        with col2:

            if st.button(
                "🚀 Release All Pending",
                key="bulk_release"
            ):

                count = release_all_jobs(
                    admin_username
                )

                st.success(
                    f"Released {count} jobs!"
                )

                st.rerun()

        st.divider()

        # Search / Filter
        col_search, col_country = st.columns(2)

        with col_search:
            search = st.text_input(
                "🔍 Search Job Title",
                key="pending_search"
            )

        with col_country:
            countries = pd.read_sql("""
                SELECT DISTINCT country
                FROM jobs
                WHERE is_released = FALSE
                OR is_released IS NULL
                ORDER BY country
            """, conn)["country"].tolist()

            selected_country = st.selectbox(
                "🌍 Filter by Country",
                ["All"] + countries,
                key="pending_country"
            )

        # Load pending jobs
        query = """
            SELECT
                title,
                company,
                country,
                location,
                salary_min,
                salary_max,
                search_term,
                created,
                redirect_url,
                COALESCE(source, 'Adzuna') as source
            FROM jobs
            WHERE (is_released = FALSE OR is_released IS NULL)
        """

        params = []

        if selected_country != "All":
            query += " AND country = %s"
            params.append(selected_country)

        query += " ORDER BY created DESC LIMIT 200"

        pending_jobs = pd.read_sql(
            query, conn, params=params
        )

        if search:
            pending_jobs = pending_jobs[
                pending_jobs["title"].str.contains(
                    search, case=False, na=False
                )
            ]

        st.write(
            f"Showing **{len(pending_jobs)}** pending jobs"
        )

        st.divider()

        # Display each job
        for idx, job in pending_jobs.iterrows():

            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:

                st.subheader(job["title"])

                st.write(
                    f"🏢 **{job['company']}** | "
                    f"🌍 {job['country']} | "
                    f"📍 {job['location']}"
                )

                if pd.notna(job["salary_min"]) and pd.notna(job["salary_max"]):
                    st.write(
                        f"💰 Salary: {job['salary_min']:,.0f} - "
                        f"{job['salary_max']:,.0f}"
                    )

                st.caption(
                    f"Category: {job['search_term']} | "
                    f"Source: {job.get('source', 'Adzuna')} | "
                    f"Posted: {job['created']}"
                )

            with col2:

                if pd.notna(job["redirect_url"]):
                    st.link_button(
                        "🔗 View Original",
                        job["redirect_url"],
                        key=f"link_{idx}"
                    )

            with col3:

                if st.button(
                    "✅ Release",
                    key=f"release_{idx}"
                ):

                    release_job_by_index(
                        job["title"],
                        job["company"],
                        admin_username
                    )

                    # Send emails
                    sent = send_release_emails(
                        job["title"],
                        job["company"],
                        job["country"],
                        job["redirect_url"]
                        if pd.notna(job["redirect_url"])
                        else ""
                    )

                    if sent > 0:
                        st.success(
                            f"Released & {sent} email(s) sent!"
                        )
                    else:
                        st.success("Job released!")

                    st.rerun()

            st.divider()

    else:

        st.success(
            "All jobs have been released! "
            "No pending jobs."
        )

    conn.close()

# =========================
# TAB 2: RELEASED JOBS
# =========================

with tab_released:

    conn = get_db_connection()

    released_count = pd.read_sql("""
        SELECT COUNT(*) as count
        FROM jobs
        WHERE is_released = TRUE
    """, conn).iloc[0]["count"]

    st.metric(
        "Released Jobs",
        f"{released_count:,}"
    )

    st.divider()

    # Search
    search_released = st.text_input(
        "🔍 Search Released Jobs",
        key="released_search"
    )

    released_jobs = pd.read_sql("""
        SELECT
            title,
            company,
            country,
            location,
            salary_min,
            salary_max,
            search_term,
            created,
            COALESCE(source, 'Adzuna') as source
        FROM jobs
        WHERE is_released = TRUE
        ORDER BY created DESC
        LIMIT 200
    """, conn)

    if search_released:

        released_jobs = released_jobs[
            released_jobs["title"].str.contains(
                search_released, case=False, na=False
            )
        ]

    st.dataframe(
        released_jobs,
        use_container_width=True
    )

    conn.close()

# =========================
# TAB 3: ALL JOBS
# =========================

with tab_all:

    conn = get_db_connection()

    all_jobs = pd.read_sql("""
        SELECT
            title,
            company,
            country,
            is_released,
            salary_min,
            salary_max,
            search_term,
            created,
            COALESCE(source, 'Adzuna') as source
        FROM jobs
        ORDER BY created DESC
        LIMIT 500
    """, conn)

    all_jobs["Status"] = all_jobs["is_released"].apply(
        lambda x: "Released"
        if x else "Pending"
    )

    st.metric(
        "Total Jobs",
        f"{len(all_jobs):,}"
    )

    # Filter
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Released", "Pending"],
        key="all_jobs_filter"
    )

    if status_filter == "Released":
        all_jobs = all_jobs[
            all_jobs["is_released"] == True
        ]
    elif status_filter == "Pending":
        all_jobs = all_jobs[
            (all_jobs["is_released"] == False)
            | (all_jobs["is_released"].isna())
        ]

    st.dataframe(
        all_jobs[[
            "title", "company", "country",
            "Status", "source", "salary_min",
            "salary_max", "search_term",
            "created"
        ]],
        use_container_width=True
    )

    conn.close()
