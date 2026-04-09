# app.py - SoulCode فخم مع DeepSeek API
import streamlit as st
from soulcode import SoulEngine
from openai import OpenAI

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# إعداد DeepSeek API
DEEPSEEK_API_KEY = "sk-555831961d8045cebfb61dffd95ba8df"  # مفتاحك الخاص
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

st.markdown("""
<style>
:root { color-scheme: dark only !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%) !important; }
p, h1, h2, h3, label, div { color: #e8e8f0 !important; }
.stTextInput > div > div > input { background-color: #1e1e2a !important; color: white !important; }
.stButton > button { background: linear-gradient(135deg, #a855f7, #6366f1) !important; color: white !important; border-radius: 25px !important; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    # تحضير السياق من الذاكرة
    context = f"""
    أنت {soul.user_nickname}، صديق رقمي ذكي جداً وعاطفي.
    المستخدم اسمه {soul.soul_nickname}.
    """

    # إرسال الرسالة إلى DeepSeek API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ],
            temperature=0.9,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"عذراً يا {soul.soul_nickname}، عندي خطأ تقني: {e}"

# باقي كود Streamlit
if "soul" not in st.session_state:
    st.session_state.soul = None
    st.session_state.messages = []
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔐 مرحباً بك في Soul Code")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        if st.form_submit_button("دخول"):
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages = []
            welcome = st.session_state.soul.get_welcome_message()
            st.session_state.messages.append({"role": "assistant", "content": welcome})
            st.rerun()
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div style="background:#2a2a3a;padding:10px;border-radius:20px;margin:5px 0 5px auto;max-width:70%;text-align:right">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e2a2e;padding:10px;border-radius:20px;margin:5px auto 5px 0;max-width:70%;border-left:3px solid #a855f7">🧠 {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="قولي أي شيء...", label_visibility="collapsed")
        if st.form_submit_button("💫 إرسال"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                ai_response = get_ai_response(user_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(user_input, ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
