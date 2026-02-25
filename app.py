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

st.markdown("""
<style>
/* Clean white theme */
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #f9f9f9 !important;
}

[data-testid="stHeader"] { background: #ffffff !important; }
footer, #MainMenu { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #eeeeee !important;
}

/* All text black */
p, span, label, div, h1, h2, h3 { color: #111111 !important; }

/* Inputs */
.stTextInput > label { color: #555 !important; font-size: 0.8rem !important; }
.stTextInput input {
    background: #ffffff !important;
    color: #111 !important;
    border: 1.5px solid #ddd !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus {
    border-color: #999 !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: #bbb !important; }

/* Buttons */
div.stButton > button {
    background: #111111 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    font-size: 0.95rem !important;
}
div.stButton > button:hover { background: #333 !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #ddd !important;
    border-radius: 8px !important;
    color: #111 !important;
}
[data-baseweb="select"] * { color: #111 !important; background: #fff !important; }
[role="option"]:hover { background: #f5f5f5 !important; }

/* Chat input */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1.5px solid #ddd !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    color: #111 !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #bbb !important; }
[data-testid="stChatInput"] button {
    background: #111 !important;
    border-radius: 8px !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
}
.stChatMessage p { color: #111 !important; font-size: 0.95rem !important; }

/* Bottom input area */
[data-testid="stBottom"] {
    background: #f9f9f9 !important;
    border-top: 1px solid #eee !important;
    padding: 0.8rem 1rem !important;
}
</style>
""", unsafe_allow_html=True)


def login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 💬 KVP Chat")
    st.markdown("Private & secure messaging")
    st.markdown("---")

    email = st.text_input("Email", placeholder="you@example.com")
    pwd   = st.text_input("Password", placeholder="••••••••", type="password")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Sign In"):
        if not email or not pwd:
            st.warning("Please enter email and password.")
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


def chat():
    # Load other users
    try:
        res = supabase.table("users").select("email, name") \
            .neq("email", st.session_state.user_email).execute()
        other_users = {u["email"]: u["name"] for u in res.data}
    except Exception:
        other_users = {}

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(st.session_state.user_email)
        st.markdown("---")

        st.markdown("**Chat with**")
        if not other_users:
            st.warning("No other users found.")
            selected_recipient = None
        else:
            selected_recipient = st.selectbox(
                "Select user",
                options=list(other_users.keys()),
                format_func=lambda x: other_users[x]
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

    recipient_name = other_users[selected_recipient]

    st.markdown(f"### 💬 {recipient_name}")
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
        st.markdown(f"<div style='text-align:center;color:#bbb;'>👋 Say hello to {recipient_name}!</div>", unsafe_allow_html=True)
    else:
        for msg in messages:
            role = "user" if msg["sender"] == st.session_state.user_email else "assistant"
            with st.chat_message(role):
                st.write(msg["message"])

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

    # Auto refresh every 3 seconds
    time.sleep(3)
    st.rerun()


if not st.session_state.logged_in:
    login()
else:
    chat()
