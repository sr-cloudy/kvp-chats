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

# ── Global CSS (Updated for Sticky Elements) ──────────────────────────────────
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

/* 📌 FIX: Sticky Header in Main Screen */
[data-testid="stHeader"] {
    background: #f0efe9 !important;
    border-bottom: 1px solid #ddddd5 !important;
    position: sticky !important;
    top: 0;
    z-index: 1000;
}

footer, #MainMenu { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1.5px solid #ddddd5 !important;
}

/* 📌 FIX: Sticky Profile in Sidebar */
.sticky-profile {
    position: sticky;
    top: 0;
    background: white;
    z-index: 100;
    padding: 1.1rem 1rem 0.9rem;
    border-bottom: 1.5px solid #ddddd5;
    margin-bottom: 10px;
}

/* Typography */
p, span, label, div, h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Chat Bubbles Styling */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0.5rem 0 2rem;
    width: 100%;
}

.brow {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    width: 100%;
}
.brow.me { flex-direction: row-reverse; }

.av {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
}
.av-me   { background: #1a1a1a; color: #ffffff; }
.av-them { background: #ddddd5; color: #1a1a1a; }

.bbl {
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 0.93rem;
    line-height: 1.55;
    word-break: break-word;
    white-space: pre-wrap;
    display: inline-block;
    max-width: 100%;
}
.bbl-me { background: #1a1a1a; color: #ffffff !important; border-bottom-right-radius: 5px; }
.bbl-them { background: #ffffff; color: #1a1a1a !important; border: 1.5px solid #e0e0d8; border-bottom-left-radius: 5px; }

.bts { font-size: 0.68rem; color: #aaa !important; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers (Your Original Logic) ─────────────────────────────────────────────

def update_presence():
    try:
        supabase.table("presence").upsert({
            "email": st.session_state.user_email,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception: pass

def get_online_emails(threshold: int = 15) -> set:
    try:
        res = supabase.table("presence").select("email, last_seen").execute()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=threshold)
        online = set()
        for row in res.data:
            try:
                last = datetime.fromisoformat(row["last_seen"].replace("Z", "+00:00"))
                if last >= cutoff: online.add(row["email"])
            except Exception: pass
        return online
    except Exception: return set()

def get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2: return (parts[0][0] + parts[-1][0]).upper()
    return (name[:2].upper() if len(name) >= 2 else name[0].upper()) if name else "?"

def fmt_time(iso: str) -> str:
    try:
        ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        h  = ts.strftime("%I").lstrip("0") or "12"
        return f"{h}:{ts.strftime('%M %p')}"
    except Exception: return ""

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
        group  = f'<div class="bgrp"><div class="bbl {bbl_cls}">{text}</div><div class="bts">{ts}</div></div>'
        rows.append(f'<div class="brow {row_cls}">{avatar}{group}</div>')
    return '<div class="chat-wrap">' + "\n".join(rows) + "</div>"

def status_badge(is_online: bool) -> str:
    color = "#22c55e" if is_online else "#ef4444"
    lbl = "Online" if is_online else "Offline"
    dot_cls = "dot-green" if is_online else "dot-red"
    return f'<span style="color:{color}; font-size:0.8rem; font-weight:600;">● {lbl}</span>'

# ── Pages ─────────────────────────────────────────────────────────────────────

def show_login():
    _, col, _ = st.columns([1, 2.2, 1])
    with col:
        st.markdown("## 💬 KVP Chat")
        email = st.text_input("Email", key="li_email")
        pwd   = st.text_input("Password", type="password", key="li_pwd")
        if st.button("Sign In"):
            res = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = res.data[0]["name"]
                st.rerun()
            else: st.error("Wrong credentials")

def show_chat():
    update_presence()
    try:
        res = supabase.table("users").select("email, name").neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in res.data}
    except: other_users = {}

    online_set = get_online_emails()
    
    with st.sidebar:
        # 📌 STICKY SIDEBAR PROFILE
        st.markdown(f'''
            <div class="sticky-profile">
                <div style="font-weight:700;">👤 {st.session_state.user_name}</div>
                <div style="font-size:0.75rem; color:#888;">{st.session_state.user_email}</div>
                {status_badge(st.session_state.user_email in online_set)}
            </div>
        ''', unsafe_allow_html=True)
        
        st.write("### Chat with")
        user_emails = list(other_users.keys())
        selected_recipient = st.selectbox("user", options=user_emails, 
                                          format_func=lambda e: f"{'🟢' if e in online_set else '🔴'} {other_users[e]}", 
                                          label_visibility="collapsed")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if selected_recipient:
        their_name = other_users[selected_recipient]
        # 📌 MAIN HEADER
        st.markdown(f"### 💬 {their_name} {status_badge(selected_recipient in online_set)}", unsafe_allow_html=True)
        st.divider()

        # Load Messages (Your Original Logic)
        sent = supabase.table("messages").select("*").eq("sender", st.session_state.user_email).eq("recipient", selected_recipient).execute()
        received = supabase.table("messages").select("*").eq("sender", selected_recipient).eq("recipient", st.session_state.user_email).execute()
        messages = sorted(sent.data + received.data, key=lambda x: x["created_at"])

        if not messages:
            st.write(f"Say hello to {their_name}!")
        else:
            st.markdown(build_chat_html(messages, st.session_state.user_email, st.session_state.user_name, their_name), unsafe_allow_html=True)

        if prompt := st.chat_input(f"Message {their_name}..."):
            supabase.table("messages").insert({"sender": st.session_state.user_email, "recipient": selected_recipient, "message": prompt}).execute()
            st.rerun()

        time.sleep(5)
        st.rerun()

# ── Entry ─────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
else:
    show_chat()
