import streamlit as st
import psycopg2

st.title("👤 Applicant Registration")

name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input(
    "Password",
    type="password"
)

country = st.text_input(
    "Preferred Country"
)

role = st.text_input(
    "Preferred Job Role"
)

if st.button("Register"):

    conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)
        

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO applicants
        (
            name,
            email,
            password,
            preferred_country,
            preferred_role
        )
        VALUES (%s,%s,%s,%s,%s)
        """,
        (
            name,
            email,
            password,
            country,
            role
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    st.success(
        "Registration Successful!"
    )