import streamlit as st
from supabase import create_client
import time

st.set_page_config(page_title="KVP Chat", page_icon="💬", layout="centered")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

GLOBAL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.main {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}

[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a3e 0%, #16213e 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    transition: border 0.3s;
}

.stTextInput > div > div > input:focus {
    border: 1px solid #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.2) !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.3) !important;
}

div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #a78bfa, #7c3aed);
    color: white !important;
    border: none !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124,58,237,0.5);
}

div.stButton > button:active {
    transform: translateY(0);
}

[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 16px !important;
    padding: 0.5rem !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}

p, label, .stMarkdown {
    color: rgba(255,255,255,0.85) !important;
}

hr {
    border-color: rgba(255,255,255,0.08) !important;
}

.login-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    margin-top: 3rem;
    box-shadow: 0 25px 50px rgba(0,0,0,0.4);
}

.app-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}

.app-subtitle {
    text-align: center;
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.9rem;
    margin-bottom: 2.5rem;
}

.chat-header {
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 16px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-badge {
    background: linear-gradient(135deg, #a78bfa, #7c3aed);
    border-radius: 50%;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: white;
}

.empty-chat {
    text-align: center;
    padding: 4rem 2rem;
    color: rgba(255,255,255,0.3) !important;
}

.sidebar-user {
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
    text-align: center;
}

.online-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 6px #4ade80;
}
</style>
"""

def login():
    st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="app-title">💬 KVP Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">✨ Private & Encrypted Messaging</div>', unsafe_allow_html=True)

        email = st.text_input("", placeholder="📧  Enter your email", key="email_input")
        pwd = st.text_input("", placeholder="🔑  Enter your password", type="password", key="pwd_input")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("💬  Start Chatting →"):
            if not email or not pwd:
                st.warning("⚠️ Please enter both email and password.")
                return
            with st.spinner(""):
                time.sleep(0.5)
                try:
                    result = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
                    if result.data:
                        user = result.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome, {user['name']}! 🎉")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

def chat():
    st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)

    try:
        users_result = supabase.table("users").select("email, name").neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in users_result.data}
    except Exception:
        other_users = {}

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-user">
                <div style="font-size:2rem;">👤</div>
                <div style="font-weight:700; font-size:1.1rem; color:white;">{st.session_state.user_name}</div>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.4);">
                    <span class="online-dot"></span>Online
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("**💬 Conversations**")

        if not other_users:
            st.warning("No other users found.")
            selected_recipient = None
        else:
            selected_recipient = st.selectbox(
                "Chat with:",
                options=list(other_users.keys()),
                format_func=lambda x: f"👤  {other_users[x]}",
                label_visibility="collapsed"
            )

        st.markdown("<br>" * 3, unsafe_allow_html=True)
        if st.button("🚪  Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.rerun()

    # Main area
    if not selected_recipient:
        st.info("No other users to chat with.")
        return

    # Chat header
    initials = other_users[selected_recipient][0].upper()
    st.markdown(f"""
        <div class="chat-header">
            <div class="user-badge">{initials}</div>
            <div>
                <div style="font-weight:700; font-size:1.1rem; color:white;">
                    {other_users[selected_recipient]}
                </div>
                <div style="font-size:0.8rem; color:rgba(255,255,255,0.4);">
                    <span class="online-dot"></span>Active now
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Load messages
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

    # Display messages
    if not messages:
        st.markdown(f"""
            <div class="empty-chat">
                <div style="font-size:3.5rem;">👋</div>
                <div style="font-size:1.1rem; margin-top:1rem;">
                    Say hello to <b style="color:rgba(167,139,250,0.9)">
                    {other_users[selected_recipient]}</b>!
                </div>
                <div style="font-size:0.85rem; margin-top:0.5rem; opacity:0.6;">
                    Your messages are private & secure 🔒
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            role = "user" if msg["sender"] == st.session_state.user_email else "assistant"
            with st.chat_message(role):
                st.write(msg["message"])

    # Chat input
    if prompt := st.chat_input(f"Message {other_users[selected_recipient]}..."):
        try:
            supabase.table("messages").insert({
                "sender": st.session_state.user_email,
                "recipient": selected_recipient,
                "message": prompt
            }).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send: {e}")

    # Auto refresh every 3 seconds
    time.sleep(3)
    st.rerun()

if not st.session_state.logged_in:
    login()
else:
    chat()
