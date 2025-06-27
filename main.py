import streamlit as st
from auth import check_login
from db import init_db, add_url, get_urls_by_user, get_logs_by_user, save_email_for_user, get_email_for_user
from scheduler import start_scheduler
import pandas as pd
from datetime import datetime, timedelta

MAX_URLS = 20

st.set_page_config("🔔 Downtime Notifier Dashboard", layout="centered")
init_db()
start_scheduler()

# 🔐 Authentication
user = check_login()
if not user:
    st.stop()

st.sidebar.success(f"Logged in as: {user}")
st.title("🌐 Downtime Notifier Dashboard")

# 📩 Email Notifications
st.sidebar.subheader("📧 Email Alerts")
current_email = get_email_for_user(user)
new_email = st.sidebar.text_input("Enter your email to receive alerts", value=current_email or "")
if st.sidebar.button("Update Email"):
    if new_email:
        save_email_for_user(user, new_email)
        st.sidebar.success("✅ Email updated!")

# 🌐 Add New URL
st.subheader("Add a New URL to Monitor")
urls = get_urls_by_user(user)
if len(urls) >= MAX_URLS:
    st.warning(f"🚫 You’ve reached the limit of {MAX_URLS} URLs.")
else:
    new_url = st.text_input("Enter a URL (e.g., https://example.com)")
    if st.button("Add URL"):
        if new_url:
            add_url(user, new_url)
            st.success(f"✅ {new_url} added for monitoring")

# 🔗 Select from Existing URLs
st.subheader("Your Monitored URLs")
urls = get_urls_by_user(user)

if not urls:
    st.info("No URLs added yet.")
    st.stop()

selected_url = st.selectbox("Select a URL to view logs:", urls)

# 📊 Logs and Chart
st.subheader(f"📈 Uptime History for {selected_url}")
logs = get_logs_by_user(user)
filtered_logs = [log for log in logs if log[0] == selected_url]

if filtered_logs:
    df = pd.DataFrame(filtered_logs, columns=["URL", "Status", "Timestamp"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Readable"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Emoji"] = df["Status"].apply(lambda s: "✅" if s else "❌")

    # ⏱️ Time Filter
    time_filter = st.selectbox("Filter logs by time range:", ["All", "Last 10 minutes", "Last 1 hour", "Last 24 hours"])
    if time_filter == "Last 10 minutes":
        df = df[df["Timestamp"] >= (datetime.now() - timedelta(minutes=10))]
    elif time_filter == "Last 1 hour":
        df = df[df["Timestamp"] >= (datetime.now() - timedelta(hours=1))]
    elif time_filter == "Last 24 hours":
        df = df[df["Timestamp"] >= (datetime.now() - timedelta(hours=24))]

    # Display Logs
    for _, row in df.sort_values(by="Timestamp", ascending=False).iterrows():
        color = "green" if row["Status"] else "red"
        st.markdown(
            f"- <span style='color:{color}'>{row['Emoji']}</span> `{row['Readable']}` — {row['URL']}",
            unsafe_allow_html=True
        )

    # 📥 CSV Export
    csv = df[["URL", "Status", "Timestamp"]].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name=f"{selected_url.replace('https://', '').replace('/', '_')}_uptime.csv", mime="text/csv")

    # 📉 Downtime Chart
    df["Downtime"] = (~df["Status"].astype(bool)).astype(int)
    df["Timestamp"] = df["Timestamp"].dt.floor("min")
    st.subheader("📉 Downtime Trend (1 = Down, 0 = Up)")
    st.line_chart(df.set_index("Timestamp")[["Downtime"]])
else:
    st.info("No logs available for this URL yet.")
