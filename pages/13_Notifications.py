import streamlit as st
import pandas as pd
import psycopg2

st.title("🔔 Notifications")

conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)

notifications = pd.read_sql("""
SELECT *
FROM notifications
ORDER BY created_at DESC
""", conn)

st.dataframe(
    notifications,
    use_container_width=True
)

conn.close()