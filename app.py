import streamlit as st
from supabase import create_client
import time

st.set_page_config(page_title="KVP Chat", page_icon="💬", layout="wide")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ─── RESET & BASE ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0d0d0d !important;
    font-family: 'DM Sans', sans-serif;
    color: #f0f0f0 !important;
}

[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }

/* ─── HIDE STREAMLIT DECORATION ─── */
[data-testid="stDecoration"] { display: none; }

/* ─── SIDEBAR ─── */
section[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #222 !important;
    width: 280px !important;
}

section[data-testid="stSidebar"] * {
    color: #f0f0f0 !important;
}

section[data-testid="stSidebar"] .stSelectbox label {
    color: #888 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
}

/* Selectbox dropdown options */
[data-baseweb="select"] * { color: #f0f0f0 !important; background: #1a1a1a !important; }
[data-baseweb="popover"] { background: #1a1a1a !important; }
[role="option"] { background: #1a1a1a !important; color: #f0f0f0 !important; }
[role="option"]:hover { background: #252525 !important; }

/* ─── BUTTONS ─── */
div.stButton > button {
    background: #f0f0f0 !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px;
}

div.stButton > button:hover {
    background: #d4d4d4 !important;
    transform: translateY(-1px);
}

/* Logout button special style */
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #666 !important;
    border: 1px solid #2a2a2a !important;
}

div.stButton > button[kind="secondary"]:hover {
    background: #1a1a1a !important;
    color: #f0f0f0 !important;
}

/* ─── TEXT INPUTS ─── */
.stTextInput > label {
    color: #888 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px !important;
}

.stTextInput > div > div > input {
    background: #1a1a1a !important;
    color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #f0f0f0 !important;
    transition: border-color 0.2s;
}

.stTextInput > div > div > input:focus {
    border-color: #555 !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.05) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder {
    color: #444 !important;
}

/* ─── CHAT INPUT ─── */
[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 14px !important;
    padding: 0.5rem 1rem !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #f0f0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #f0f0f0 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #444 !important;
}

[data-testid="stChatInput"] button {
    background: #f0f0f0 !important;
    border-radius: 8px !important;
    color: #0d0d0d !important;
}

/* ─── CHAT MESSAGES ─── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.4rem 0 !important;
}

/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: transparent !important;
}

.stChatMessage p {
    color: #f0f0f0 !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}

/* Avatar icons fix for dark mode */
[data-testid="stChatMessageAvatar"] {
    background: #1e1e1e !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 50% !important;
}

/* ─── SCROLLABLE CHAT AREA ─── */
.chat-scroll-area {
    height: calc(100vh - 220px);
    overflow-y: auto;
    padding: 1rem 0;
    padding-bottom: 1rem;
    scroll-behavior: smooth;
}

.chat-scroll-area::-webkit-scrollbar { width: 4px; }
.chat-scroll-area::-webkit-scrollbar-track { background: transparent; }
.chat-scroll-area::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 4px; }

/* ─── STICKY INPUT CONTAINER ─── */
.input-sticky {
    position: fixed;
    bottom: 0;
    left: 280px;
    right: 0;
    background: #0d0d0d;
    border-top: 1px solid #1a1a1a;
    padding: 1rem 2rem;
    z-index: 999;
}

/* ─── MARKDOWN & TEXT ─── */
.stMarkdown p, .stMarkdown div, p, span, label {
    color: #f0f0f0 !important;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #f0f0f0 !important;
}

/* ─── WARNINGS / ERRORS / INFO ─── */
[data-testid="stAlert"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    color: #f0f0f0 !important;
    border-radius: 10px !important;
}

/* ─── SPINNER ─── */
[data-testid="stSpinner"] { color: #f0f0f0 !important; }

/* ─── LOGIN PAGE ─── */
.login-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 2rem;
}

.login-card {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 20px;
    padding: 3rem 2.5rem;
    width: 100%;
    max-width: 420px;
}

.login-logo {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #f0f0f0;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0.3rem;
}

.login-tagline {
    text-align: center;
    color: #555;
    font-size: 0.85rem;
    margin-bottom: 2.5rem;
    letter-spacing: 0.5px;
}

/* ─── SIDEBAR COMPONENTS ─── */
.sidebar-profile {
    padding: 1.5rem 1rem 1rem;
    border-bottom: 1px solid #1e1e1e;
    margin-bottom: 1.2rem;
}

.profile-avatar {
    width: 48px;
    height: 48px;
    background: #f0f0f0;
    color: #0d0d0d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    margin-bottom: 0.8rem;
}

.profile-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #f0f0f0;
}

.profile-status {
    font-size: 0.75rem;
    color: #4ade80;
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 2px;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #4ade80;
    border-radius: 50%;
    box-shadow: 0 0 6px #4ade80;
    display: inline-block;
}

/* ─── CHAT HEADER ─── */
.chat-topbar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1.2rem 2rem;
    border-bottom: 1px solid #1a1a1a;
    background: #0d0d0d;
    position: sticky;
    top: 0;
    z-index: 100;
}

.chat-avatar {
    width: 40px;
    height: 40px;
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #f0f0f0;
    flex-shrink: 0;
}

.chat-recipient-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #f0f0f0;
}

.chat-recipient-status {
    font-size: 0.75rem;
    color: #4ade80;
}

/* ─── EMPTY STATE ─── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 50vh;
    color: #333;
    gap: 1rem;
}

.empty-state-icon {
    font-size: 3rem;
    opacity: 0.4;
}

.empty-state-text {
    font-size: 0.9rem;
    color: #444 !important;
    text-align: center;
}

/* ─── DIVIDER ─── */
hr { border-color: #1e1e1e !important; }

/* ─── COLUMNS FIX ─── */
[data-testid="column"] { padding: 0 !important; }

/* ─── MAIN CONTENT PADDING ─── */
.main-content {
    padding: 0 2rem;
    padding-bottom: 100px;
}

/* Section label in sidebar */
.section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #444 !important;
    padding: 0 1rem;
    margin-bottom: 0.5rem;
}
</style>
"""


def login():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='height: 80px'></div>", unsafe_allow_html=True)

        st.markdown("""
            <div class="login-logo">💬 KVP</div>
            <div class="login-tagline">PRIVATE · SECURE · SIMPLE</div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        pwd = st.text_input("Password", placeholder="••••••••", type="password", key="login_pwd")

        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn"):
            if not email or not pwd:
                st.warning("Please fill in both fields.")
                return
            with st.spinner("Authenticating..."):
                time.sleep(0.4)
                try:
                    result = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
                    if result.data:
                        user = result.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = user["name"]
                        st.rerun()
                    else:
                        st.error("Wrong email or password.")
                except Exception as e:
                    st.error(f"Error: {e}")


def chat():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # Load other users
    try:
        users_result = supabase.table("users").select("email, name") \
            .neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in users_result.data}
    except Exception:
        other_users = {}

    initials_me = st.session_state.user_name[0].upper()

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-profile">
                <div class="profile-avatar">{initials_me}</div>
                <div class="profile-name">{st.session_state.user_name}</div>
                <div class="profile-status">
                    <span class="status-dot"></span> Online
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Conversations</div>', unsafe_allow_html=True)

        if not other_users:
            st.warning("No other users found.")
            selected_recipient = None
        else:
            selected_recipient = st.selectbox(
                "chat_with",
                options=list(other_users.keys()),
                format_func=lambda x: other_users[x],
                label_visibility="collapsed"
            )

        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.rerun()

    # ── MAIN CHAT AREA ──
    if not selected_recipient:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-text">Select someone to chat with</div>
            </div>
        """, unsafe_allow_html=True)
        return

    recipient_name = other_users[selected_recipient]
    initials_them = recipient_name[0].upper()

    # Chat topbar
    st.markdown(f"""
        <div class="chat-topbar">
            <div class="chat-avatar">{initials_them}</div>
            <div>
                <div class="chat-recipient-name">{recipient_name}</div>
                <div class="chat-recipient-status">● Active now</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Load messages
    try:
        sent = supabase.table("messages").select("*") \
            .eq("sender", st.session_state.user_email) \
            .eq("recipient", selected_recipient).execute()

        received = supabase.table("messages").select("*") \
            .eq("sender", selected_recipient) \
            .eq("recipient", st.session_state.user_email).execute()

        messages = sorted(
            sent.data + received.data,
            key=lambda x: x["created_at"]
        )
    except Exception as e:
        st.error(f"Error loading messages: {e}")
        messages = []

    # Message display
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    if not messages:
        st.markdown(f"""
            <div class="empty-state">
                <div class="empty-state-icon">👋</div>
                <div class="empty-state-text">
                    No messages yet.<br>Start the conversation with {recipient_name}!
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            is_me = msg["sender"] == st.session_state.user_email
            role = "user" if is_me else "assistant"
            with st.chat_message(role):
                st.write(msg["message"])

    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input(f"Message {recipient_name}..."):
        try:
            supabase.table("messages").insert({
                "sender": st.session_state.user_email,
                "recipient": selected_recipient,
                "message": prompt
            }).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send: {e}")

    # Auto refresh
    time.sleep(3)
    st.rerun()


if not st.session_state.logged_in:
    login()
else:
    chat()
