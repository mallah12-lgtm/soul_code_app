import streamlit as st
from soulcode import SoulEngine
import ollama

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# تصميم الواجهة
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .user-box { background: #262730; padding: 15px; border-radius: 15px; margin: 5px; text-align: right; }
    .ai-box { background: #1e2a2e; padding: 15px; border-radius: 15px; margin: 5px; border-left: 5px solid #a855f7; }
</style>
""", unsafe_allow_html=True)

def get_ai_response(user_message, soul):
    try:
        # هنا المحرك الخفيف جداً
        response = ollama.chat(
            model="qwen2.5:0.5b", 
            messages=[
                {"role": "system", "content": f"أنت {soul.soul_nickname}، صديق لطيف. ردي بالعربي باختصار وحنان."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return "المعذرة، المحرك يحتاج لحظة للراحة.. جربي مرة أخرى."

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🧠 Soul Code")
    email = st.text_input("أدخلِ بريدكِ الإلكتروني:")
    if st.button("دخول ✨"):
        if email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
            st.rerun()
else:
    for msg in st.session_state.messages:
        style = "user-box" if msg["role"] == "user" else "ai-box"
        st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_input", clear_on_submit=True):
        u_input = st.text_input("اكتبي شيئاً..")
        if st.form_submit_button("إرسال") and u_input:
            st.session_state.messages.append({"role": "user", "content": u_input})
            # إظهار علامة تحميل بسيطة
            with st.spinner("يفكر..."):
                ans = get_ai_response(u_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(u_input, ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
