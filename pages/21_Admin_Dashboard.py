import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "src"
))

from admin_utils import (
    get_db_connection,
    get_admin_stats,
    ban_user,
    unban_user,
    release_all_jobs,
    release_job_by_index,
    log_admin_action,
    send_release_emails
)

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛡",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    .admin-title {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 50%, #FF8B8B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid rgba(255, 75, 75, 0.15);
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #FF4B4B;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #888;
        margin-top: 0.3rem;
    }
    .section-divider {
        border-top: 2px solid rgba(255, 75, 75, 0.2);
        margin: 2rem 0;
    }
    .ban-active {
        color: #FF4B4B;
        font-weight: 600;
    }
    .ban-inactive {
        color: #4CAF50;
        font-weight: 600;
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

st.markdown(
    '<p class="admin-title">'
    'Admin Dashboard'
    '</p>',
    unsafe_allow_html=True
)

st.caption(
    f"Logged in as: **{admin_username}** | "
    f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)

st.markdown("---")

# =========================
# TABS
# =========================

(
    tab_dashboard,
    tab_users,
    tab_login_history,
    tab_block,
    tab_activity,
    tab_jobs,
    tab_email,
    tab_alerts,
    tab_logs
) = st.tabs([
    "📊 Dashboard",
    "👥 User Management",
    "📋 Login History",
    "🚫 Block/Unblock",
    "📈 User Activity",
    "💼 Job Statistics",
    "📧 Email Statistics",
    "🔔 Alerts Monitoring",
    "📝 System Logs"
])

# =============================================
# TAB 1: DASHBOARD
# =============================================

with tab_dashboard:

    st.subheader("📊 Platform Overview")

    stats = get_admin_stats()

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "👥 Total Users",
        stats["total_users"]
    )

    c2.metric(
        "✅ Active Users",
        stats["active_users"]
    )

    c3.metric(
        "🚫 Banned Users",
        stats["banned_users"]
    )

    c4.metric(
        "💼 Total Jobs",
        f"{stats['total_jobs']:,}"
    )

    # KPI Row 2
    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "✅ Released Jobs",
        f"{stats['released_jobs']:,}"
    )

    c6.metric(
        "⏳ Pending Jobs",
        f"{stats['pending_jobs']:,}"
    )

    c7.metric(
        "📌 Applications",
        stats["total_applications"]
    )

    c8.metric(
        "📧 Alerts Sent",
        stats["total_alerts"]
    )

    st.divider()

    # Charts
    conn = get_db_connection()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("👥 User Registrations")

        users_df = pd.read_sql("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as registrations
            FROM applicants
            GROUP BY DATE(created_at)
            ORDER BY date
        """, conn)

        if not users_df.empty:

            fig = px.area(
                users_df,
                x="date",
                y="registrations",
                title="User Registrations Over Time"
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("No registration data yet.")

    with col2:

        st.subheader("🌍 Jobs by Country")

        jobs_country = pd.read_sql("""
            SELECT
                country,
                COUNT(*) as jobs
            FROM jobs
            GROUP BY country
            ORDER BY jobs DESC
        """, conn)

        if not jobs_country.empty:

            fig = px.pie(
                jobs_country,
                names="country",
                values="jobs",
                title="Job Distribution by Country",
                hole=0.4
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    conn.close()

# =============================================
# TAB 2: USER MANAGEMENT
# =============================================

with tab_users:

    st.subheader("👥 All Registered Users")

    conn = get_db_connection()

    users = pd.read_sql("""
        SELECT
            id,
            name,
            email,
            preferred_country,
            preferred_role,
            is_banned,
            created_at
        FROM applicants
        ORDER BY created_at DESC
    """, conn)

    # Search
    search_user = st.text_input(
        "🔍 Search by name or email",
        key="search_users"
    )

    if search_user:

        users = users[
            users["name"].str.contains(
                search_user, case=False, na=False
            )
            |
            users["email"].str.contains(
                search_user, case=False, na=False
            )
        ]

    st.write(f"Total Users: **{len(users)}**")

    # Add status column
    users["Status"] = users["is_banned"].apply(
        lambda x: "BANNED" if x else "Active"
    )

    st.dataframe(
        users[[
            "id", "name", "email",
            "preferred_country",
            "preferred_role",
            "Status", "created_at"
        ]],
        use_container_width=True
    )

    # User Detail View
    st.divider()

    st.subheader("🔍 View User Details")

    user_ids = users["id"].tolist()

    if user_ids:

        selected_user_id = st.selectbox(
            "Select User ID",
            user_ids,
            key="user_detail_select"
        )

        if st.button(
            "View Full Details",
            key="view_user_btn"
        ):

            # User Info
            user_info = pd.read_sql(
                "SELECT * FROM applicants WHERE id=%s",
                conn,
                params=(selected_user_id,)
            )

            st.write("**User Info:**")
            st.dataframe(
                user_info,
                use_container_width=True
            )

            # Saved Jobs
            saved = pd.read_sql(
                "SELECT * FROM saved_jobs WHERE applicant_id=%s",
                conn,
                params=(selected_user_id,)
            )

            st.write(
                f"**Saved Jobs: {len(saved)}**"
            )

            if not saved.empty:
                st.dataframe(
                    saved,
                    use_container_width=True
                )

            # Applications
            apps = pd.read_sql(
                "SELECT * FROM applications WHERE applicant_id=%s",
                conn,
                params=(selected_user_id,)
            )

            st.write(
                f"**Applications: {len(apps)}**"
            )

            if not apps.empty:
                st.dataframe(
                    apps,
                    use_container_width=True
                )

            # Preferences
            prefs = pd.read_sql(
                "SELECT * FROM applicant_preferences WHERE applicant_id=%s",
                conn,
                params=(selected_user_id,)
            )

            st.write(
                f"**Preferences: {len(prefs)}**"
            )

            if not prefs.empty:
                st.dataframe(
                    prefs,
                    use_container_width=True
                )

            # Notifications
            notifs = pd.read_sql(
                "SELECT * FROM notifications WHERE applicant_id=%s ORDER BY created_at DESC",
                conn,
                params=(selected_user_id,)
            )

            st.write(
                f"**Notifications: {len(notifs)}**"
            )

            if not notifs.empty:
                st.dataframe(
                    notifs,
                    use_container_width=True
                )

    conn.close()

# =============================================
# TAB 3: LOGIN HISTORY
# =============================================

with tab_login_history:

    st.subheader("📋 User Login History")

    conn = get_db_connection()

    login_logs = pd.read_sql("""
        SELECT
            lh.id,
            a.name,
            a.email,
            lh.login_time,
            lh.status
        FROM login_history lh
        LEFT JOIN applicants a
        ON lh.applicant_id = a.id
        ORDER BY lh.login_time DESC
        LIMIT 500
    """, conn)

    if login_logs.empty:

        st.info(
            "No login history recorded yet. "
            "Logins will appear here after users log in."
        )

    else:

        st.metric(
            "Total Logins Recorded",
            len(login_logs)
        )

        st.dataframe(
            login_logs,
            use_container_width=True
        )

        # Login trend chart
        login_logs["date"] = pd.to_datetime(
            login_logs["login_time"]
        ).dt.date

        daily_logins = (
            login_logs.groupby("date")
            .size()
            .reset_index(name="logins")
        )

        fig = px.bar(
            daily_logins,
            x="date",
            y="logins",
            title="Daily Login Activity"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    conn.close()

# =============================================
# TAB 4: BLOCK / UNBLOCK USERS
# =============================================

with tab_block:

    st.subheader("🚫 Block / Unblock Users")

    conn = get_db_connection()

    all_users = pd.read_sql("""
        SELECT
            id, name, email,
            is_banned, banned_at, ban_reason
        FROM applicants
        ORDER BY is_banned DESC, name ASC
    """, conn)

    conn.close()

    if all_users.empty:

        st.info("No users found.")

    else:

        for _, user in all_users.iterrows():

            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:

                status_icon = (
                    "🔴" if user["is_banned"]
                    else "🟢"
                )

                st.write(
                    f"{status_icon} **{user['name']}** "
                    f"({user['email']})"
                )

                if user["is_banned"]:

                    st.caption(
                        f"Banned at: {user['banned_at']} | "
                        f"Reason: {user['ban_reason']}"
                    )

            with col2:

                if not user["is_banned"]:

                    reason = st.text_input(
                        "Ban Reason",
                        key=f"reason_{user['id']}",
                        placeholder="Enter reason"
                    )

                    if st.button(
                        "🚫 Ban User",
                        key=f"ban_{user['id']}"
                    ):

                        if reason:

                            ban_user(
                                user["id"],
                                reason,
                                admin_username
                            )

                            st.success(
                                f"{user['name']} has been banned."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Please enter a ban reason."
                            )

            with col3:

                if user["is_banned"]:

                    if st.button(
                        "✅ Unban User",
                        key=f"unban_{user['id']}"
                    ):

                        unban_user(
                            user["id"],
                            admin_username
                        )

                        st.success(
                            f"{user['name']} has been unbanned."
                        )

                        st.rerun()

            st.divider()

# =============================================
# TAB 5: USER ACTIVITY
# =============================================

with tab_activity:

    st.subheader("📈 User Activity Overview")

    conn = get_db_connection()

    # Per-user activity
    activity = pd.read_sql("""
        SELECT
            a.id,
            a.name,
            a.email,
            COALESCE(sj.saved_count, 0) as saved_jobs,
            COALESCE(ap.app_count, 0) as applications,
            COALESCE(sa.alert_count, 0) as alerts_received,
            COALESCE(pf.pref_count, 0) as preferences_set
        FROM applicants a
        LEFT JOIN (
            SELECT applicant_id, COUNT(*) as saved_count
            FROM saved_jobs GROUP BY applicant_id
        ) sj ON a.id = sj.applicant_id
        LEFT JOIN (
            SELECT applicant_id, COUNT(*) as app_count
            FROM applications GROUP BY applicant_id
        ) ap ON a.id = ap.applicant_id
        LEFT JOIN (
            SELECT applicant_id, COUNT(*) as alert_count
            FROM sent_alerts GROUP BY applicant_id
        ) sa ON a.id = sa.applicant_id
        LEFT JOIN (
            SELECT applicant_id, COUNT(*) as pref_count
            FROM applicant_preferences GROUP BY applicant_id
        ) pf ON a.id = pf.applicant_id
        ORDER BY applications DESC
    """, conn)

    if activity.empty:

        st.info("No user activity data.")

    else:

        st.dataframe(
            activity,
            use_container_width=True
        )

        st.divider()

        # Activity Charts
        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                activity.head(20),
                x="name",
                y="applications",
                title="Applications per User",
                color="applications"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                activity.head(20),
                x="name",
                y="saved_jobs",
                title="Saved Jobs per User",
                color="saved_jobs"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    conn.close()

# =============================================
# TAB 6: JOB STATISTICS
# =============================================

with tab_jobs:

    st.subheader("💼 Job Statistics")

    conn = get_db_connection()

    stats = get_admin_stats()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Jobs",
        f"{stats['total_jobs']:,}"
    )

    c2.metric(
        "Released",
        f"{stats['released_jobs']:,}"
    )

    c3.metric(
        "Pending",
        f"{stats['pending_jobs']:,}"
    )

    release_pct = 0
    if stats["total_jobs"] > 0:
        release_pct = round(
            (stats["released_jobs"] / stats["total_jobs"]) * 100
        )

    c4.metric(
        "Release Rate",
        f"{release_pct}%"
    )

    st.divider()

    # Bulk Release
    if stats["pending_jobs"] > 0:

        st.warning(
            f"There are **{stats['pending_jobs']}** "
            f"pending jobs awaiting release."
        )

        if st.button(
            "🚀 Release All Pending Jobs",
            key="release_all_btn"
        ):

            count = release_all_jobs(admin_username)

            st.success(
                f"Released {count} jobs successfully!"
            )

            st.rerun()

    st.divider()

    # Jobs by Country
    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🌍 Jobs by Country")

        country_stats = pd.read_sql("""
            SELECT
                country,
                COUNT(*) as total,
                SUM(CASE WHEN is_released = TRUE THEN 1 ELSE 0 END) as released,
                SUM(CASE WHEN is_released = FALSE OR is_released IS NULL THEN 1 ELSE 0 END) as pending
            FROM jobs
            GROUP BY country
            ORDER BY total DESC
        """, conn)

        st.dataframe(
            country_stats,
            use_container_width=True
        )

    with col2:

        st.subheader("🔍 Jobs by Search Term")

        term_stats = pd.read_sql("""
            SELECT
                search_term,
                COUNT(*) as jobs
            FROM jobs
            GROUP BY search_term
            ORDER BY jobs DESC
        """, conn)

        fig = px.bar(
            term_stats,
            x="search_term",
            y="jobs",
            color="jobs",
            title="Jobs by Search Term"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Salary Distribution
    st.divider()

    st.subheader("💰 Salary Distribution")

    salary_data = pd.read_sql("""
        SELECT
            country,
            salary_min,
            salary_max,
            (COALESCE(salary_min,0) + COALESCE(salary_max,0)) / 2 as avg_salary
        FROM jobs
        WHERE salary_min > 0
        AND salary_max > 0
    """, conn)

    if not salary_data.empty:

        fig = px.box(
            salary_data,
            x="country",
            y="avg_salary",
            color="country",
            title="Salary Distribution by Country"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    conn.close()

# =============================================
# TAB 7: EMAIL STATISTICS
# =============================================

with tab_email:

    st.subheader("📧 Email & Alert Statistics")

    conn = get_db_connection()

    # KPIs
    c1, c2, c3 = st.columns(3)

    alert_count = pd.read_sql(
        "SELECT COUNT(*) as count FROM sent_alerts",
        conn
    ).iloc[0]["count"]

    notif_count = pd.read_sql(
        "SELECT COUNT(*) as count FROM notifications",
        conn
    ).iloc[0]["count"]

    unique_recipients = pd.read_sql("""
        SELECT COUNT(DISTINCT applicant_id) as count
        FROM sent_alerts
    """, conn).iloc[0]["count"]

    c1.metric("Total Emails Sent", alert_count)
    c2.metric("Total Notifications", notif_count)
    c3.metric("Unique Recipients", unique_recipients)

    st.divider()

    # Emails by User
    st.subheader("📊 Emails by User")

    email_by_user = pd.read_sql("""
        SELECT
            a.name,
            a.email,
            COUNT(sa.id) as emails_sent
        FROM sent_alerts sa
        JOIN applicants a
        ON sa.applicant_id = a.id
        GROUP BY a.name, a.email
        ORDER BY emails_sent DESC
    """, conn)

    if not email_by_user.empty:

        st.dataframe(
            email_by_user,
            use_container_width=True
        )

        fig = px.bar(
            email_by_user,
            x="name",
            y="emails_sent",
            color="emails_sent",
            title="Emails Sent per User"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No email records found.")

    # Recent Alerts
    st.divider()

    st.subheader("🕐 Recent Email Activity")

    recent_alerts = pd.read_sql("""
        SELECT
            sa.id,
            a.name,
            a.email,
            sa.job_title,
            sa.sent_at
        FROM sent_alerts sa
        JOIN applicants a
        ON sa.applicant_id = a.id
        ORDER BY sa.sent_at DESC
        LIMIT 50
    """, conn)

    if not recent_alerts.empty:

        st.dataframe(
            recent_alerts,
            use_container_width=True
        )

    else:
        st.info("No recent alerts.")

    conn.close()

# =============================================
# TAB 8: ALERTS MONITORING
# =============================================

with tab_alerts:

    st.subheader("🔔 Alerts & Notifications Monitoring")

    conn = get_db_connection()

    # Filter
    filter_status = st.selectbox(
        "Filter by Status",
        ["All", "Unread", "Read"],
        key="alert_filter"
    )

    notif_query = """
        SELECT
            n.id,
            a.name,
            a.email,
            n.title as job_title,
            n.company,
            n.country,
            n.is_read,
            n.created_at
        FROM notifications n
        LEFT JOIN applicants a
        ON n.applicant_id = a.id
        {where_clause}
        ORDER BY n.created_at DESC
        LIMIT 500
    """

    if filter_status == "Unread":
        where = "WHERE n.is_read = FALSE"

    elif filter_status == "Read":
        where = "WHERE n.is_read = TRUE"

    else:
        where = ""

    notifications = pd.read_sql(
        notif_query.format(where_clause=where),
        conn
    )

    # KPIs
    c1, c2 = st.columns(2)

    total_notifs = pd.read_sql(
        "SELECT COUNT(*) as c FROM notifications",
        conn
    ).iloc[0]["c"]

    unread_notifs = pd.read_sql(
        "SELECT COUNT(*) as c FROM notifications WHERE is_read = FALSE",
        conn
    ).iloc[0]["c"]

    c1.metric("Total Notifications", total_notifs)
    c2.metric("Unread Notifications", unread_notifs)

    st.divider()

    if not notifications.empty:

        notifications["Status"] = notifications["is_read"].apply(
            lambda x: "Read" if x else "Unread"
        )

        st.dataframe(
            notifications[[
                "id", "name", "email",
                "job_title", "company",
                "country", "Status",
                "created_at"
            ]],
            use_container_width=True
        )

        # Timeline
        notifications["date"] = pd.to_datetime(
            notifications["created_at"]
        ).dt.date

        daily = (
            notifications.groupby("date")
            .size()
            .reset_index(name="alerts")
        )

        fig = px.line(
            daily,
            x="date",
            y="alerts",
            title="Alert Delivery Timeline"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No notifications found.")

    conn.close()

# =============================================
# TAB 9: SYSTEM LOGS
# =============================================

with tab_logs:

    st.subheader("📝 Admin Activity Logs")

    conn = get_db_connection()

    # Search
    log_search = st.text_input(
        "🔍 Search logs",
        key="log_search",
        placeholder="Search by action, username, or details"
    )

    log_query = """
        SELECT
            id,
            admin_username,
            action,
            target_user_id,
            details,
            created_at
        FROM admin_activity_log
        ORDER BY created_at DESC
        LIMIT 500
    """

    logs = pd.read_sql(log_query, conn)

    if log_search and not logs.empty:

        logs = logs[
            logs["action"].str.contains(
                log_search, case=False, na=False
            )
            |
            logs["admin_username"].str.contains(
                log_search, case=False, na=False
            )
            |
            logs["details"].str.contains(
                log_search, case=False, na=False
            )
        ]

    if not logs.empty:

        st.metric(
            "Total Log Entries",
            len(logs)
        )

        st.dataframe(
            logs,
            use_container_width=True
        )

        # Action breakdown
        action_counts = (
            logs["action"]
            .value_counts()
            .reset_index()
        )

        action_counts.columns = [
            "Action", "Count"
        ]

        fig = px.pie(
            action_counts,
            names="Action",
            values="Count",
            title="Admin Actions Breakdown",
            hole=0.5
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No admin activity logs yet. "
            "Actions like ban/unban/release will appear here."
        )

    conn.close()
