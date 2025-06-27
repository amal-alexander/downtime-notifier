import streamlit as st
from db import add_user, check_user_login

def check_login():
    st.sidebar.subheader("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if check_user_login(username, password):
            st.session_state["user"] = username
            return username
        else:
            st.sidebar.error("Invalid credentials")
    if st.sidebar.button("Sign Up"):
        if username and password:
            add_user(username, password)
            st.sidebar.success("User created! Please log in.")
    return st.session_state.get("user", None)
