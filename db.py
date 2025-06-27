import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, email TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS urls (user TEXT, url TEXT, interval TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, url TEXT, status INTEGER, timestamp TEXT)")
        conn.commit()

def add_url(user, url, interval):
    with get_conn() as conn:
        conn.execute("INSERT INTO urls (user, url, interval) VALUES (?, ?, ?)", (user, url, interval))
        conn.commit()

def delete_url(user, url):
    with get_conn() as conn:
        conn.execute("DELETE FROM urls WHERE user=? AND url=?", (user, url))
        conn.execute("DELETE FROM logs WHERE user=? AND url=?", (user, url))
        conn.commit()

def get_urls_by_user_with_intervals(user):
    with get_conn() as conn:
        rows = conn.execute("SELECT url, interval FROM urls WHERE user=?", (user,)).fetchall()
        return rows

def get_logs_by_user(user):
    with get_conn() as conn:
        rows = conn.execute("SELECT url, status, timestamp FROM logs WHERE user=?", (user,)).fetchall()
        return rows

def save_email_for_user(username, email):
    with get_conn() as conn:
        conn.execute("UPDATE users SET email=? WHERE username=?", (email, username))
        conn.commit()

def get_email_for_user(username):
    with get_conn() as conn:
        row = conn.execute("SELECT email FROM users WHERE username=?", (username,)).fetchone()
        return row[0] if row and row[0] else ""
