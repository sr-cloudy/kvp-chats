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

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: #0d0d0d !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #f0f0f0 !important;
}

/* ── Hide Streamlit chrome but KEEP the sidebar toggle button ── */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }

/* Keep the sidebar collapse/expand button visible and style it */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0f0f0 !important;
    z-index: 99999 !important;
}

[data-testid="stSidebarCollapsedControl"] svg {
    fill: #f0f0f0 !important;
    color: #f0f0f0 !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #1e1e1e !important;
}
section[data-testid="stSidebar"] * { color: #f0f0f0 !important; }
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
}
[data-baseweb="select"] * { color: #f0f0f0 !important; background: #1a1a1a !important; }
[data-baseweb="popover"] { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; }
[role="option"] { background: #1a1a1a !important; color: #f0f0f0 !important; }
[role="option"]:hover { background: #252525 !important; }

/* ── BUTTONS ── */
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
}
div.stButton > button:hover {
    background: #d4d4d4 !important;
    transform: translateY(-1px);
}

/* ── TEXT INPUTS ── */
.stTextInput > label {
    color: #666 !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
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
}
.stTextInput > div > div > input:focus {
    border-color: #444 !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #3a3a3a !important; }

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #f0f0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #f0f0f0 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #3a3a3a !important; }
[data-testid="stChatInput"] button {
    background: #f0f0f0 !important;
    border-radius: 8px !important;
    color: #0d0d0d !important;
}

/* ── STICKY BOTTOM INPUT AREA ── */
[data-testid="stBottom"] {
    background: #0d0d0d !important;
    border-top: 1px solid #1a1a1a !important;
    padding: 0.8rem 1rem !important;
    position: sticky !important;
    bottom: 0 !important;
    z-index: 9998 !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.3rem 0 !important;
}
.stChatMessage p {
    color: #f0f0f0 !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}
[data-testid="stChatMessageAvatar"] {
    background: #1e1e1e !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 50% !important;
}

/* ── FIXED TOPBAR ── */
.kvp-topbar {
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
    height: 64px;
    background: #0d0d0d;
    border-bottom: 1px solid #1a1a1a;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 1.5rem 0 4rem; /* left padding to avoid overlap with sidebar toggle */
    z-index: 9997;
}

/* On wider screens push topbar past the sidebar */
@media (min-width: 768px) {
    .kvp-topbar {
        left: 0;
        padding-left: 2rem;
    }
}

.kvp-topbar .chat-avatar {
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
.kvp-topbar .rname {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #f0f0f0;
    line-height: 1.2;
}
.kvp-topbar .rstatus {
    font-size: 0.72rem;
    color: #4ade80;
}

/* Push main content below topbar */
[data-testid="stMain"] .block-container {
    padding-top: 80px !important;
    padding-bottom: 20px !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* ── MISC TEXT ── */
hr { border-color: #1e1e1e !important; }
.stMarkdown p, p, span, label { color: #f0f0f0 !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #f0f0f0 !important; }
[data-testid="stAlert"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    color: #f0f0f0 !important;
    border-radius: 10px !important;
}

/* ── SIDEBAR PROFILE ── */
.sidebar-profile {
    padding: 1.5rem 1rem 1rem;
    border-bottom: 1px solid #1e1e1e;
    margin-bottom: 1rem;
}
.profile-avatar {
    width: 46px;
    height: 46px;
    background: #f0f0f0;
    color: #0d0d0d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    margin-bottom: 0.6rem;
}
.profile-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #f0f0f0;
}
.profile-status { font-size: 0.72rem; color: #4ade80; margin-top: 2px; }
.status-dot {
    display: inline-block;
    width: 6px; height: 6px;
    background: #4ade80;
    border-radius: 50%;
    box-shadow: 0 0 6px #4ade80;
    margin-right: 4px;
    vertical-align: middle;
}
.section-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #444 !important;
    padding: 0 1rem;
    margin-bottom: 0.4rem;
    display: block;
}

/* ── LOGIN ── */
.login-logo {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #f0f0f0;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0.25rem;
}
.login-tagline {
    text-align: center;
    color: #444 !important;
    font-size: 0.78rem;
    letter-spacing: 2px;
    margin-bottom: 2.5rem;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
}
.empty-state-icon { font-size: 3rem; opacity: 0.3; }
.empty-state-text { font-size: 0.88rem; color: #444 !important; margin-top: 1rem; }
</style>
"""


def login():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="login-logo">💬 KVP</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-tagline">PRIVATE · SECURE · SIMPLE</div>', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        pwd   = st.text_input("Password", placeholder="••••••••", type="password", key="login_pwd")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn"):
            if not email or not pwd:
                st.warning("Please fill in both fields.")
                return
            with st.spinner("Signing in..."):
                time.sleep(0.4)
                try:
                    res = supabase.table("users").select("*") \
                        .eq("email", email).eq("password", pwd).execute()
                    if res.data:
                        u = res.data[0]
                        st.session_state.logged_in  = True
                        st.session_state.user_email = email
                        st.session_state.user_name  = u["name"]
                        st.rerun()
                    else:
                        st.error("Wrong email or password.")
                except Exception as e:
                    st.error(f"Error: {e}")


def chat():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # Load other users
    try:
        res = supabase.table("users").select("email, name") \
            .neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in res.data}
    except Exception:
        other_users = {}

    me_initial = st.session_state.user_name[0].upper()

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-profile">
                <div class="profile-avatar">{me_initial}</div>
                <div class="profile-name">{st.session_state.user_name}</div>
                <div class="profile-status">
                    <span class="status-dot"></span>Online
                </div>
            </div>
            <span class="section-label">Conversations</span>
        """, unsafe_allow_html=True)

        selected_recipient = None
        if not other_users:
            st.warning("No other users found.")
        else:
            selected_recipient = st.selectbox(
                "chat_with",
                options=list(other_users.keys()),
                format_func=lambda x: other_users[x],
                label_visibility="collapsed"
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", key="logout_btn"):
            st.session_state.logged_in  = False
            st.session_state.user_email = ""
            st.session_state.user_name  = ""
            st.rerun()

    # ── NO RECIPIENT ──
    if not selected_recipient:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-text">Select someone to start chatting</div>
            </div>
        """, unsafe_allow_html=True)
        return

    recipient_name = other_users[selected_recipient]
    them_initial   = recipient_name[0].upper()

    # ── FIXED TOPBAR ──
    # Injected as HTML with position:fixed so it never scrolls away
    st.markdown(f"""
        <div class="kvp-topbar">
            <div class="chat-avatar">{them_initial}</div>
            <div>
                <div class="rname">{recipient_name}</div>
                <div class="rstatus">● Active now</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── LOAD MESSAGES ──
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

    # ── DISPLAY MESSAGES ──
    if not messages:
        st.markdown(f"""
            <div class="empty-state">
                <div class="empty-state-icon">👋</div>
                <div class="empty-state-text">
                    No messages yet — say hello to {recipient_name}!
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            role = "user" if msg["sender"] == st.session_state.user_email else "assistant"
            with st.chat_message(role):
                st.write(msg["message"])

    # ── SEND MESSAGE ──
    if prompt := st.chat_input(f"Message {recipient_name}..."):
        try:
            supabase.table("messages").insert({
                "sender":    st.session_state.user_email,
                "recipient": selected_recipient,
                "message":   prompt
            }).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send: {e}")

    # Auto-refresh every 3 s for incoming messages
    time.sleep(3)
    st.rerun()


if not st.session_state.logged_in:
    login()
else:
    chat()
