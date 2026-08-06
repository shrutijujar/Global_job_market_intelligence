import streamlit as st
import psycopg2

st.title("🔐 Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login"):

    conn = psycopg2.connect(
        host="localhost",
        database="job_market_db",
        user="postgres",
        password="shruti65"
    )

    cur = conn.cursor()

    cur.execute(
        """
        SELECT id,name,email,is_banned
        FROM applicants
        WHERE email=%s
        AND password=%s
        """,
        (
            email,
            password
        )
    )

    user = cur.fetchone()

    if user:

        user_id = user[0]
        user_name = user[1]
        user_email = user[2]
        is_banned = user[3]

        # Check if user is banned
        if is_banned:

            # Log failed login (banned)
            cur.execute("""
                INSERT INTO login_history
                (applicant_id, status)
                VALUES (%s, %s)
            """, (user_id, "banned"))

            conn.commit()

            cur.close()
            conn.close()

            st.error(
                "Your account has been suspended. "
                "Please contact the administrator "
                "at shrutijujar321@gmail.com"
            )

        else:

            # Log successful login
            cur.execute("""
                INSERT INTO login_history
                (applicant_id, status)
                VALUES (%s, %s)
            """, (user_id, "success"))

            conn.commit()

            cur.close()
            conn.close()

            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["name"] = user_name
            st.session_state["email"] = user_email

            st.success(
                f"Welcome {user_name}"
            )

    else:

        cur.close()
        conn.close()

        st.error(
            "Invalid Email or Password"
        )