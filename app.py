import streamlit as st
from supabase import create_client
import time
import html as htmllib
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="KVP Chat", page_icon="💬", layout="centered")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ── Session defaults ──────────────────────────────────────────────────────────
for key, val in {"logged_in": False, "user_email": "", "user_name": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* Base */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #f0efe9 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"] {
    background: #f0efe9 !important;
    border-bottom: 1px solid #ddddd5 !important;
}
footer, #MainMenu { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1.5px solid #ddddd5 !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* Typography */
p, span, label, div, h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 5rem !important;
}

/* Inputs */
.stTextInput > label {
    color: #555 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
.stTextInput input {
    background: #fafaf8 !important;
    color: #1a1a1a !important;
    border: 1.5px solid #ddddd5 !important;
    border-radius: 10px !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput input:focus {
    border-color: #1a1a1a !important;
    box-shadow: 0 0 0 3px rgba(26,26,26,0.08) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: #c0c0b8 !important; }

/* Buttons - main solid black */
div.stButton > button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    letter-spacing: 0.02em !important;
}
div.stButton > button:hover { background: #333 !important; border-color: #333 !important; }
div.stButton > button:active { background: #000 !important; border-color: #000 !important; }

/* Sidebar logout - outlined */
section[data-testid="stSidebar"] div.stButton > button {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1.5px solid #ddddd5 !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #f0efe9 !important;
    border-color: #999 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #ddddd5 !important;
    border-radius: 10px !important;
}
[data-baseweb="select"] * { color: #1a1a1a !important; background: #fff !important; }
[role="option"]:hover { background: #f0efe9 !important; }

/* Chat input */
[data-testid="stBottom"] {
    background: #f0efe9 !important;
    border-top: 1px solid #ddddd5 !important;
}
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1.5px solid #ddddd5 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatInput"] textarea {
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #c0c0b8 !important; }
[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    border-radius: 8px !important;
    color: #fff !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid #ddddd5 !important;
    margin: 0.75rem 0 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Status dots */
.dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    vertical-align: middle;
    margin-right: 5px;
    flex-shrink: 0;
}
.dot-green { background: #22c55e; box-shadow: 0 0 0 2px rgba(34,197,94,0.22); }
.dot-red   { background: #ef4444; }

/* ════════════════════════════════════════
   CHAT BUBBLES  — the proper fix
   ════════════════════════════════════════ */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0.5rem 0 2rem;
    width: 100%;
}

/* Each row: avatar + bubble group side by side */
.brow {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    width: 100%;
}
/* My messages: reverse so avatar goes right */
.brow.me { flex-direction: row-reverse; }

/* Avatar circle */
.av {
    width: 34px;
    height: 34px;
    min-width: 34px;
    min-height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    flex-shrink: 0;
    font-family: 'DM Sans', sans-serif;
    line-height: 1;
}
.av-me   { background: #1a1a1a; color: #ffffff; }
.av-them { background: #ddddd5; color: #1a1a1a; }

/* Bubble group: bubble + timestamp stacked */
.bgrp {
    display: flex;
    flex-direction: column;
    gap: 3px;
    /* KEY: limit width so bubble doesn't go full-screen,
       but also don't let it collapse to a tiny strip */
    max-width: calc(100% - 50px);
    min-width: 0;
}
/* Align group content to the right for "me" rows */
.brow.me .bgrp {
    align-items: flex-end;
}

/* The bubble itself */
.bbl {
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 0.93rem;
    line-height: 1.55;
    word-break: break-word;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
    /* CRITICAL: bubble should size to content, not stretch full width */
    display: inline-block;
    max-width: 100%;
}
.bbl-me {
    background: #1a1a1a;
    color: #ffffff !important;
    border-bottom-right-radius: 5px;
}
.bbl-them {
    background: #ffffff;
    color: #1a1a1a !important;
    border: 1.5px solid #e0e0d8;
    border-bottom-left-radius: 5px;
}

/* Timestamp */
.bts {
    font-size: 0.68rem;
    color: #aaa !important;
    padding: 0 3px;
    font-family: 'DM Sans', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def update_presence():
    try:
        supabase.table("presence").upsert({
            "email": st.session_state.user_email,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception:
        pass


def get_online_emails(threshold: int = 15) -> set:
    try:
        res    = supabase.table("presence").select("email, last_seen").execute()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=threshold)
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


def get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (name[:2].upper() if len(name) >= 2 else name[0].upper()) if name else "?"


def fmt_time(iso: str) -> str:
    try:
        ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        h  = ts.strftime("%I").lstrip("0") or "12"
        return f"{h}:{ts.strftime('%M %p')}"
    except Exception:
        return ""


def build_chat_html(messages, my_email, my_name, their_name) -> str:
    rows = []
    for msg in messages:
        is_me   = msg["sender"] == my_email
        text    = htmllib.escape(str(msg.get("message", "")))
        ts      = fmt_time(msg.get("created_at", ""))
        av_init = get_initials(my_name if is_me else their_name)
        av_cls  = "av-me" if is_me else "av-them"
        row_cls = "me" if is_me else ""
        bbl_cls = "bbl-me" if is_me else "bbl-them"

        avatar = f'<div class="av {av_cls}">{av_init}</div>'
        group  = f'''<div class="bgrp">
            <div class="bbl {bbl_cls}">{text}</div>
            <div class="bts">{ts}</div>
        </div>'''
        rows.append(f'<div class="brow {row_cls}">{avatar}{group}</div>')

    return '<div class="chat-wrap">' + "\n".join(rows) + "</div>"


def status_badge(is_online: bool) -> str:
    cls = "dot dot-green" if is_online else "dot dot-red"
    lbl = "Online" if is_online else "Offline"
    color = "#22c55e" if is_online else "#ef4444"
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'font-size:0.8rem;font-weight:500;color:{color} !important;">'
        f'<span class="{cls}"></span>{lbl}</span>'
    )


# ── Login page ────────────────────────────────────────────────────────────────

def show_login():
    # Use columns to naturally center — no broken HTML div wrapping
    _, col, _ = st.columns([1, 2.2, 1])
    with col:
        st.markdown(
            "<h2 style='margin-bottom:4px;'>💬 KVP Chat</h2>"
            "<p style='color:#888 !important;margin-bottom:1.4rem;font-size:0.92rem;'>"
            "Private &amp; secure messaging</p>",
            unsafe_allow_html=True
        )
        st.divider()

        email = st.text_input("Email", placeholder="you@example.com", key="li_email")
        pwd   = st.text_input("Password", placeholder="••••••••", type="password", key="li_pwd")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In", key="li_btn"):
            if not email or not pwd:
                st.warning("Please fill in both fields.")
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


# ── Chat page ─────────────────────────────────────────────────────────────────

def show_chat():
    update_presence()

    try:
        res = supabase.table("users").select("email, name") \
            .neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in res.data}
    except Exception:
        other_users = {}

    online_set = get_online_emails()
    me_online  = st.session_state.user_email in online_set

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        # Sticky profile header
        st.markdown(
            f"<div style='padding:1.1rem 1rem 0.9rem;"
            f"border-bottom:1.5px solid #ddddd5;background:#fff;"
            f"position:sticky;top:0;z-index:99;'>"
            f"<div style='font-weight:700;font-size:1rem;margin-bottom:2px;'>"
            f"👤 {st.session_state.user_name}</div>"
            f"<div style='font-size:0.76rem;color:#888 !important;margin-bottom:6px;'>"
            f"{st.session_state.user_email}</div>"
            f"{status_badge(me_online)}"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='padding:0.9rem 0.8rem 0;'>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='font-weight:600;font-size:0.82rem;"
            "text-transform:uppercase;letter-spacing:0.05em;color:#888 !important;"
            "margin-bottom:6px;'>Chat with</p>",
            unsafe_allow_html=True
        )

        selected_recipient = None
        if not other_users:
            st.warning("No other users found.")
        else:
            user_emails = list(other_users.keys())

            def fmt(email):
                icon = "🟢" if email in online_set else "🔴"
                return f"{icon} {other_users[email]}"

            selected_recipient = st.selectbox(
                "user", options=user_emails,
                format_func=fmt, label_visibility="collapsed"
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.logged_in  = False
            st.session_state.user_email = ""
            st.session_state.user_name  = ""
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Main ─────────────────────────────────────────────────────────────────
    if not selected_recipient:
        st.info("Select a user from the sidebar to start chatting.")
        return

    their_name   = other_users[selected_recipient]
    their_online = selected_recipient in online_set

    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;padding:0.2rem 0 0.4rem;'>"
        f"<span style='font-size:1.2rem;font-weight:700;'>💬 {their_name}</span>"
        f"{status_badge(their_online)}"
        f"</div>",
        unsafe_allow_html=True
    )
    st.divider()

    # Load messages
    try:
        sent     = supabase.table("messages").select("*") \
                    .eq("sender",    st.session_state.user_email) \
                    .eq("recipient", selected_recipient).execute()
        received = supabase.table("messages").select("*") \
                    .eq("sender",    selected_recipient) \
                    .eq("recipient", st.session_state.user_email).execute()
        messages = sorted(sent.data + received.data, key=lambda x: x["created_at"])
    except Exception as e:
        st.error(f"Error loading messages: {e}")
        messages = []

    # Render
    if not messages:
        st.markdown(
            f"<div style='text-align:center;color:#b8b8b0;padding:3rem 0;font-size:0.95rem;'>"
            f"👋 Say hello to {their_name}!</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            build_chat_html(
                messages,
                st.session_state.user_email,
                st.session_state.user_name,
                their_name
            ),
            unsafe_allow_html=True
        )

    # Send
    if prompt := st.chat_input(f"Message {their_name}..."):
        try:
            supabase.table("messages").insert({
                "sender":    st.session_state.user_email,
                "recipient": selected_recipient,
                "message":   prompt
            }).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send: {e}")

    time.sleep(5)
    st.rerun()


# ── Entry ─────────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    show_login()
else:
    show_chat()
