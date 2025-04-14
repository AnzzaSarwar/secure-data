import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import base64

# 🔐 Generate key from passkey
def generate_key(passkey):
    return base64.urlsafe_b64encode(hashlib.sha256(passkey.encode()).digest())

# 🔐 Encrypt data
def encrypt_data(data, passkey):
    key = generate_key(passkey)
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

# 🔓 Decrypt data
def decrypt_data(token, passkey):
    try:
        key = generate_key(passkey)
        fernet = Fernet(key)
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        return "Invalid passkey or corrupted data."

# 🔐 Hash password for storing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 💾 Dummy database using session state
if "users" not in st.session_state:
    st.session_state["users"] = {}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "vault" not in st.session_state:
    st.session_state["vault"] = {}

# 🎨 Custom Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #000000, #001f3f);
        background-attachment: fixed;
        color: white !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Inputs style */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #111827;
        color: #ffffff;
        border-radius: 8px;
        padding: 0.5em;
        border: 1px solid #374151;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(to right, #00FFFF, #8A2BE2);
        color: white;
        font-weight: bold;
        padding: 0.6em 1.2em;
        border: none;
        border-radius: 12px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 10px rgba(0,255,255,0.4), 0 0 20px rgba(138,43,226,0.4);
    }

    .stButton>button:hover {
        background: linear-gradient(to right, #ffffff, #80dfff);
        color: #111827;
        font-weight: 900;
        box-shadow: 0 0 20px rgba(0,255,255,0.8), 0 0 35px rgba(138,43,226,0.8);
        transform: scale(1.05);
    }

    /* Username text color */
    .stTextInput input {
        color: white !important;
    }

    .stTextInput label {
        color: white !important;
        font-weight: bold;
    }

    .stTextArea textarea {
        color: black !important;
    }

    .stTextArea label {
        color: white !important;
        font-weight: bold;
    }

    /* Tabs and text color fix */
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        color: white;
        border-radius: 6px;
        padding: 6px 10px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #334155;
    }

    /* Bold username */
    .stSidebar .stTextInput input {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 📌 Sidebar
with st.sidebar:
    if st.session_state["logged_in"]:
        st.success(f"👋 Welcome, {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()

        st.markdown("### 🧭 Navigate")
        page = st.radio("Choose Page", ["🔐 Store Data", "🔍 Retrieve Data"])
    else:
        page = None

# 🔑 Auth logic
def login_page():
    st.title("🔐 Login or Register")
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            hashed = hash_password(password)
            if st.session_state["users"].get(username) == hashed:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if new_user in st.session_state["users"]:
                st.warning("User already exists.")
            else:
                st.session_state["users"][new_user] = hash_password(new_pass)
                st.success("User registered successfully!")

# 🚀 Main App
if st.session_state["logged_in"]:
    st.title("🔐 Secure Data Vault")

    if page == "🔐 Store Data":
        st.subheader("📦 Store Data")
        secret = st.text_area("🔒 Enter data to encrypt:")
        key_input = st.text_input("🔑 Set a passkey:", type="password")

        if st.button("Encrypt & Save"):
            if secret and key_input:
                encrypted = encrypt_data(secret, key_input)
                user = st.session_state["username"]
                st.session_state["vault"].setdefault(user, []).append(encrypted)
                st.success("✅ Data encrypted and saved!")
            else:
                st.warning("Please enter both data and a passkey.")

    elif page == "🔍 Retrieve Data":
        st.subheader("🔓 Retrieve Data")
        user = st.session_state["username"]
        stored_data = st.session_state["vault"].get(user, [])

        if stored_data:
            selected = st.selectbox("📁 Select Encrypted Data", stored_data)
            passkey = st.text_input("🔑 Enter your passkey to decrypt:", type="password")
            if st.button("Decrypt"):
                decrypted = decrypt_data(selected, passkey)
                st.code(decrypted)
        else:
            st.info("No data stored yet.")
else:
    login_page()
st.caption("Built with 💖 by Anza bajwa | Powered by Streamlit")
