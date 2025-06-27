from apscheduler.schedulers.background import BackgroundScheduler
import requests
from db import get_all_users, get_urls_by_user_with_intervals, log_uptime
import time

scheduler = BackgroundScheduler()

# Ping logic
def check_urls(user, urls):
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            is_up = response.status_code == 200
        except Exception:
            is_up = False
        log_uptime(user, url, is_up)

# This groups URLs by their interval
def schedule_jobs():
    interval_map = {
        "5min": [],
        "1hr": [],
        "24hr": []
    }

    for user in get_all_users():
        urls_with_intervals = get_urls_by_user_with_intervals(user)
        for url, interval in urls_with_intervals:
            if interval in interval_map:
                interval_map[interval].append((user, url))

    # Helper: flatten and group by user
    def group_by_user(pairs):
        grouped = {}
        for user, url in pairs:
            grouped.setdefault(user, []).append(url)
        return grouped

    # Schedule for each group
    for interval, pairs in interval_map.items():
        grouped = group_by_user(pairs)

        for user, url_list in grouped.items():
            job_id = f"{user}_{interval}"

            # Avoid duplicates if Streamlit reruns
            if scheduler.get_job(job_id):
                continue

            if interval == "5min":
                scheduler.add_job(check_urls, 'interval', minutes=5, args=[user, url_list], id=job_id)
            elif interval == "1hr":
                scheduler.add_job(check_urls, 'interval', hours=1, args=[user, url_list], id=job_id)
            elif interval == "24hr":
                scheduler.add_job(check_urls, 'interval', hours=24, args=[user, url_list], id=job_id)

def start_scheduler():
    if not scheduler.running:
        schedule_jobs()
        scheduler.start()
