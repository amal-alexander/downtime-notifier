import streamlit as st
from auth import check_login
from db import (
    init_db, add_url, get_urls_by_user, get_logs_by_user,
    save_email_for_user, get_email_for_user
)
from scheduler import start_scheduler
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

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
st.subheader("Add a URL to Monitor")
urls = get_urls_by_user(user)
if len(urls) >= MAX_URLS:
    st.warning(f"🚫 Limit reached: You can only monitor {MAX_URLS} URLs.")
else:
    new_url = st.text_input("Enter a new URL (e.g., https://example.com)")
    if st.button("Add URL"):
        if new_url:
            add_url(user, new_url)
            st.success(f"✅ Added {new_url}")
            st.rerun()

# 🔗 Existing URLs
st.subheader("Your Monitored URLs")
urls = get_urls_by_user(user)

if not urls:
    st.info("No URLs added yet.")
    st.stop()

selected_url = st.selectbox("Choose a URL to view its logs:", urls)

# 📊 Overview Box
st.subheader("📊 Monitoring Overview")
all_logs = get_logs_by_user(user)
total_urls = len(urls)
total_logs = len(all_logs)
total_downs = sum(1 for log in all_logs if log[1] == 0)

# Calculate uptime % for last 24 hrs
now = datetime.now()
last_24h_logs = [log for log in all_logs if pd.to_datetime(log[2]) >= now - timedelta(hours=24)]
if last_24h_logs:
    ups = sum(1 for log in last_24h_logs if log[1] == 1)
    uptime_percent = round(100 * ups / len(last_24h_logs), 2)
    uptime_pie = {"Up": ups, "Down": len(last_24h_logs) - ups}
else:
    uptime_percent = 100.0
    uptime_pie = {"Up": 1, "Down": 0}

# Find latest downtime
downtime_logs = [log for log in all_logs if log[1] == 0]
last_downtime = max(downtime_logs, key=lambda x: x[2])[2] if downtime_logs else "N/A"
last_downtime_url = max(downtime_logs, key=lambda x: x[2])[0] if downtime_logs else "N/A"

# Display Metrics
st.markdown(f"""
- **Total Monitored URLs:** `{total_urls}`
- **Total Downtime Events:** `{total_downs}`
- **Uptime (Last 24h):** `{uptime_percent}%`
- **Last Downtime:** `{last_downtime}` ({last_downtime_url})
""")

# Uptime Pie Chart
fig = px.pie(
    names=list(uptime_pie.keys()),
    values=list(uptime_pie.values()),
    title="Uptime vs Downtime (Last 24 Hours)",
    color_discrete_sequence=["green", "red"]
)
st.plotly_chart(fig, use_container_width=True)

# ⏱️ Time Filter
time_filter = st.selectbox("Select time range to view logs:", [
    "Last 5 minutes", "Last 1 hour", "Last 24 hours", "All"
])

# 📊 Logs
logs = get_logs_by_user(user)
filtered_logs = [log for log in logs if log[0] == selected_url]

if filtered_logs:
    df = pd.DataFrame(filtered_logs, columns=["URL", "Status", "Timestamp"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Readable"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Emoji"] = df["Status"].apply(lambda s: "✅" if s else "❌")

    # Apply time filter
    now = datetime.now()
    if time_filter == "Last 5 minutes":
        df = df[df["Timestamp"] >= now - timedelta(minutes=5)]
    elif time_filter == "Last 1 hour":
        df = df[df["Timestamp"] >= now - timedelta(hours=1)]
    elif time_filter == "Last 24 hours":
        df = df[df["Timestamp"] >= now - timedelta(hours=24)]

    # 📈 Show Logs
    st.subheader(f"📈 Log History for: {selected_url}")
    for _, row in df.sort_values(by="Timestamp", ascending=False).iterrows():
        color = "green" if row["Status"] else "red"
        st.markdown(
            f"- <span style='color:{color}'>{row['Emoji']}</span> `{row['Readable']}` — {row['URL']}",
            unsafe_allow_html=True
        )

    # 📥 Download CSV
    csv = df[["URL", "Status", "Timestamp"]].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Logs as CSV", data=csv, file_name=f"{selected_url.replace('/', '_')}_uptime.csv")

    # 📉 Downtime Chart
    df["Downtime"] = (~df["Status"].astype(bool)).astype(int)
    df["Timestamp"] = df["Timestamp"].dt.floor("min")
    st.subheader("📉 Downtime Trend (1 = Down, 0 = Up)")
    st.line_chart(df.set_index("Timestamp")[["Downtime"]])
else:
    st.info("No logs available yet for this URL.")
