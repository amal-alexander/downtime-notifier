import streamlit as st
from auth import check_login
from db import (
    init_db, add_url, update_url_interval,
    get_urls_by_user_with_intervals, get_logs_by_user,
    save_email_for_user, get_email_for_user
)
from scheduler import start_scheduler
import pandas as pd
from datetime import datetime, timedelta

INTERVAL_OPTIONS = ["5min", "1hr", "24hr"]
MAX_URLS = 20

st.set_page_config("🔔 Downtime Notifier Dashboard", layout="centered")
init_db()
start_scheduler()

# 🔐 Login
user = check_login()
if not user:
    st.stop()

st.sidebar.success(f"Logged in as: {user}")
st.title("🌐 Downtime Notifier Dashboard")

# 📧 Email Alerts
st.sidebar.subheader("📩 Email Notifications")
current_email = get_email_for_user(user)
new_email = st.sidebar.text_input("Enter your email", value=current_email or "")
if st.sidebar.button("Update Email"):
    if new_email:
        save_email_for_user(user, new_email)
        st.sidebar.success("✅ Email updated!")

# ➕ Add URL
st.subheader("Add New URL to Monitor")
user_urls = get_urls_by_user_with_intervals(user)
if len(user_urls) >= MAX_URLS:
    st.warning(f"🚫 You can monitor up to {MAX_URLS} URLs.")
else:
    with st.form("add_url_form"):
        new_url = st.text_input("URL (e.g., https://example.com)")
        interval = st.selectbox("Check interval", INTERVAL_OPTIONS)
        submitted = st.form_submit_button("Add URL")
        if submitted and new_url:
            add_url(user, new_url, interval)
            st.success(f"✅ Monitoring {new_url} every {interval}")
            st.rerun()

# 🔗 Monitored URLs
st.subheader("📋 Your Monitored URLs")
user_urls = get_urls_by_user_with_intervals(user)
if not user_urls:
    st.info("No URLs added yet.")
    st.stop()

selected_url = st.selectbox("View logs for URL:", [u for u, _ in user_urls])
current_interval = next((i for u, i in user_urls if u == selected_url), "5min")
new_interval = st.selectbox("Update interval for this URL:", INTERVAL_OPTIONS, index=INTERVAL_OPTIONS.index(current_interval))
if st.button("Update Interval"):
    update_url_interval(user, selected_url, new_interval)
    st.success("✅ Interval updated.")
    st.rerun()

# ⏱️ Log Time Filter
time_filter = st.selectbox("Show logs from:", ["Last 5 minutes", "Last 1 hour", "Last 24 hours", "All"])

# 📊 Logs
logs = get_logs_by_user(user)
filtered_logs = [log for log in logs if log[0] == selected_url]

if filtered_logs:
    df = pd.DataFrame(filtered_logs, columns=["URL", "Status", "Timestamp"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Readable"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Emoji"] = df["Status"].apply(lambda s: "✅" if s else "❌")

    # ⏳ Apply Time Filter
    now = datetime.now()
    if time_filter == "Last 5 minutes":
        df = df[df["Timestamp"] >= now - timedelta(minutes=5)]
    elif time_filter == "Last 1 hour":
        df = df[df["Timestamp"] >= now - timedelta(hours=1)]
    elif time_filter == "Last 24 hours":
        df = df[df["Timestamp"] >= now - timedelta(hours=24)]

    st.subheader(f"📈 Status History for: {selected_url}")
    for _, row in df.sort_values(by="Timestamp", ascending=False).iterrows():
        st.markdown(
            f"- <span style='color:{'green' if row['Status'] else 'red'}'>{row['Emoji']}</span> `{row['Readable']}` — {row['URL']}",
            unsafe_allow_html=True
        )

    # 📉 Downtime Chart
    df["Downtime"] = (~df["Status"].astype(bool)).astype(int)
    df["Timestamp"] = df["Timestamp"].dt.floor("min")
    st.subheader("📉 Downtime Trend (1 = Down, 0 = Up)")
    st.line_chart(df.set_index("Timestamp")[["Downtime"]])

    # 📥 Download CSV
    csv = df[["URL", "Status", "Timestamp"]].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Logs as CSV", data=csv, file_name=f"{selected_url.replace('/', '_')}_uptime.csv")

else:
    st.info("No logs yet for this URL.")
