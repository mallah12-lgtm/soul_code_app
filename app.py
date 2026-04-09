import streamlit as st
from soulcode import SoulEngine
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Soul Code AI", page_icon="🧠", layout="wide")

# --- إعداد جيميناي (GEMINI CONFIG) ---
GOOGLE_API_KEY = "AIzaSyCeT1nqiYIAU4AsItjfpXnAqCB1KPotz3s" 
genai.configure(api_key=GOOGLE_API_KEY)

# الحل لمشكلة 404: كتابة الاسم بشكل مباشر وبسيط
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CSS لتنسيق الواجهة ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { 
        background: #262730; padding: 15px; border-radius: 15px; 
        margin: 10px 0; text-align: right; border-right: 5px solid #6366f1; 
        float: right; width: 85%; clear: both;
    }
    .ai-box { 
        background: #1e2a2e; padding: 15px; border-radius: 15px; 
        margin: 10px 0; border-left: 5px solid #a855f7; 
        float: left; width: 85%; clear: both;
    }
    .stButton>button { width: 100%; border-radius: 20px; background: #6366f1; color: white; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # صياغة الطلب بدقة
        prompt = f"أنت {soul.soul_nickname}، صديق ذكي وحنون لـ {soul.user_nickname}. رد بالعربية بأسلوب لطيف وقصير جداً. الرسالة: {user_message}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # إذا فشل اسم الموديل، هذا الكود سيحاول تجربة الاسم البديل فوراً
        try:
            alt_model = genai.GenerativeModel('gemini-pro')
            response = alt_model.generate_content(user_message)
            return response.text
        except:
            return f"عذراً صديقتي، يبدو أن هناك ضغط على السيرفر، جربي إرسال الرسالة مرة أخرى. 💙"

# --- منطق البرنامج ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🧠 Soul Code AI")
    email = st.text_input("أدخلي بريدكِ الإلكتروني للبدء:")
    if st.button("دخول ✨"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    st.write(f"### متصلة الآن مع Soul Code ✨")
    
    # عرض الشات
    for msg in st.session_state.messages:
        style = "user-box" if msg["role"] == "user" else "ai-box"
        st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)

    # حقل الإدخال
    with st.form("chat_input", clear_on_submit=True):
        u_input = st.text_input("اكتبي رسالتكِ هنا...")
        if st.form_submit_button("إرسال ✨") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            with st.spinner("Soul Code يكتب لكِ..."):
                ans = get_ai_response(u_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(u_input, ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()

    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.rerun()
