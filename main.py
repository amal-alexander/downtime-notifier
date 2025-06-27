import streamlit as st
from auth import check_login
from db import init_db, add_url, get_urls_by_user_with_intervals, get_logs_by_user, save_email_for_user, get_email_for_user, delete_url
import pandas as pd
from datetime import datetime, timedelta

CHECK_OPTIONS = {
    "Every 5 minutes": "5min",
    "Every 1 hour": "1h",
    "Every 24 hours": "24h"
}

st.set_page_config("🔔 Downtime Notifier", layout="centered")
init_db()

user = check_login()
if not user:
    st.stop()

st.sidebar.success(f"Logged in as: {user}")
st.title("🔔 Downtime Notifier Dashboard")

# 📧 Email setting
st.sidebar.subheader("📩 Notification Email")
current_email = get_email_for_user(user)
email_input = st.sidebar.text_input("Your Email", value=current_email or "")
if st.sidebar.button("Update Email"):
    save_email_for_user(user, email_input)
    st.sidebar.success("✅ Email saved")

# ➕ Add URL
st.subheader("➕ Monitor a New URL")
with st.form("add_url_form"):
    new_url = st.text_input("Enter URL")
    freq_label = st.selectbox("Check Frequency", list(CHECK_OPTIONS.keys()))
    submitted = st.form_submit_button("Add")
    if submitted and new_url:
        add_url(user, new_url.strip(), CHECK_OPTIONS[freq_label])
        st.success(f"✅ Monitoring {new_url} every {freq_label}")
        st.experimental_rerun()

# 📋 Show monitored URLs
st.subheader("🌐 Your Monitored URLs")
url_list = get_urls_by_user_with_intervals(user)
if not url_list:
    st.info("No URLs being monitored yet.")
else:
    for url, interval in url_list:
        col1, col2, col3 = st.columns([5, 2, 1])
        col1.markdown(f"**{url}**")
        col2.markdown(f"⏱️ {interval}")
        if col3.button("❌", key=url):
            delete_url(user, url)
            st.experimental_rerun()

    # Optionally show logs for one
    selected_url = st.selectbox("📜 View logs for a URL:", [u[0] for u in url_list])
    logs = get_logs_by_user(user)
    filtered = [log for log in logs if log[0] == selected_url]
    if filtered:
        df = pd.DataFrame(filtered, columns=["URL", "Status", "Timestamp"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df["Readable"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df["Emoji"] = df["Status"].apply(lambda s: "✅" if s else "❌")

        st.markdown("### 📈 Log History")
        for _, row in df.sort_values(by="Timestamp", ascending=False).iterrows():
            color = "green" if row["Status"] else "red"
            st.markdown(
                f"- <span style='color:{color}'>{row['Emoji']}</span> `{row['Readable']}` — {row['URL']}",
                unsafe_allow_html=True
            )
    else:
        st.info("No logs available yet for this URL.")
