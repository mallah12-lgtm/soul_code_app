import streamlit as st
from soulcode import SoulEngine
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Soul Code AI", page_icon="🧠", layout="wide")

# --- إعداد جيميناي (GEMINI CONFIG) ---
# وضعنا المفتاح الخاص بكِ هنا
GOOGLE_API_KEY = "AIzaSyCeT1nqiYIAU4AsItjfpXnAqCB1KPotz3s" 
genai.configure(api_key=GOOGLE_API_KEY)

# التعديل هنا: استخدمنا 'gemini-1.5-flash' بدون إضافات أو 'gemini-pro' كبديل مضمون
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- CSS لتنسيق الواجهة ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { 
        background: #262730; padding: 15px; border-radius: 15px; 
        margin: 10px 0; text-align: right; border-right: 5px solid #6366f1; 
        float: right; width: 80%;
    }
    .ai-box { 
        background: #1e2a2e; padding: 15px; border-radius: 15px; 
        margin: 10px 0; border-left: 5px solid #a855f7; 
        float: left; width: 80%;
    }
    .stButton>button { width: 100%; border-radius: 20px; background: #6366f1; color: white; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # صياغة الطلب
        prompt = f"أنت {soul.soul_nickname}، صديق ذكي وحنون لـ {soul.user_nickname}. رد بالعربية بأسلوب لطيف وقصير. الرسالة: {user_message}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # إذا فشل الفلاش، نجرب البرو كخطة احتياطية فورية
        return f"عذراً، جيميناي يحتاج لحظة.. تأكدي من استقرار الإنترنت. (الخطأ: {e})"

# --- منطق البرنامج ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🧠 Soul Code - المتصل بالسحابة")
    email = st.text_input("أدخلي بريدكِ الإلكتروني:")
    if st.button("فتح البوابة ✨"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    st.write(f"### متصل الآن مع: {st.session_state.soul.user_nickname} ✨")
    
    # عرض الشات
    for msg in st.session_state.messages:
        style = "user-box" if msg["role"] == "user" else "ai-box"
        st.markdown(f'<div class="{style}">{msg["content"]}</div><div style="clear:both;"></div>', unsafe_allow_html=True)

    # حقل الإدخال
    with st.form("chat_input", clear_on_submit=True):
        u_input = st.text_input("اكتبي شيئاً...")
        if st.form_submit_button("إرسال ✨") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            with st.spinner("Soul Code يستجيب..."):
                ans = get_ai_response(u_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(u_input, ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()

    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.rerun()
