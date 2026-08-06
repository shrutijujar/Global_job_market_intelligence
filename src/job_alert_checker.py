import psycopg2
import pandas as pd
from send_email import send_job_alert

conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)

# Load jobs
jobs = pd.read_sql(
    "SELECT * FROM jobs",
    conn
)

# Load preferences
prefs = pd.read_sql("""
SELECT
    a.id as applicant_id,
    a.email,
    p.country,
    p.job_role
FROM applicants a
JOIN applicant_preferences p
ON a.id = p.applicant_id
""", conn)

for _, pref in prefs.iterrows():

    matches = jobs[
        jobs["country"].str.contains(
            pref["country"],
            case=False,
            na=False
        )
        &
        jobs["title"].str.contains(
            pref["job_role"],
            case=False,
            na=False
        )
    ]

    print(
        f"Found {len(matches)} jobs for "
        f"{pref['email']}"
    )

    for _, job in matches.iterrows():

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM sent_alerts
        WHERE applicant_id=%s
        AND job_title=%s
        """,
        (
            pref["applicant_id"],
            job["title"]
        ))

        already_sent = cur.fetchone()

        if already_sent:
            continue

        print("STEP 1")

send_job_alert(
    pref["email"],
    job["title"],
    job["company"],
    job["country"],
    job["redirect_url"]
)

print("STEP 2")
cur.execute("""
INSERT INTO notifications
(
    applicant_id,
    title,
    company,
    country,
    job_url
)
VALUES (%s,%s,%s,%s,%s)
""",
(
    pref["applicant_id"],
    job["title"],
    job["company"],
    job["country"],
    job["redirect_url"]
))

conn.commit()

cur.execute("""
        INSERT INTO sent_alerts
        (
            applicant_id,
            job_title
        )
        VALUES (%s,%s)
        """,
        (
            pref["applicant_id"],
            job["title"]
        ))

conn.commit()

print(
            f"Email sent: {job['title']}"
        )

cur.close()

conn.close()