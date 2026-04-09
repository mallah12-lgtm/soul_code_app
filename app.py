import streamlit as st
from soulcode import SoulEngine
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Soul Code AI", page_icon="🧠", layout="wide")

# --- إعداد جيميناي (GEMINI CONFIG) ---
GOOGLE_API_KEY = "AIzaSyAR0iwF5_S3PKrMwvfq9StZrMS02t1Hlss" 
genai.configure(api_key=GOOGLE_API_KEY)

# دالة ذكية لاختيار الموديل المتاح تلقائياً
def load_best_model():
    available_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    for m in available_models:
        try:
            temp_model = genai.GenerativeModel(m)
            # تجربة وهمية للتأكد أن الموديل يعمل
            return temp_model
        except:
            continue
    return None

model = load_best_model()

# --- تنسيق الواجهة ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { background: #262730; padding: 15px; border-radius: 15px; margin: 10px 0; text-align: right; border-right: 5px solid #6366f1; float: right; width: 80%; clear: both; }
    .ai-box { background: #1e2a2e; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 5px solid #a855f7; float: left; width: 80%; clear: both; }
    .stButton>button { width: 100%; border-radius: 20px; background: #6366f1; color: white; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    if not model:
        return "❌ لم أجد محركاً متاحاً في حسابكِ حالياً. تأكدي من إعدادات API Key."
    try:
        prompt = f"أنت {soul.soul_nickname}، صديق ذكي وحنون لـ {soul.user_nickname}. رد بالعربية بأسلوب لطيف وقصير جداً. الرسالة: {user_message}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"💙 عذراً، جربي إرسال الرسالة مرة أخرى (خطأ بسيط في الشبكة)."

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

    with st.form("chat_input", clear_on_submit=True):
        u_input = st.text_input("تحدثي مع Soul Code..")
        if st.form_submit_button("إرسال ✨") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            with st.spinner("يفكر..."):
                ans = get_ai_response(u_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(u_input, ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()

    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.rerun()
