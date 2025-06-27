import streamlit as st
from db import (
    init_db, add_url, get_urls_by_user_with_intervals, delete_url,
    get_logs_by_user, save_email_for_user, get_email_for_user
)
from scheduler import start_scheduler
from datetime import datetime, timedelta
import pandas as pd

# Initialize DB and Scheduler
st.set_page_config("🔔 Downtime Notifier", layout="centered")
init_db()
start_scheduler()

# Dummy login for demo (replace with real auth)
user = "admin"  # Replace with actual login if needed

st.title("🌐 Downtime Notifier Dashboard")
st.sidebar.success(f"Logged in as: {user}")

# Email section
st.sidebar.subheader("📩 Email for Alerts")
current_email = get_email_for_user(user)
email_input = st.sidebar.text_input("Enter email", value=current_email or "")
if st.sidebar.button("Update Email"):
    save_email_for_user(user, email_input)
    st.sidebar.success("✅ Email updated")

# Add URL
st.subheader("➕ Add URL to Monitor")
url_input = st.text_input("URL (e.g., https://example.com)")
interval_input = st.selectbox("Check every...", ["5min", "1hr", "24hr"])
if st.button("Add"):
    if url_input:
        add_url(user, url_input, interval_input)
        st.success("✅ URL Added")
        st.rerun()

# Display Monitored URLs
st.subheader("🔗 Your URLs")
url_rows = get_urls_by_user_with_intervals(user)

if not url_rows:
    st.info("No URLs added yet.")
else:
    for url, interval in url_rows:
        st.markdown(f"**{url}** — every **{interval}**")
        if st.button(f"❌ Remove {url}"):
            delete_url(user, url)
            st.rerun()

# Select and View Logs
st.subheader("📊 View Logs")
urls = [row[0] for row in url_rows]
if urls:
    selected_url = st.selectbox("Select URL:", urls)
    time_range = st.selectbox("Time Filter:", ["Last 5 minutes", "Last 1 hour", "Last 24 hours", "All"])

    logs = get_logs_by_user(user)
    filtered = [log for log in logs if log[0] == selected_url]

    if filtered:
        df = pd.DataFrame(filtered, columns=["URL", "Status", "Timestamp"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        now = datetime.now()

        if time_range == "Last 5 minutes":
            df = df[df["Timestamp"] >= now - timedelta(minutes=5)]
        elif time_range == "Last 1 hour":
            df = df[df["Timestamp"] >= now - timedelta(hours=1)]
        elif time_range == "Last 24 hours":
            df = df[df["Timestamp"] >= now - timedelta(hours=24)]

        df["Readable"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df["Emoji"] = df["Status"].apply(lambda s: "✅" if s else "❌")
        for _, row in df.iterrows():
            color = "green" if row["Status"] else "red"
            st.markdown(f"- <span style='color:{color}'>{row['Emoji']}</span> `{row['Readable']}`", unsafe_allow_html=True)
    else:
        st.info("No logs found for this URL.")
