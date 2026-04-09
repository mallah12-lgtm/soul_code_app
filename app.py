import streamlit as st
from soulcode import SoulEngine
import ollama

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# تصميم الواجهة (CSS)
st.markdown("""
<style>
    .stApp { background: #0e1117; color: white; }
    .user-msg { background: #2a2a3a; padding: 15px; border-radius: 15px; margin: 10px 0; text-align: right; }
    .ai-msg { background: #1e2a2e; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 4px solid #a855f7; }
</style>
""", unsafe_allow_html=True)

# دالة التواصل مع Ollama
def get_ai_response(user_message, soul):
    try:
        # ملاحظة: تأكد من اسم الموديل qwen:8b أو الموديل الذي حملته
        response = ollama.chat(
            model="qwen:8b", 
            messages=[
                {"role": "system", "content": f"أنت {soul.soul_nickname}، صديق ذكي وعاطفي. اسم المستخدم هو {soul.user_nickname}. رد بالعربية بأسلوب ودود وقصير."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"خطأ في الاتصال بـ Ollama: {e}"

# إدارة الحالة (Session State)
if "soul" not in st.session_state: st.session_state.soul = None
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# شاشة تسجيل الدخول
if not st.session_state.logged_in:
    st.title("🧠 Soul Code")
    email = st.text_input("أدخل بريدك الإلكتروني للبدء:")
    if st.button("دخول"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.rerun()
else:
    # واجهة الشات
    st.subheader(f"💬 مرحباً {st.session_state.soul.user_nickname}")
    
    # عرض الرسائل
    for msg in st.session_state.messages:
        div_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # حقل الإدخال
    with st.form("chat", clear_on_submit=True):
        u_input = st.text_input("اكتب رسالتك هنا...")
        if st.form_submit_button("إرسال") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            ans = get_ai_response(u_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(u_input, ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()

    # أزرار الإحصائيات
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 إحصائياتي"):
            st.toast(st.session_state.soul.get_weekly_insights())
    with col2:
        if st.button("🌟 اقتراح لي"):
            st.info(st.session_state.soul.get_personalized_suggestion())
