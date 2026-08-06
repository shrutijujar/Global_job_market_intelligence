"""
Admin Utility Functions
Shared helpers for the admin dashboard pages.
"""

import psycopg2
import pandas as pd
from datetime import datetime


def get_db_connection():
    """Returns a psycopg2 connection."""

    return psycopg2.connect(
        host="localhost",
        database="job_market_db",
        user="postgres",
        password="shruti65"
    )


def ban_user(user_id, reason, admin_username):
    """Ban a user and log the action."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE applicants
        SET is_banned = TRUE,
            banned_at = %s,
            ban_reason = %s
        WHERE id = %s
    """, (datetime.now(), reason, user_id))

    cur.execute("""
        INSERT INTO admin_activity_log
        (admin_username, action, target_user_id, details)
        VALUES (%s, %s, %s, %s)
    """, (
        admin_username,
        "BAN_USER",
        user_id,
        f"Reason: {reason}"
    ))

    conn.commit()
    cur.close()
    conn.close()


def unban_user(user_id, admin_username):
    """Unban a user and log the action."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE applicants
        SET is_banned = FALSE,
            banned_at = NULL,
            ban_reason = NULL
        WHERE id = %s
    """, (user_id,))

    cur.execute("""
        INSERT INTO admin_activity_log
        (admin_username, action, target_user_id, details)
        VALUES (%s, %s, %s, %s)
    """, (
        admin_username,
        "UNBAN_USER",
        user_id,
        "User unbanned"
    ))

    conn.commit()
    cur.close()
    conn.close()


def release_job_by_index(job_title, job_company, admin_username):
    """Release a specific job by title+company and log."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE jobs
        SET is_released = TRUE
        WHERE title = %s
        AND company = %s
        AND (is_released = FALSE OR is_released IS NULL)
    """, (job_title, job_company))

    cur.execute("""
        INSERT INTO admin_activity_log
        (admin_username, action, target_user_id, details)
        VALUES (%s, %s, %s, %s)
    """, (
        admin_username,
        "RELEASE_JOB",
        None,
        f"Released: {job_title} at {job_company}"
    ))

    conn.commit()
    cur.close()
    conn.close()


def release_all_jobs(admin_username):
    """Release all pending jobs."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE jobs
        SET is_released = TRUE
        WHERE is_released = FALSE
        OR is_released IS NULL
    """)

    count = cur.rowcount

    cur.execute("""
        INSERT INTO admin_activity_log
        (admin_username, action, target_user_id, details)
        VALUES (%s, %s, %s, %s)
    """, (
        admin_username,
        "RELEASE_ALL_JOBS",
        None,
        f"Bulk released {count} jobs"
    ))

    conn.commit()
    cur.close()
    conn.close()

    return count


def log_admin_action(admin_username, action, target_user_id, details):
    """Write an entry to the admin activity log."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO admin_activity_log
        (admin_username, action, target_user_id, details)
        VALUES (%s, %s, %s, %s)
    """, (
        admin_username,
        action,
        target_user_id,
        details
    ))

    conn.commit()
    cur.close()
    conn.close()


def log_login(applicant_id, status="success"):
    """Log a user login attempt."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO login_history
        (applicant_id, status)
        VALUES (%s, %s)
    """, (applicant_id, status))

    conn.commit()
    cur.close()
    conn.close()


def send_release_emails(job_title, job_company, job_country, job_url):
    """
    Send email alerts to users whose preferences
    match the released job.
    """

    conn = get_db_connection()
    cur = conn.cursor()

    # Find matching users
    cur.execute("""
        SELECT a.email, a.name, p.job_role
        FROM applicants a
        JOIN applicant_preferences p
        ON a.id = p.applicant_id
        WHERE a.is_banned = FALSE
        AND p.country = %s
    """, (job_country,))

    matching_users = cur.fetchall()

    cur.close()
    conn.close()

    if not matching_users:
        return 0

    try:
        import yagmail

        yag = yagmail.SMTP(
            "shrutijujar321@gmail.com",
            "ixlo vner ezan toir"
        )

        sent_count = 0

        for user_email, user_name, user_role in matching_users:

            # Check if job role matches
            if user_role and user_role.lower() in job_title.lower():

                body = f"""
Hello {user_name},

A new job has been released on our platform!

Title: {job_title}
Company: {job_company}
Country: {job_country}

Apply Here:
{job_url}

Best Regards,
Europe Job Market Intelligence Team
"""

                yag.send(
                    to=user_email,
                    subject=f"New Job Released: {job_title}",
                    contents=body
                )

                sent_count += 1

        return sent_count

    except Exception as e:
        print(f"Email error: {e}")
        return 0


def get_admin_stats():
    """Get summary statistics for admin dashboard."""

    conn = get_db_connection()

    stats = {}

    # Total users
    stats["total_users"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM applicants",
        conn
    ).iloc[0]["count"]

    # Banned users
    stats["banned_users"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM applicants WHERE is_banned = TRUE",
        conn
    ).iloc[0]["count"]

    # Active users
    stats["active_users"] = (
        stats["total_users"] - stats["banned_users"]
    )

    # Total jobs
    stats["total_jobs"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM jobs",
        conn
    ).iloc[0]["count"]

    # Released jobs
    stats["released_jobs"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM jobs WHERE is_released = TRUE",
        conn
    ).iloc[0]["count"]

    # Pending jobs
    stats["pending_jobs"] = (
        stats["total_jobs"] - stats["released_jobs"]
    )

    # Total applications
    stats["total_applications"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM applications",
        conn
    ).iloc[0]["count"]

    # Total alerts sent
    stats["total_alerts"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM sent_alerts",
        conn
    ).iloc[0]["count"]

    # Total notifications
    stats["total_notifications"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM notifications",
        conn
    ).iloc[0]["count"]

    # Total saved jobs
    stats["total_saved_jobs"] = pd.read_sql(
        "SELECT COUNT(*) as count FROM saved_jobs",
        conn
    ).iloc[0]["count"]

    conn.close()

    return stats
