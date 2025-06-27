import streamlit as st
from db import add_user, check_user_login

def check_login():
    st.sidebar.subheader("🔐 Login")

    if "user" not in st.session_state:
        st.session_state.user = None

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    col1, col2 = st.sidebar.columns(2)

    if col1.button("Login"):
        if check_user_login(username, password):
            st.session_state.user = username
            st.sidebar.success(f"✅ Logged in as {username}")
        else:
            st.sidebar.error("❌ Invalid username or password")

    if col2.button("Sign Up"):
        if username and password:
            add_user(username, password)
            st.sidebar.success("✅ Account created! Please log in.")
        else:
            st.sidebar.warning("⚠️ Enter both username and password")

    return st.session_state.user
