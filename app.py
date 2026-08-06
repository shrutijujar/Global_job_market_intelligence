import streamlit as st

st.set_page_config(
    page_title="Europe Job Market Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AI-Powered Europe Job Market Intelligence Platform")

st.info(
    "Use the sidebar on the left to navigate between dashboards."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries", "10+")

with col2:
    st.metric("Modules", "5")

with col3:
    st.metric("AI Features", "Coming Soon")

st.markdown("---")

st.subheader("Platform Roadmap")

st.progress(40)

st.write("✅ Executive Dashboard")
st.write("✅ Salary Intelligence")
st.write("🔄 Skill Intelligence")
st.write("🔄 Visa Analytics")
st.write("🔄 AI Career Advisor")