import streamlit as st
from soulcode import SoulEngine
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Soul Code AI", page_icon="🧠")

# --- أهم خطوة: المفتاح الجديد ---
# أنشئي مفتاحاً جديداً من AI Studio وضعيه هنا مكان النجوم
GOOGLE_API_KEY = "AIzaSyAR0iwF5_S3PKrMwvfq9StZrMS02t1Hlss" 

genai.configure(api_key=GOOGLE_API_KEY)

# --- تنسيق الواجهة ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { background: #262730; padding: 15px; border-radius: 15px; margin: 10px 0; text-align: right; border-right: 5px solid #6366f1; clear: both; }
    .ai-box { background: #1e2a2e; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 5px solid #a855f7; clear: both; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # استخدام الموديل الأكثر استقراراً ومجانية
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"أنت {soul.soul_nickname}، صديق ذكي لـ {soul.user_nickname}. رد بالعربية باختصار: {user_message}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"💙 الروح مشغولة قليلاً، جربي ثانية! (السبب: {str(e)[:50]})"

# --- منطق البرنامج ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🧠 Soul Code AI")
    email = st.text_input("أدخلي بريدكِ الإلكتروني:")
    if st.button("دخول ✨"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    st.write(f"### متصلة الآن مع Soul Code ✨")
    for msg in st.session_state.messages:
        style = "user-box" if msg["role"] == "user" else "ai-box"
        st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat", clear_on_submit=True):
        u_input = st.text_input("تحدثي معي..")
        if st.form_submit_button("إرسال") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            ans = get_ai_response(u_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(u_input, ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
