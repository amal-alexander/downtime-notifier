from apscheduler.schedulers.background import BackgroundScheduler
from db import get_urls_by_user, log_uptime, get_all_users
from monitor import check_url_status
import time

scheduler = BackgroundScheduler()

def check_all():
    users = get_all_users()
    for user in users:
        urls = get_urls_by_user(user)
        for url in urls:
            status = check_url_status(url)
            log_uptime(user, url, status)

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(check_all, 'interval', minutes=5)
        scheduler.start()
