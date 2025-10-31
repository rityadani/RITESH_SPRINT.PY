import streamlit as st
from dashboard_rl import rl_dashboard

# ----------------------------
# ✅ MAIN DASHBOARD NAVIGATION
# ----------------------------

st.set_page_config(
    page_title="AI Self-Healing System",
    layout="wide",
    page_icon="🤖"
)

# Sidebar
st.sidebar.title("📌 Navigation")

page = st.sidebar.selectbox(
    "Select Page",
    ["Home", "RL Learning"]  # You can add more pages later
)

# ----------------------------
# ✅ HOME PAGE
# ----------------------------
if page == "Home":
    st.title("🚀 AI Self-Healing System Dashboard")
    st.write("""
    Welcome to the AIOps Self-Healing System.

    This dashboard monitors:
    - ⚙️ System health
    - 🤖 Automatic Fix Attempts
    - 🧠 RL Agent Learning
    - 👨‍🏫 Human Feedback Loop
    """)

    st.markdown("---")
    st.subheader("✅ System Status: Running")
    st.success("AI self-healing pipeline active!")

    st.info("Use sidebar to open the **RL Learning** panel.")


# ----------------------------
# ✅ RL LEARNING PAGE
# ----------------------------
elif page == "RL Learning":
    rl_dashboard()
