import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        # Create base tables
        c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS urls (user TEXT, url TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, url TEXT, status INTEGER, timestamp TEXT)")

        # Add missing 'email' column to users
        try:
            c.execute("ALTER TABLE users ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass  # Already exists

        # Add missing 'interval' column to urls
        try:
            c.execute("ALTER TABLE urls ADD COLUMN interval TEXT DEFAULT '5min'")
        except sqlite3.OperationalError:
            pass  # Already exists

        conn.commit()

# ✅ User Management
def add_user(username, password):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

def check_user_login(username, password):
    with get_conn() as conn:
        result = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        return result is not None

def save_email_for_user(username, email):
    with get_conn() as conn:
        conn.execute("UPDATE users SET email=? WHERE username=?", (email, username))
        conn.commit()

def get_email_for_user(username):
    with get_conn() as conn:
        row = conn.execute("SELECT email FROM users WHERE username=?", (username,)).fetchone()
        return row[0] if row and row[0] else ""

def get_all_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT username FROM users").fetchall()
        return [r[0] for r in rows]

# ✅ URL Management
def add_url(user, url, interval="5min"):
    with get_conn() as conn:
        conn.execute("INSERT INTO urls (user, url, interval) VALUES (?, ?, ?)", (user, url, interval))
        conn.commit()

def update_url_interval(user, url, new_interval):
    with get_conn() as conn:
        conn.execute("UPDATE urls SET interval=? WHERE user=? AND url=?", (new_interval, user, url))
        conn.commit()

def get_urls_by_user_with_intervals(user):
    with get_conn() as conn:
        rows = conn.execute("SELECT url, interval FROM urls WHERE user=?", (user,)).fetchall()
        return rows

def get_urls_by_user(user):
    with get_conn() as conn:
        rows = conn.execute("SELECT url FROM urls WHERE user=?", (user,)).fetchall()
        return [r[0] for r in rows]

# ✅ Uptime Logs
def log_uptime(user, url, status):
    with get_conn() as conn:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO logs (user, url, status, timestamp) VALUES (?, ?, ?, ?)",
                     (user, url, int(status), ts))
        conn.commit()

def get_logs_by_user(user):
    with get_conn() as conn:
        rows = conn.execute("SELECT url, status, timestamp FROM logs WHERE user=?", (user,)).fetchall()
        return rows
