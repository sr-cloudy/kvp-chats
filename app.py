import streamlit as st
from supabase import create_client
import time
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="KVP Chat", page_icon="💬", layout="centered")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: #f5f5f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] {
    background: #f5f5f0 !important;
    border-bottom: 1px solid #e0e0d8 !important;
}

footer, #MainMenu { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1.5px solid #e0e0d8 !important;
    min-width: 240px !important;
    max-width: 260px !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 0 !important;
}

/* Sticky user header at top of sidebar */
section[data-testid="stSidebar"] > div > div:first-child {
    position: sticky !important;
    top: 0 !important;
    background: #ffffff !important;
    z-index: 100 !important;
    padding: 1.2rem 1rem 0.8rem !important;
    border-bottom: 1.5px solid #e0e0d8 !important;
    margin-bottom: 1rem !important;
}

/* ── Typography ── */
p, span, label, div, h1, h2, h3, h4 {
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Text inputs ── */
.stTextInput > label {
    color: #666 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}

.stTextInput input {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1.5px solid #ddd !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.95rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput input:focus {
    border-color: #1a1a1a !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(26,26,26,0.08) !important;
}

.stTextInput input::placeholder { color: #bbb !important; }

/* ── Buttons ── */
div.stButton > button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    font-size: 0.92rem !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.1s ease !important;
}

div.stButton > button:hover {
    background: #333333 !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:active {
    background: #000000 !important;
    transform: translateY(0) !important;
}

/* Logout button - outlined style */
section[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    color: #1a1a1a !important;
    border: 1.5px solid #ddd !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #f5f5f0 !important;
    border-color: #1a1a1a !important;
    transform: none !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #ddd !important;
    border-radius: 10px !important;
    color: #1a1a1a !important;
}

[data-baseweb="select"] * { color: #1a1a1a !important; background: #fff !important; }
[role="option"]:hover { background: #f5f5f0 !important; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1.5px solid #ddd !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
}

[data-testid="stChatInput"] textarea {
    color: #1a1a1a !important;
    background: transparent !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}

[data-testid="stChatInput"] textarea::placeholder { color: #bbb !important; }

[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    border-radius: 8px !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
}

.stChatMessage p {
    color: #1a1a1a !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
}

/* ── Bottom bar ── */
[data-testid="stBottom"] {
    background: #f5f5f0 !important;
    border-top: 1px solid #e0e0d8 !important;
    padding: 0.8rem 1rem !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #e0e0d8 !important;
    margin: 0.8rem 0 !important;
}

/* ── Online dot styles ── */
.user-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    color: #666 !important;
    font-weight: 500;
}

.dot-online {
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 2px rgba(34,197,94,0.25);
    flex-shrink: 0;
}

.dot-offline {
    width: 8px; height: 8px;
    background: #ef4444;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

/* ── Login card ── */
.login-card {
    background: #ffffff;
    border: 1.5px solid #e0e0d8;
    border-radius: 20px;
    padding: 2.5rem 2rem;
    max-width: 400px;
    margin: 3rem auto 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Chat bubbles ── */
.chat-area {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 1rem 0 1.5rem;
}

.bubble-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
}

.bubble-row.me {
    flex-direction: row-reverse;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    flex-shrink: 0;
    letter-spacing: 0.03em;
}

.avatar.me-av   { background: #1a1a1a; color: #fff; }
.avatar.them-av { background: #e0e0d8; color: #1a1a1a; }

.bubble {
    max-width: 68%;
    padding: 0.6rem 1rem;
    border-radius: 18px;
    font-size: 0.95rem;
    line-height: 1.5;
    word-break: break-word;
    color: #1a1a1a !important;
}

.bubble.me {
    background: #1a1a1a;
    color: #ffffff !important;
    border-bottom-right-radius: 4px;
}

.bubble.them {
    background: #ffffff;
    border: 1.5px solid #e0e0d8;
    border-bottom-left-radius: 4px;
}

.bubble-time {
    font-size: 0.7rem;
    color: #bbb !important;
    margin-top: 2px;
    padding: 0 4px;
}

.time-me   { text-align: right; }
.time-them { text-align: left; }

.msg-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def update_presence():
    """Upsert a heartbeat row so others can see we're online."""
    try:
        supabase.table("presence").upsert({
            "email": st.session_state.user_email,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception:
        pass  # presence table may not exist — silently skip


def get_online_emails(threshold_seconds: int = 15) -> set:
    """Return set of emails seen within threshold_seconds."""
    try:
        res = supabase.table("presence").select("email, last_seen").execute()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=threshold_seconds)
        online = set()
        for row in res.data:
            try:
                last = datetime.fromisoformat(row["last_seen"].replace("Z", "+00:00"))
                if last >= cutoff:
                    online.add(row["email"])
            except Exception:
                pass
        return online
    except Exception:
        return set()


def initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "?"


def render_messages_html(messages, my_email, my_name, recipient_name):
    """Render all messages as clean custom HTML bubbles."""
    if not messages:
        return ""

    import html as htmllib

    rows = []
    for msg in messages:
        is_me = msg["sender"] == my_email
        text  = htmllib.escape(msg["message"])
        name  = my_name if is_me else recipient_name
        av_cls    = "me-av" if is_me else "them-av"
        bub_cls   = "me"    if is_me else "them"
        row_cls   = "me"    if is_me else ""
        time_cls  = "time-me" if is_me else "time-them"

        try:
            ts  = datetime.fromisoformat(msg["created_at"].replace("Z", "+00:00"))
            ts_label = ts.strftime("%-I:%M %p")
        except Exception:
            ts_label = ""

        av_html = f'<div class="avatar {av_cls}">{initials(name)}</div>'
        bub_html = f'''
        <div class="msg-group">
          <div class="bubble {bub_cls}">{text}</div>
          <div class="bubble-time {time_cls}">{ts_label}</div>
        </div>'''

        if is_me:
            row = f'<div class="bubble-row {row_cls}">{av_html}{bub_html}</div>'
        else:
            row = f'<div class="bubble-row {row_cls}">{av_html}{bub_html}</div>'

        rows.append(row)

    inner = "\n".join(rows)
    return f'<div class="chat-area">{inner}</div>'


def status_dot(is_online: bool) -> str:
    cls = "dot-online" if is_online else "dot-offline"
    label = "Online" if is_online else "Offline"
    return f'<span class="user-status"><span class="{cls}"></span>{label}</span>'


# ── Login ─────────────────────────────────────────────────────────────────────

def login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("## 💬 KVP Chat")
    st.markdown("<p style='color:#666;margin-top:-0.5rem;'>Private &amp; secure messaging</p>", unsafe_allow_html=True)
    st.markdown("---")

    email = st.text_input("Email", placeholder="you@example.com")
    pwd   = st.text_input("Password", placeholder="••••••••", type="password")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Sign In"):
        if not email or not pwd:
            st.warning("Please enter email and password.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        with st.spinner("Signing in..."):
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

    st.markdown('</div>', unsafe_allow_html=True)


# ── Chat ──────────────────────────────────────────────────────────────────────

def chat():
    # Heartbeat
    update_presence()

    # Load other users
    try:
        res = supabase.table("users").select("email, name") \
            .neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in res.data}
    except Exception:
        other_users = {}

    # Online status
    online_set = get_online_emails()

    # ── SIDEBAR ──
    with st.sidebar:
        # Sticky user profile block
        me_online = st.session_state.user_email in online_set
        st.markdown(
            f"### 👤 {st.session_state.user_name}<br>"
            f"<span style='color:#888;font-size:0.8rem;'>{st.session_state.user_email}</span><br>"
            f"{status_dot(me_online)}",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("**Chat with**")

        if not other_users:
            st.warning("No other users found.")
            selected_recipient = None
        else:
            # Build options with status labels
            user_emails = list(other_users.keys())
            def format_user(email):
                name = other_users[email]
                dot = "🟢" if email in online_set else "🔴"
                return f"{dot} {name}"

            selected_recipient = st.selectbox(
                "Select user",
                options=user_emails,
                format_func=format_user,
                label_visibility="collapsed"
            )

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in  = False
            st.session_state.user_email = ""
            st.session_state.user_name  = ""
            st.rerun()

    # ── MAIN ──
    if not selected_recipient:
        st.info("Select a user from the sidebar to start chatting.")
        return

    recipient_name   = other_users[selected_recipient]
    recipient_online = selected_recipient in online_set

    # Chat header
    st.markdown(
        f"### 💬 {recipient_name} &nbsp; {status_dot(recipient_online)}",
        unsafe_allow_html=True
    )
    st.markdown("---")

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

    # Display messages
    if not messages:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align:center;color:#bbb;font-size:0.95rem;'>👋 Say hello to {recipient_name}!</div>",
            unsafe_allow_html=True
        )
    else:
        html = render_messages_html(
            messages,
            st.session_state.user_email,
            st.session_state.user_name,
            recipient_name
        )
        st.markdown(html, unsafe_allow_html=True)

    # Send message
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

    # Auto refresh every 5 seconds (reduced from 3 to be less aggressive)
    time.sleep(5)
    st.rerun()


# ── Entry ─────────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    login()
else:
    chat()
