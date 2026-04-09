import streamlit as st
from soulcode import SoulEngine
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Soul Code AI", page_icon="🧠", layout="wide")

# --- إعداد جيميناي (GEMINI CONFIG) ---
# تم وضع مفتاحك هنا مباشرة
GOOGLE_API_KEY = "AIzaSyCeT1nqiYIAU4AsItjfpXnAqCB1KPotz3s" 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CSS لتنسيق الواجهة بشكل احترافي ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { 
        background: #262730; 
        padding: 15px; 
        border-radius: 15px; 
        margin: 10px 0; 
        text-align: right; 
        border-right: 5px solid #6366f1;
        float: right;
        width: 80%;
    }
    .ai-box { 
        background: #1e2a2e; 
        padding: 15px; 
        border-radius: 15px; 
        margin: 10px 0; 
        border-left: 5px solid #a855f7;
        float: left;
        width: 80%;
    }
    .stButton>button { width: 100%; border-radius: 20px; background: #6366f1; color: white; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # صياغة الطلب لجيميناي ليعرف هويته من ملف soulcode
        prompt = f"""
        أنت الآن تلعب دور {soul.soul_nickname}.
        صديقك المفضل هو {soul.user_nickname}.
        تعليماتك: رد بالعربية بأسلوب ودود جداً، كن حنوناً وذكياً. 
        اجعل الردود قصيرة ومريحة.
        رسالة المستخدم الحالية: {user_message}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطأ في الاتصال بالسحابة: {e}"

# --- منطق البرنامج ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🧠 Soul Code - مدعوم بـ Gemini")
    email = st.text_input("أدخلي بريدكِ الإلكتروني للبدء:")
    if st.button("فتح بوابة الروح ✨"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    st.write(f"### مرحبا بكِ، {st.session_state.soul.user_nickname} ✨")
    
    # عرض الشات
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            style = "user-box" if msg["role"] == "user" else "ai-box"
            st.markdown(f'<div class="{style}">{msg["content"]}</div><div style="clear:both;"></div>', unsafe_allow_html=True)

    # حقل الإدخال في الأسفل
    with st.form("chat_input", clear_on_submit=True):
        u_input = st.text_input("اكتبي شيئاً لـ Soul Code..")
        if st.form_submit_button("إرسال ✨") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            
            with st.spinner("Soul Code يفكر..."):
                ans = get_ai_response(u_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(u_input, ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()

    # أزرار التحكم
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 إحصائياتي"):
            st.toast(st.session_state.soul.get_weekly_insights())
    with col2:
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()
