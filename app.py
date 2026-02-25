import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Private Secure Chat", page_icon="🔒")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

def login():
    st.title("🔒 Private Secure Chat")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            result = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
            if result.data:
                user = result.data[0]
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = user["name"]
                st.rerun()
            else:
                st.error("Invalid Email or Password.")
        except Exception as e:
            st.error(f"Error: {e}")

def chat():
    try:
        users_result = supabase.table("users").select("email, name").neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in users_result.data}
    except Exception:
        other_users = {}

    st.sidebar.title("💬 Chat")
    st.sidebar.write(f"Logged in as: **{st.session_state.user_name}**")

    if not other_users:
        st.sidebar.warning("No other users found.")
        selected_recipient = None
    else:
        selected_recipient = st.sidebar.selectbox(
            "Chat with:",
            options=list(other_users.keys()),
            format_func=lambda x: other_users[x]
        )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

    st.title(f"Welcome, {st.session_state.user_name}! 👋")

    if not selected_recipient:
        st.info("No other users to chat with.")
        return

    st.subheader(f"Conversation with {other_users[selected_recipient]}")

    # Fixed: fetch sent and received separately instead of using .or_()
    try:
        sent = supabase.table("messages").select("*") \
            .eq("sender", st.session_state.user_email) \
            .eq("recipient", selected_recipient) \
            .execute()

        received = supabase.table("messages").select("*") \
            .eq("sender", selected_recipient) \
            .eq("recipient", st.session_state.user_email) \
            .execute()

        messages = sorted(
            sent.data + received.data,
            key=lambda x: x["created_at"]
        )
    except Exception as e:
        st.error(f"Error loading messages: {e}")
        messages = []

    if not messages:
        st.info("No messages yet. Say hello! 👋")
    else:
        for msg in messages:
            role = "user" if msg["sender"] == st.session_state.user_email else "assistant"
            with st.chat_message(role):
                st.write(msg["message"])
                st.caption(f"{msg['sender']} • {msg['created_at'][:16]}")

    if prompt := st.chat_input(f"Message {other_users[selected_recipient]}..."):
        try:
            supabase.table("messages").insert({
                "sender": st.session_state.user_email,
                "recipient": selected_recipient,
                "message": prompt
            }).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send message: {e}")

if not st.session_state.logged_in:
    login()
else:
    chat()
