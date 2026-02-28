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

# ── Global CSS (Fixed for Sticky & Icons) ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

/* Fix broken sidebar icon text */
button[kind="header"] div {
    font-size: 0px !important;
}

/* Base App Styling */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f0efe9 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* 📌 STICKY MAIN HEADER */
[data-testid="stHeader"] {
    background: #f0efe9 !important;
    border-bottom: 1px solid #ddddd5 !important;
    position: sticky !important;
    top: 0;
    z-index: 99;
}

/* 📌 STICKY SIDEBAR PROFILE */
/* This ensures the profile stays at the top of the sidebar */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
    position: sticky !important;
    top: 0;
    z-index: 100;
    background: white !important;
    padding-top: 10px;
}

.sticky-profile-box {
    background: white !important;
    padding: 1rem;
    border-bottom: 1.5px solid #ddddd5;
    width: 100%;
}

/* Chat Bubble Styling */
.chat-wrap { display: flex; flex-direction: column; gap: 10px; padding: 1rem 0; width: 100%; }
.brow { display: flex; align-items: flex-end; gap: 8px; width: 100%; }
.brow.me { flex-direction: row-reverse; }
.av { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700; flex-shrink: 0;}
.av-me { background: #1a1a1a; color: white; }
.av-them { background: #ddddd5; color: #1a1a1a; }
.bbl { padding: 10px 14px; border-radius: 18px; font-size: 0.93rem; line-height: 1.55; word-break: break-word; white-space: pre-wrap; display: inline-block; max-width: 80%; }
.bbl-me { background: #1a1a1a; color: #ffffff !important; border-bottom-right-radius: 4px; }
.bbl-them { background: #ffffff; color: #1a1a1a !important; border: 1px solid #e0e0d8; border-bottom-left-radius: 4px; }
.bts { font-size: 0.65rem; color: #aaa !important; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers (Logic remains exactly same) ──────────────────────────────────────

def update_presence():
    try:
        supabase.table("presence").upsert({
            "email": st.session_state.user_email,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception: pass

def get_online_emails() -> set:
    try:
        res = supabase.table("presence").select("email, last_seen").execute()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=20)
        return {row["email"] for row in res.data if datetime.fromisoformat(row["last_seen"].replace("Z", "+00:00")) >= cutoff}
    except: return set()

def get_initials(name: str) -> str:
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else (name[:2].upper() if name else "?")

def fmt_time(iso: str) -> str:
    try: return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%I:%M %p").lstrip("0")
    except: return ""

def build_chat_html(messages, my_email, my_name, their_name) -> str:
    rows = []
    for msg in messages:
        is_me = msg["sender"] == my_email
        row_cls, bbl_cls, av_cls = ("me", "bbl-me", "av-me") if is_me else ("", "bbl-them", "av-them")
        avatar = f'<div class="av {av_cls}">{get_initials(my_name if is_me else their_name)}</div>'
        content = f'<div class="bbl {bbl_cls}">{htmllib.escape(str(msg.get("message", "")))}</div>'
        ts = f'<div class="bts">{fmt_time(msg.get("created_at", ""))}</div>'
        rows.append(f'<div class="brow {row_cls}">{avatar}<div>{content}{ts}</div></div>')
    return f'<div class="chat-wrap">{"".join(rows)}</div>'

# ── App Flow ──────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("💬 KVP Chat")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Sign In"):
            res = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
            if res.data:
                st.session_state.update({"logged_in": True, "user_email": email, "user_name": res.data[0]["name"]})
                st.rerun()
            else: st.error("Wrong login")
else:
    update_presence()
    online_set = get_online_emails()
    
    # SIDEBAR
    with st.sidebar:
        # Wrapped in a div for the sticky CSS to target
        st.markdown(f'''
            <div class="sticky-profile-box">
                <div style="font-weight:700; font-size:1.1rem;">👤 {st.session_state.user_name}</div>
                <div style="font-size:0.8rem; color:#888;">{st.session_state.user_email}</div>
                <div style="color:#22c55e; font-size:0.75rem; font-weight:600;">● Online</div>
            </div>
        ''', unsafe_allow_html=True)
        
        try:
            res = supabase.table("users").select("email, name").neq("email", st.session_state.user_email).execute()
            other_users = {u["email"]: u["name"] for u in res.data}
            st.write("### Chat with")
            sel_email = st.selectbox("Users", options=list(other_users.keys()), 
                                     format_func=lambda e: f"{'🟢' if e in online_set else '🔴'} {other_users[e]}",
                                     label_visibility="collapsed")
        except: sel_email = None

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # MAIN CHAT
    if sel_email:
        status = "🟢 Online" if sel_email in online_set else "🔴 Offline"
        st.markdown(f"### 💬 {other_users[sel_email]} <small style='font-size:0.7rem; color:#888;'>{status}</small>", unsafe_allow_html=True)
        
        # Load messages (Logic remains yours)
        sent = supabase.table("messages").select("*").eq("sender", st.session_state.user_email).eq("recipient", sel_email).execute()
        recv = supabase.table("messages").select("*").eq("sender", sel_email).eq("recipient", st.session_state.user_email).execute()
        msgs = sorted(sent.data + recv.data, key=lambda x: x["created_at"])
        
        st.markdown(build_chat_html(msgs, st.session_state.user_email, st.session_state.user_name, other_users[sel_email]), unsafe_allow_html=True)

        if prompt := st.chat_input(f"Message {other_users[sel_email]}..."):
            supabase.table("messages").insert({"sender": st.session_state.user_email, "recipient": sel_email, "message": prompt}).execute()
            st.rerun()

    time.sleep(5)
    st.rerun()
