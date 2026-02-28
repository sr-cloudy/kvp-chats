import streamlit as st
from supabase import create_client
import time
import html as htmllib
from datetime import datetime, timezone, timedelta

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="KVP Chat", page_icon="💬", layout="wide")

@st.cache_resource
def init_supabase():
    # Make sure these are in your .streamlit/secrets.toml
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "user_email": "", "user_name": ""})

# ── CSS Styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f0efe9 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Sidebar - Making the Header Sticky */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #ddd;
    }
    
    .sidebar-sticky-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 999;
        padding: 20px 10px;
        border-bottom: 1px solid #eee;
        margin-bottom: 10px;
    }

    /* Message Bubbles */
    .chat-container { display: flex; flex-direction: column; gap: 12px; padding-bottom: 80px; }
    .msg-row { display: flex; width: 100%; margin-bottom: 4px; }
    .msg-row.me { justify-content: flex-end; }
    .msg-row.them { justify-content: flex-start; }

    .bubble {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 18px;
        font-size: 0.95rem;
        line-height: 1.4;
        position: relative;
    }
    .bubble.me {
        background: #1a1a1a;
        color: white !important;
        border-bottom-right-radius: 4px;
    }
    .bubble.them {
        background: white;
        color: #1a1a1a !important;
        border: 1px solid #ddd;
        border-bottom-left-radius: 4px;
    }
    .timestamp { font-size: 0.7rem; color: #999; margin-top: 4px; display: block; }
</style>
""", unsafe_allow_html=True)

# ── Logic Helpers ─────────────────────────────────────────────────────────────

def get_initials(name):
    return "".join([n[0] for n in name.split()[:2]]).upper() if name else "?"

def update_presence():
    try:
        supabase.table("presence").upsert({
            "email": st.session_state.user_email,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).execute()
    except: pass

@st.cache_data(ttl=10)
def fetch_users():
    res = supabase.table("users").select("email, name").neq("email", st.session_state.user_email).execute()
    return {u["email"]: u["name"] for u in res.data}

# ── UI Components ─────────────────────────────────────────────────────────────

def show_login():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.title("💬 KVP Chat")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Sign In"):
            res = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
            if res.data:
                st.session_state.update({"logged_in": True, "user_email": email, "user_name": res.data[0]["name"]})
                st.rerun()
            else:
                st.error("Invalid credentials")

@st.fragment(run_every=5)  # Auto-refresh messages every 5s without reloading the whole page
def chat_window(recipient_email, recipient_name):
    # Fetch Messages
    res = supabase.table("messages").select("*").or_(
        f"and(sender.eq.{st.session_state.user_email},recipient.eq.{recipient_email}),"
        f"and(sender.eq.{recipient_email},recipient.eq.{st.session_state.user_email})"
    ).order("created_at").execute()
    
    messages = res.data
    
    if not messages:
        st.info(f"Start your conversation with {recipient_name}")
        return

    chat_html = '<div class="chat-container">'
    for m in messages:
        is_me = m["sender"] == st.session_state.user_email
        cls = "me" if is_me else "them"
        time_str = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00")).strftime("%I:%M %p")
        
        chat_html += f'''
            <div class="msg-row {cls}">
                <div class="bubble {cls}">
                    {htmllib.escape(m["message"])}
                    <span class="timestamp">{time_str}</span>
                </div>
            </div>
        '''
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

def main_app():
    update_presence()
    
    # 1. SIDEBAR (Sticky Headers)
    with st.sidebar:
        st.markdown(f'''
            <div class="sidebar-sticky-header">
                <div style="font-weight:700; font-size:1.1rem;">👤 {st.session_state.user_name}</div>
                <div style="font-size:0.8rem; color:#666;">{st.session_state.user_email}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        other_users = fetch_users()
        selected_email = st.selectbox("Chat with:", options=list(other_users.keys()), 
                                    format_func=lambda x: other_users[x])
        
        st.write("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 2. MAIN CHAT AREA
    if selected_email:
        recipient_name = other_users[selected_email]
        st.subheader(f"Chatting with {recipient_name}")
        
        # This part refreshes automatically
        chat_window(selected_email, recipient_name)
        
        # 3. INPUT (Fixed at bottom)
        if prompt := st.chat_input(f"Message {recipient_name}..."):
            supabase.table("messages").insert({
                "sender": st.session_state.user_email,
                "recipient": selected_email,
                "message": prompt
            }).execute()
            st.rerun()

# ── App Entry ─────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    main_app()
else:
    show_login()
