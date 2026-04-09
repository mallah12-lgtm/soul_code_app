import streamlit as st
from soulcode import SoulEngine
import ollama

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# CSS التصميم الاحترافي
st.markdown("""
<style>
    .stApp { background: #0a0a0f; color: #e8e8f0; }
    .user-msg { background: #2a2a3a; padding: 15px; border-radius: 15px; margin: 10px 0; text-align: right; border-right: 4px solid #6366f1; }
    .ai-msg { background: #1e2a2e; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 4px solid #a855f7; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # استخدام الموديل الخفيف الذي حملته بنجاح
        response = ollama.chat(
            model="qwen2.5:0.5b", 
            messages=[
                {"role": "system", "content": f"أنت {soul.soul_nickname}، صديق ذكي وحنون. اسم المستخدم {soul.user_nickname}. رد بالعربية بأسلوب جميل."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"عذراً، حدث خطأ في المحرك: {e}"

# إدارة الجلسة
if "soul" not in st.session_state: st.session_state.soul = None
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧠 Soul Code")
    email = st.text_input("أدخل بريدك الإلكتروني:")
    if st.button("إبدأ الرحلة 🚀"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    st.subheader(f"💬 دردشة {st.session_state.soul.soul_nickname}")
    
    # عرض الرسائل بتنسيق جميل
    for msg in st.session_state.messages:
        role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # نموذج الإرسال
    with st.form("chat_input", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            u_input = st.text_input("", placeholder="اكتب هنا...", label_visibility="collapsed")
        with col_btn:
            if st.form_submit_button("إرسال 💫") and u_input:
                st.session_state.messages.append({"role": "user", "content": u_input})
                with st.spinner("Soul Code يفكر..."):
                    ans = get_ai_response(u_input, st.session_state.soul)
                    st.session_state.soul.learn_from_conversation(u_input, ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()

    # الأزرار الإضافية
    cols = st.columns(3)
    with cols[0]:
        if st.button("📊 إحصائياتي"): st.info(st.session_state.soul.get_weekly_insights())
    with cols[1]:
        if st.button("🌟 اقتراح"): st.info(st.session_state.soul.get_personalized_suggestion())
    with cols[2]:
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()
