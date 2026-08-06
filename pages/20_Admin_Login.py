import streamlit as st
import psycopg2

st.set_page_config(
    page_title="Admin Login",
    page_icon="🔐",
    layout="wide"
)

# =========================
# CUSTOM STYLING
# =========================

st.markdown("""
<style>
    .admin-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .admin-header h1 {
        color: #FF4B4B;
        font-size: 2.5rem;
    }
    .admin-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(255, 75, 75, 0.2);
        margin: 1rem 0;
    }
    .admin-badge {
        background: linear-gradient(135deg, #FF4B4B, #FF6B6B);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF6B6B, #FF8B8B);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CHECK IF ALREADY LOGGED IN
# =========================

if st.session_state.get("admin_logged_in"):

    st.title("🔐 Admin Panel")

    st.success(
        f"Logged in as: {st.session_state['admin_username']}"
    )

    st.info(
        "Navigate to **Admin Dashboard** or **Admin Job Review** "
        "from the sidebar."
    )

    if st.button("🚪 Logout"):

        st.session_state["admin_logged_in"] = False
        st.session_state["admin_username"] = None

        st.success("Logged out successfully.")
        st.rerun()

    st.stop()

# =========================
# LOGIN FORM
# =========================

st.markdown(
    '<div class="admin-header">'
    '<h1>🔐 Admin Login</h1>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="admin-badge">'
    'ADMINISTRATOR ACCESS'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    st.markdown("#### Enter Admin Credentials")

    username_or_email = st.text_input(
        "Username or Email",
        placeholder="Enter admin username or email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter admin password"
    )

    if st.button("🔓 Login as Admin"):

        if not username_or_email or not password:

            st.error("Please enter both fields.")

        else:

            conn = psycopg2.connect(
                host="localhost",
                database="job_market_db",
                user="postgres",
                password="shruti65"
            )

            cur = conn.cursor()

            cur.execute("""
                SELECT id, username, email
                FROM admin_users
                WHERE (username = %s OR email = %s)
                AND password = %s
            """, (username_or_email, username_or_email, password))

            admin = cur.fetchone()

            cur.close()
            conn.close()

            if admin:

                st.session_state["admin_logged_in"] = True
                st.session_state["admin_username"] = admin[1]
                st.session_state["admin_email"] = admin[2]

                st.success(
                    f"Welcome, {admin[2] or admin[1]}! Redirecting..."
                )

                st.rerun()

            else:

                st.error(
                    "Invalid admin credentials."
                )

    st.markdown("---")

    st.caption(
        "This area is restricted to authorized "
        "administrators only."
    )
