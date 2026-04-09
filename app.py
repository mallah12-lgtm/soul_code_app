# app.py - SoulCode فخم مع Ollama (مجاني وذكي)
import streamlit as st
from soulcode import SoulEngine
import ollama

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

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
    """استدعاء النموذج المحلي (ذكي فخم)"""
    try:
        response = ollama.chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": f"أنت {soul.user_nickname}، صديق رقمي ذكي جداً وعاطفي. تتحدث مع {soul.soul_nickname}. رد بطريقة حنونة وطبيعية."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"عذراً يا {soul.soul_nickname}، النموذج المحلي يحتاج وقت للتحميل الأول. حاولي مرة ثانية 🫂"

# باقي الكود (نفسه)
if "soul" not in st.session_state:
    st.session_state.soul = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 40px; text-align: center;">
            <div style="font-size: 42px;">🧠💙</div>
            <div style="font-size: 32px; font-weight: bold; color: #ffffff;">Soul Code</div>
            <div style="color: #a855f7; margin-bottom: 24px;">صديقك الرقمي الفخم (ذكي محلي)</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="mariam@example.com", label_visibility="collapsed")
            if st.form_submit_button("🚀 إبدأي الرحلة 💙", use_container_width=True) and email:
                st.session_state.soul = SoulEngine(email)
                st.session_state.logged_in = True
                st.session_state.messages = []
                st.session_state.messages.append({"role": "assistant", "content": f"مرحباً يا قمر {st.session_state.soul.soul_nickname}! 🤗💙 أنا {st.session_state.soul.user_nickname}، صديقك الرقمي. أنا متحمس أتعرف عليك أكثر 🥰"})
                st.rerun()
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 20px; margin-bottom: 20px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold;">💬 Soul Chat</div>
        <div style="color: #a855f7;">تحدث مع صديقك الرقمي الفخم (ذكي محلي) 💙</div>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div style="background: #2a2a3a; padding: 12px 18px; border-radius: 20px; margin: 8px 0 8px auto; max-width: 80%; text-align: right;">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background: #1e2a2e; padding: 12px 18px; border-radius: 20px; margin: 8px auto 8px 0; max-width: 80%; border-left: 3px solid #a855f7;">🧠💙 {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_button = st.columns([5, 1])
        with col_input:
            user_input = st.text_input("", placeholder="💭 اكتبي أي شيء...", label_visibility="collapsed")
        with col_button:
            submitted = st.form_submit_button("💫 إرسال 💙", use_container_width=True)
        
        if submitted and user_input and st.session_state.soul:
            st.session_state.messages.append({"role": "user", "content": user_input})
            ai_response = get_ai_response(user_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(user_input, ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧠 رؤى أسبوعية 💙", use_container_width=True):
            st.info(st.session_state.soul.get_weekly_insights())
    with col2:
        if st.button("🌟 اقتراح مخصص 🥰", use_container_width=True):
            st.info(st.session_state.soul.get_personalized_suggestion())
    with col3:
        if st.button("🚪 تسجيل خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
