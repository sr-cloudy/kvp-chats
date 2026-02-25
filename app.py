import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SETUP: This is your password/security
SECRET_PASSWORD = "kvp@1842Chats" 

st.title("🔒 My Private Chat")

# Simple Login
password = st.sidebar.text_input("Enter Password", type="password")

if password == SECRET_PASSWORD:
    st.success("Welcome, Admin!")
    
    # Initialize chat history in a simple way
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input with Emoji support
    if prompt := st.chat_input("Type your message (emojis welcome! 😊)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
else:
    st.warning("Please enter the correct password to chat.")
