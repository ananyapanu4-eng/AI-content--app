import streamlit as st
import pandas as pd
import os
from datetime import datetime
from groq import Groq
import hashlib


# 🔐 LOAD API
os.getenv("GROQ_API_KEY")()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
# 🎨 PAGE SETTINGS
st.set_page_config(page_title="AI Marketing Pro", layout="wide")

# 🎨 UI DESIGN
st.markdown("""
         <style>
    .main {background-color: #0E1117; color: white;}
    .stTextInput>div>div>input {background-color: #262730; color: white;}
    .stButton>button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
}
.stTabs [data-baseweb="tab"] {font-size: 18px;}
</style>
""", unsafe_allow_html=True)

# 🔐 LOGIN STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🔐 PASSWORD HASH
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🔐 LOAD USERS
def load_users():
    try:
        return pd.read_csv("users.csv")
    except:
        return pd.DataFrame(columns=["email", "password"])

# 🔐 SAVE USER
def save_user(email, password):
    df = load_users()

    # prevent duplicate users
    if email in df["email"].values:
        st.warning("⚠️ Email already registered")
        return

    new_user = pd.DataFrame([{
        "email": email,
        "password": hash_password(password)
    }])

    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv("users.csv", index=False)

# 🔐 CHECK LOGIN
def check_login(email, password):
    df = load_users()
    hashed = hash_password(password)
    user = df[(df["email"] == email) & (df["password"] == hashed)]
    return not user.empty

# 🔐 LOGIN UI
def login():
    st.markdown("## 🔐 Welcome Back")
    choice = st.radio("Select", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Create Account"):
            if email and password:
                save_user(email, password)
                st.success("✅ Account Created!")
            else:
                st.warning("⚠️ Enter email & password")

    else:
        if st.button("Login"):
            if check_login(email, password):
                st.session_state.logged_in = True
                st.success("✅ Login Successful!")
            else:
                st.error("❌ Invalid Email or Password")

# 🚫 STOP IF NOT LOGGED IN
if not st.session_state.logged_in:
    login()
    st.stop()

# 🚀 HEADER
st.markdown("""
# 🚀 AI Marketing Pro Dashboard
### 💼 Smart Tools for Digital Growth
""")
st.divider()

# 📌 TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Instagram AI",
    "🤖 Chatbot",
    "📋 Leads",
    "📊 History"
])

# 📸 INSTAGRAM AI
with tab1:
    st.subheader("📸 Instagram AI Generator")

    topic = st.text_input("💡 Enter your product/topic")

    if st.button("✨ Generate Marketing Content"):
        if topic:
            st.info("⏳ Generating...")

            prompt = f"""
Create:
- Instagram caption with emojis
- 15 hashtags
- 3 reel ideas
- Caption in English and Kannada
Topic: {topic}
"""

            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            output = res.choices[0].message.content

            st.success("✅ Done!")
            st.markdown(output)

            with open("content.txt", "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.now()} ---\n{output}\n")
        else:
            st.warning("⚠️ Enter topic")

# 🤖 CHATBOT
with tab2:
    st.subheader("🤖 AI Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask something")

    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.chat_history
            )

            reply = res.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**👤 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")

# 📋 LEADS
with tab3:
    st.subheader("📋 Lead Collection")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    if st.button("Save Lead"):
        if name and email:
            df = pd.DataFrame([{
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Time": datetime.now()
            }])

            df.to_csv("leads.csv", mode='a', header=not os.path.exists("leads.csv"), index=False)
            st.success("✅ Saved!")

        else:
            st.warning("⚠️ Enter Name & Email")

    if os.path.exists("leads.csv"):
        with open("leads.csv", "r") as f:
            st.download_button("⬇️ Download Leads", f, "leads.csv")

# 📊 HISTORY
with tab4:
    st.subheader("📊 Content History")

    if os.path.exists("content.txt"):
        with open("content.txt", "r", encoding="utf-8") as f:
           st.text(f.read())
    else:
        st.warning("No history yet")
