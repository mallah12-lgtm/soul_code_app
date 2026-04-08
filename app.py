# app.py - SoulCode واجهة Dashboard عصري (ثابتة الألوان)
import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# ========== CSS يجبر الوضع الداكن ويلغي تأثير النظام ==========
st.markdown("""
<style>
    /* إلغاء تأثير الوضع الداكن/الفاتح من المتصفح والنظام */
    :root {
        color-scheme: dark only !important;
    }
    
    /* تجاوز كل ألوان النظام */
    html, body {
        background-color: #0a0a0f !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%) !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #0a0a0f !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0a0a0f !important;
        border-right: 1px solid #1e1e2e !important;
    }
    
    /* كل النصوص باللون الفاتح */
    p, h1, h2, h3, h4, h5, h6, label, span, div, .stMarkdown {
        color: #e8e8f0 !important;
    }
    
    /* حقول الإدخال */
    .stTextInput > div > div > input {
        background-color: #1e1e2a !important;
        color: #ffffff !important;
        border: 1px solid #3a3a4a !important;
        border-radius: 12px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 2px rgba(168,85,247,0.2) !important;
    }
    
    /* الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #a855f7, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(168,85,247,0.3) !important;
    }
    
    /* صناديق المعلومات */
    .stAlert {
        background-color: #1e1e2e !important;
        border: none !important;
        border-radius: 16px !important;
    }
    
    .stAlert > div {
        color: #e8e8f0 !important;
    }
    
    /* المقاييس */
    [data-testid="stMetric"] {
        background-color: #1a1a25 !important;
        border-radius: 16px !important;
        padding: 10px !important;
    }
    
    [data-testid="stMetric"] label {
        color: #a855f7 !important;
    }
    
    /* إخفاء العناصر الافتراضية */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* مسافات */
    .block-container {
        padding-top: 20px !important;
        padding-bottom: 80px !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== CSS للواجهة العصري ==========
st.markdown("""
<style>
    /* البطاقات */
    .welcome-card {
        background: linear-gradient(135deg, #1e1e2e, #161622);
        border-radius: 28px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .welcome-title {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .welcome-sub {
        color: #a855f7;
        font-size: 14px;
    }
    
    /* بطاقات الميزات */
    .feature-card {
        background: rgba(30, 30, 46, 0.6);
        border-radius: 24px;
        padding: 20px;
        transition: all 0.2s;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 16px;
    }
    .feature-card:hover {
        background: rgba(40, 40, 56, 0.8);
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 36px;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 16px;
    }
    
    /* رسائل المحادثة */
    .chat-message-user {
        background: linear-gradient(135deg, #2a2a3a, #222232);
        color: #e0e0e8;
        padding: 12px 18px;
        border-radius: 20px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        text-align: right;
    }
    .chat-message-ai {
        background: linear-gradient(135deg, #1e2a2e, #162024);
        color: #c9e2e8;
        padding: 12px 18px;
        border-radius: 20px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        border-left: 3px solid #a855f7;
    }
    
    /* الشريط العلوي */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: rgba(18, 18, 30, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
    }
    .logo {
        font-size: 24px;
        font-weight: bold;
        background: linear-gradient(135deg, #a855f7, #6366f1);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .logo-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 4px;
    }
    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.05);
        padding: 8px 16px;
        border-radius: 40px;
    }
    .user-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #a855f7, #6366f1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ========== تهيئة حالة الجلسة ==========
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "soul" not in st.session_state:
    st.session_state.soul = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== دالة الردود الذكية ==========
def get_smart_response(user_message, soul):
    analysis = soul.analyze_message(user_message)
    soul.save_conversation(user_message, "", analysis["topic"], analysis["sentiment"])
    
    responses = {
        r"مرحبا|سلام|اهلا": [f"مرحباً {soul.soul_nickname}! 🤗 كيف تشعر اليوم؟"],
        r"كيف حالك": [f"أنا بخير {soul.soul_nickname}! شكراً لسؤالك 💙"],
        r"بخير|تمام": [f"الحمد لله! فرحتني {soul.soul_nickname} 🎉"],
        r"حزين|تعبت": [f"أنا آسف {soul.soul_nickname} 🫂 أنا هنا معك."],
    }
    
    for pattern, response_list in responses.items():
        if re.search(pattern, user_message, re.IGNORECASE):
            return random.choice(response_list)
    
    return f"أنا هنا أتعلم منك {soul.soul_nickname}! 💙 علميني أكثر عن نفسك."

# ========== الشاشات ==========
def show_home():
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-title">Nurture Your Essence,<br>Decode Your Self</div>
        <div class="welcome-sub">✦ Discover Your Path</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧘</div>
            <div class="feature-title">Deep Meditation</div>
            <div class="feature-desc">رحلة تأمل عميق لفهم ذاتك</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <div class="feature-title">Wisdom Guide</div>
            <div class="feature-desc">بوصلة الحكمة لاتخاذ قراراتك</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.soul:
        summary = st.session_state.soul.get_user_summary()
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(255,255,255,0.03); border-radius: 20px; padding: 12px;">
                <div style="font-size: 28px; font-weight: bold;">{summary['total_conversations']}</div>
                <div style="font-size: 12px; color: #6b7280;">Conversations</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(255,255,255,0.03); border-radius: 20px; padding: 12px;">
                <div style="font-size: 28px; font-weight: bold;">{summary['interests_count']}</div>
                <div style="font-size: 12px; color: #6b7280;">Interests</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(255,255,255,0.03); border-radius: 20px; padding: 12px;">
                <div style="font-size: 28px; font-weight: bold;">{len(st.session_state.messages)//2}</div>
                <div style="font-size: 12px; color: #6b7280;">Sessions</div>
            </div>
            """, unsafe_allow_html=True)

def show_chat():
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-title">💬 Soul Chat</div>
        <div class="welcome-sub">تحدث مع صديقك الرقمي</div>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-ai">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="💭 اكتب رسالتك هنا...", label_visibility="collapsed")
        submitted = st.form_submit_button("💫 Send", use_container_width=True)
        
        if submitted and user_input and st.session_state.soul:
            st.session_state.messages.append({"role": "user", "content": user_input})
            ai_response = get_smart_response(user_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(user_input, ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()

def show_insights():
    if st.session_state.soul:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">📊 Insights</div>
            <div class="welcome-sub">رؤى عن شخصيتك وتطورك</div>
        </div>
        """, unsafe_allow_html=True)
        
        summary = st.session_state.soul.get_user_summary()
        
        if summary.get("dominant_emotion"):
            emotion_icon = "😊" if summary["dominant_emotion"] == "positive" else "🫂"
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{emotion_icon}</div>
                <div class="feature-title">Dominant Emotion</div>
                <div class="feature-desc">مشاعرك الغالبة هي: {summary['dominant_emotion']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if summary["top_interests"]:
            interests_text = ", ".join([f"{i[0]}" for i in summary["top_interests"]])
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Your Interests</div>
                <div class="feature-desc">{interests_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔮 Show Weekly Insights", use_container_width=True):
            st.info(st.session_state.soul.get_weekly_insights())
    else:
        st.info("✨ سجل الدخول أولاً لترى رؤى شخصيتك")

def show_profile():
    if st.session_state.soul:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">👤 Profile</div>
            <div class="welcome-sub">إعداداتك الشخصية</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("🏷️ Your Name", value=st.session_state.soul.soul_nickname)
            if st.button("💫 Update Name"):
                st.session_state.soul.set_soul_nickname(new_name)
                st.success("✅ Updated!")
        
        with col2:
            new_soul = st.text_input("🤖 Soul Name", value=st.session_state.soul.user_nickname)
            if st.button("🔄 Update Soul Name"):
                st.session_state.soul.set_user_nickname(new_soul)
                st.success("✅ Updated!")
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("✨ سجل الدخول أولاً")

# ========== الشريط العلوي ==========
if st.session_state.logged_in and st.session_state.soul:
    first_letter = st.session_state.soul.soul_nickname[0] if st.session_state.soul.soul_nickname else "S"
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="logo">🧠 SoulCode</div>
            <div class="logo-sub">Nurture Your Essence, Decode Your Self</div>
        </div>
        <div class="user-info">
            <div class="user-avatar">{first_letter}</div>
            <span>{st.session_state.soul.soul_nickname}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="top-bar">
        <div>
            <div class="logo">🧠 SoulCode</div>
            <div class="logo-sub">Nurture Your Essence, Decode Your Self</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== المحتوى الرئيسي ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="welcome-card" style="text-align: center; margin-top: 40px;">
            <div class="welcome-title" style="font-size: 32px;">✨ Welcome Back</div>
            <div class="welcome-sub">Enter your email to continue your journey</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="sarah@example.com", label_visibility="collapsed")
            submitted = st.form_submit_button("🚀 Start Journey", use_container_width=True)
            
            if submitted and email:
                st.session_state.soul = SoulEngine(email)
                st.session_state.logged_in = True
                st.session_state.messages = []
                welcome = st.session_state.soul.get_welcome_message()
                st.session_state.messages.append({"role": "assistant", "content": welcome})
                st.rerun()
else:
    # عرض الصفحة المختارة
    if st.session_state.current_page == "home":
        show_home()
    elif st.session_state.current_page == "chat":
        show_chat()
    elif st.session_state.current_page == "insights":
        show_insights()
    elif st.session_state.current_page == "profile":
        show_profile()
    
    # ========== شريط التنقل السفلي ==========
    st.markdown("---")
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    with col_nav1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with col_nav2:
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    with col_nav3:
        if st.button("📊 Insights", use_container_width=True):
            st.session_state.current_page = "insights"
            st.rerun()
    with col_nav4:
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
