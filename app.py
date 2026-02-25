import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Private Secure Chat", page_icon="🔒")

# Create connection to Google Sheets
# You will add your Sheet URL in the Streamlit Dashboard "Secrets" later
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

def login():
    # DIRECT CSV READ (Bypasses many 302 redirect issues)
    sheet_id = "1XMJASMYZ9ACVc4G5QZEie7W5Zu0KNpXlQNOVXIbPkcg"
    # We target the 'Users' tab specifically by name
    users_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Users"
    
    try:
        users_df = pd.read_csv(users_url)
    except Exception as e:
        st.error("Connection Error: Make sure your Google Sheet is set to 'Anyone with the link' can View.")
        return

    st.title("Login to Private Chat")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Make sure column names match your sheet exactly (email, password)
        user_match = users_df[(users_df['email'] == email) & (users_df['password'].astype(str) == str(pwd))]
        
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.user_name = user_match.iloc[0]['name']
            st.rerun()
        else:
            st.error("Invalid Email or Password. Check your Google Sheet!")

# --- CHAT INTERFACE ---
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user_name}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"Welcome, {st.session_state.user_name}! 👋")

    # 1. Read existing chat history from Sheet
    chat_df = conn.read(worksheet="ChatHistory")

    # 2. Display existing messages
    for idx, row in chat_df.iterrows():
        with st.chat_message("user" if row['sender'] == st.session_state.user_email else "assistant"):
            st.write(f"**{row['sender']}**: {row['message']}")

    # 3. Chat Input
    if prompt := st.chat_input("Write a message..."):
        # Append to the Google Sheet
        new_row = pd.DataFrame([{
            "sender": st.session_state.user_email,
            "message": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        # Update the sheet
        updated_df = pd.concat([chat_df, new_row], ignore_index=True)
        conn.update(worksheet="ChatHistory", data=updated_df)
        
        st.rerun() # Refresh to show new message
