import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(
    page_title="Application Tracker",
    layout="wide"
)

st.title("📌 Application Tracker")

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

query = """
SELECT *
FROM applications
WHERE applicant_id=%s
ORDER BY applied_at DESC
"""

applications = pd.read_sql(
    query,
    conn,
    params=(
        st.session_state["user_id"],
    )
)

st.metric(
    "Applications",
    len(applications)
)

st.divider()

if applications.empty:

    st.info(
        "No applications found."
    )

else:

    for _, app in applications.iterrows():

        st.subheader(
            app["job_title"]
        )

        st.write(
            f"🏢 {app['company']}"
        )

        st.write(
            f"🌍 {app['country']}"
        )

        st.write(
            f"📊 Status: {app['status']}"
        )

        if pd.notna(app["job_url"]):

            st.link_button(
                "🚀 Open Job",
                app["job_url"]
            )

        new_status = st.selectbox(
            "Update Status",
            [
                "Applied",
                "Interview Scheduled",
                "Interview Completed",
                "Offer Received",
                "Rejected"
            ],
            key=f"status_{app['id']}"
        )

        if st.button(
            "Update",
            key=f"update_{app['id']}"
        ):

            cur = conn.cursor()

            cur.execute(
                """
                UPDATE applications
                SET status=%s
                WHERE id=%s
                """,
                (
                    new_status,
                    app["id"]
                )
            )

            conn.commit()

            cur.close()

            st.success(
                "Status Updated"
            )

            st.rerun()

        st.divider()

conn.close()