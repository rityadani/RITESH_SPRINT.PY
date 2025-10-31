import streamlit as st
import pandas as pd
import os


# ======================
# ✅ DATA LOADING FUNCTIONS
# ======================
def load_q_table():
    file = "data/rl_table.csv"
    return pd.read_csv(file) if os.path.exists(file) else pd.DataFrame(columns=["state","action","q_value"])

def load_feedback():
    file = "data/human_feedback.csv"
    return pd.read_csv(file) if os.path.exists(file) else pd.DataFrame(columns=["timestamp","state","action","feedback"])

def load_logs():
    file = "logs/planner_log.csv"
    return pd.read_csv(file) if os.path.exists(file) else pd.DataFrame(columns=["timestamp","state","action","result","reward"])


# ======================
# ✅ RL DASHBOARD PAGE
# ======================
def rl_dashboard():

    st.title("🤖 AI Self-Healing System — RL Insights Panel")

    q_table = load_q_table()
    feedback = load_feedback()
    logs = load_logs()


    # ======================
    # 📌 RL Q-TABLE VIEW
    # ======================
    st.subheader("📂 Reinforcement Learning Q-Table (Memory Bank)")
    st.dataframe(q_table, use_container_width=True)

    if not q_table.empty:
        avg_q = q_table["q_value"].mean()
        st.info(f"📊 **Avg Q-Value Learned:** {avg_q:.3f}")



    # ======================
    # 📈 RL REWARD TREND
    # ======================
    if not logs.empty:
        st.subheader("📈 RL Reward Trend (Learning Curve)")
        st.line_chart(logs["reward"], height=200)



    # ======================
    # 👨‍🏫 HUMAN FEEDBACK TREND
    # ======================
    if not feedback.empty:
        st.subheader("👨‍🏫 Human Feedback Trend")
        fb_counts = feedback["feedback"].value_counts()
        st.bar_chart(fb_counts, height=200)



    # ======================
    # 🧾 RECENT LOGS TABLE
    # ======================
    st.subheader("🧾 Recent Fix Attempts")
    st.dataframe(logs.tail(12), use_container_width=True)



    # ======================
    # ✅ SUCCESS METRICS
    # ======================
    st.subheader("📊 Performance Summary")

    if not logs.empty:
        auto_success = (logs["result"].sum() / len(logs)) * 100
        st.success(f"✅ **AI Auto-Fix Success Rate:** {auto_success:.2f}%")

    if not feedback.empty:
        human_score = feedback["feedback"].mean() * 100
        st.warning(f"🧠 **Human Feedback Score:** {human_score:.2f}%")



    st.markdown("---")
    st.caption("⚡ Live RL Agent Training Monitor — © AI-Ops Internship Project")
