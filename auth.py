import streamlit as st
from db import add_user, check_user_login

def check_login():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return st.session_state.username

    st.sidebar.title("🔐 Login / Sign Up")
    login_tab, signup_tab = st.sidebar.tabs(["Login", "Sign Up"])

    with login_tab:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if check_user_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                return username
            else:
                st.error("❌ Invalid credentials")

    with signup_tab:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if new_user and new_pass:
                add_user(new_user, new_pass)
                st.success("✅ Account created. Now log in.")
            else:
                st.warning("Please enter both fields.")
    return None