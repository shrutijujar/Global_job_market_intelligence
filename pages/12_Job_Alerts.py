import streamlit as st
import psycopg2

st.title("🔔 Job Alerts")

email = st.text_input("Your Email")

country = st.selectbox(
    "Country",
    [
        "United Kingdom",
        "Netherlands",
        "Germany",
        "France",
        "Belgium"
    ]
)

job_role = st.text_input(
    "Preferred Job Role"
)

if st.button("Save Alert"):

    conn = psycopg2.connect(
        host="localhost",
        database="job_market_db",
        user="postgres",
        password="shruti65"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM applicants
        WHERE email=%s
    """, (email,))

    applicant = cur.fetchone()

    if applicant:

        cur.execute("""
            INSERT INTO applicant_preferences
            (
                applicant_id,
                country,
                job_role
            )
            VALUES (%s,%s,%s)
        """,
        (
            applicant[0],
            country,
            job_role
        ))

        conn.commit()

        st.success(
            "Alert Preference Saved"
        )

    else:
        st.error(
            "Applicant not found"
        )

    cur.close()
    conn.close()