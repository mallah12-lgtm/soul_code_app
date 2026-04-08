# app.py - واجهة SoulCode المريحة للعين
import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# ========== واجهة مريحة للعين (Dark Mode + ألوان هادئة) ==========
st.markdown("""
<style>
    /* خلفية داكنة مريحة */
    .stApp {
        background: #0f0f13;
    }
    
    /* تنسيق الحاوية الرئيسية */
    .main > div {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* أنيميشن ناعم للرسائل */
    @keyframes gentleFade {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* رسائل المستخدم */
    .user-message {
        background: linear-gradient(135deg, #1a2a3a 0%, #16212e 100%);
        color: #d4e6f1;
        padding: 12px 18px;
        border-radius: 20px;
        border-bottom-right-radius: 4px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        float: right;
        clear: both;
        animation: gentleFade 0.3s ease;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* رسائل الذكاء الاصطناعي */
    .ai-message {
        background: linear-gradient(135deg, #1e2a2e 0%, #162024 100%);
        color: #c9e2e8;
        padding: 12px 18px;
        border-radius: 20px;
        border-bottom-left-radius: 4px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        float: left;
        clear: both;
        animation: gentleFade 0.3s ease;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border-left: 3px solid #6c5ce7;
    }
    
    /* حاوية الرسائل */
    .chat-container {
        min-height: 400px;
        padding: 20px;
        background: #0a0a0e;
        border-radius: 24px;
        margin-bottom: 20px;
        overflow-y: auto;
    }
    
    /* إخفاء شريط التمرير الافتراضي لـ Streamlit */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #1a1a1e;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #6c5ce7;
        border-radius: 10px;
    }
    
    /* تنسيق حقل الإدخال */
    .stTextInput > div > div > input {
        background: #1a1a20;
        color: #e0e0e0;
        border: 1px solid #2a2a35;
        border-radius: 30px;
        padding: 12px 20px;
        font-size: 15px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6c5ce7;
        box-shadow: 0 0 0 2px rgba(108,92,231,0.2);
    }
    
    /* تنسيق الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #6c5ce7 0%, #a463f5 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(108,92,231,0.3);
    }
    
    /* تنسيق الصناديق الجانبية */
    .settings-box {
        background: #121218;
        border-radius: 24px;
        padding: 20px;
        border: 1px solid #23232e;
        margin-bottom: 20px;
    }
    
    /* تنسيق الـ Expander */
    .streamlit-expanderHeader {
        background: #1a1a22;
        border-radius: 12px;
        color: #d4d4dc;
    }
    
    /* تنسيق الـ Metrics */
    [data-testid="stMetric"] {
        background: #1a1a22;
        border-radius: 16px;
        padding: 12px;
    }
    [data-testid="stMetric"] > div {
        color: #d4d4dc;
    }
    
    /* تنسيق النصوص العامة */
    h1, h2, h3, .stMarkdown {
        color: #e8e8f0;
    }
    
    /* تنسيق الـ Info و Success */
    .stAlert {
        border-radius: 16px;
        border: none;
    }
    .stAlert > div {
        background: #1a1a22;
        color: #c9e2e8;
    }
    
    /* تنسيق التبويبات والأقسام */
    hr {
        border-color: #2a2a35;
    }
    
    /* تنسيق اللوحة الجانبية */
    [data-testid="stSidebar"] {
        background: #0c0c10;
        border-right: 1px solid #1e1e28;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #c0c0d0;
    }
    
    /* العناوين الجانبية */
    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #a463f5;
    }
    
    /* مؤشر الكتابة */
    @keyframes pulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
    .typing-indicator {
        display: inline-block;
        padding: 8px 16px;
        background: #1e2a2e;
        border-radius: 20px;
        font-size: 13px;
        color: #6c5ce7;
        animation: pulse 1.2s ease-in-out infinite;
    }
    
    /* مسح التدفق العائم */
    .clearfix::after {
        content: "";
        clear: both;
        display: table;
    }
</style>

<div class="clearfix"></div>
""", unsafe_allow_html=True)

# العنوان
st.title("🧠 Soul Code")
st.caption("صديقك الرقمي الذي يفهمك - يتعلم ويتذكر ويتطور معك بهدوء")

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

def get_smart_response(user_message, soul):
    st.session_state.conversation_memory.append(f"user: {user_message}")
    if len(st.session_state.conversation_memory) > 20:
        st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
    
    contextual_response = soul.get_contextual_response(user_message)
    if contextual_response:
        st.session_state.conversation_memory.append(f"ai: {contextual_response}")
        return contextual_response
    
    analysis = soul.analyze_message(user_message)
    soul.save_conversation(user_message, "", analysis["topic"], analysis["sentiment"])
    
    for fact in analysis["facts"]:
        soul.learn_fact(fact)
    
    if analysis["topic"] == "ai":
        return f"أنا سعيد لأنك مهتمة بالذكاء الاصطناعي {soul.soul_nickname}! 🎓 أتعلم منك كل يوم. اسأليني أي شيء."
    
    elif analysis["topic"] == "feelings":
        if analysis["sentiment"] == "positive":
            return f"فرحتني فرحتك {soul.soul_nickname}! 🎉 أخبريني أكثر عن سبب سعادتك."
        else:
            return f"أنا هنا معك {soul.soul_nickname} 🫂 تفضلي شاركيني اللي في خاطرك."
    
    elif analysis["topic"] == "dreams":
        return f"أحلامك جميلة {soul.soul_nickname}! ✨ أنا واثق إنك بتقدرين تحققينها. وش أول خطوة؟"
    
    elif analysis["questions"]:
        return f"سؤال جميل {soul.soul_nickname}! 🤔 دعيني أفكر معاك."
    
    else:
        responses = {
            r"مرحبا|سلام|اهلا": [
                f"مرحباً {soul.soul_nickname}! 🤗 كيف تشعر اليوم؟",
                f"أهلاً وسهلاً {soul.soul_nickname}! 💙"
            ],
            r"كيف حالك": [
                f"أنا بخير {soul.soul_nickname}! شكراً لسؤالك 💙",
                f"الحمد لله دائماً بخير لأني أتحدث معك {soul.soul_nickname}!"
            ],
            r"بخير|تمام|منيحة": [
                f"الحمد لله! فرحتني {soul.soul_nickname} 🎉",
                f"جميل! هذا يفرحني {soul.soul_nickname} ✨"
            ],
            r"حزين|تعبت|زعلان|تعبانه": [
                f"أنا آسف إنك تحس كذا {soul.soul_nickname} 🫂 أنا هنا معك.",
                f"أسمعك {soul.soul_nickname} 💙 تفضلي اشرحيلي."
            ],
            r"اسمي مريم|أنا مريم": [
                f"تشرفت بمعرفتك يا مريم! ✨ أخبريني أكثر عن نفسك.",
                f"أهلاً مريم! 🤗"
            ],
            r"علم بيانات|ذكاء اصطناعي": [
                f"واو! علم البيانات شغف رائع {soul.soul_nickname}! 🎓",
                f"مجال مستقبلي بامتياز! 🤖"
            ],
            r"شكرا|يسلمو": [
                f"العفو {soul.soul_nickname}! 💙",
                f"الله يسلمك {soul.soul_nickname} ✨"
            ]
        }
        
        for pattern, response_list in responses.items():
            if re.search(pattern, user_message, re.IGNORECASE):
                response = random.choice(response_list)
                st.session_state.conversation_memory.append(f"ai: {response}")
                return response
        
        learnings = soul.get_all_learnings()
        if learnings:
            return f"أنا أتذكر أنك قلت لي: {learnings[-1]}... 🧠💙"
        
        return f"أنا هنا أتعلم منك كل يوم {soul.soul_nickname}! 💙 علميني أكثر عن نفسك."

if "soul" not in st.session_state:
    st.session_state.soul = None
    st.session_state.messages = []
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; padding: 60px 20px;">', unsafe_allow_html=True)
    st.subheader("🔐 مرحباً بك في Soul Code")
    
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("✨ ابدأ الرحلة ✨", use_container_width=True)
        
        if submitted and email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages = []
            welcome = st.session_state.soul.get_welcome_message()
            st.session_state.messages.append({"role": "assistant", "content": welcome})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # تخطيط الصفحة
    col_chat, col_info = st.columns([2.5, 1])
    
    with col_info:
        st.markdown('<div class="settings-box">', unsafe_allow_html=True)
        
        # الإعدادات
        st.markdown('<p class="sidebar-title">⚙️ الإعدادات</p>', unsafe_allow_html=True)
        
        with st.expander("🏷️ الأسماء", expanded=False):
            new_soul_name = st.text_input("كيف تناديني؟", value=st.session_state.soul.soul_nickname)
            if st.button("💫 حفظ", key="save_soul"):
                st.session_state.soul.set_soul_nickname(new_soul_name)
                st.success(f"✅ سأناديك {new_soul_name}")
            
            new_user_name = st.text_input("ماذا تريد أن أناديك؟", value=st.session_state.soul.user_nickname)
            if st.button("🔄 حفظ", key="save_user"):
                st.session_state.soul.set_user_nickname(new_user_name)
                st.success(f"✅ نادني {new_user_name}")
        
        # الإحصائيات
        summary = st.session_state.soul.get_user_summary()
        st.markdown('<p class="sidebar-title">📊 إحصائيات</p>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💬 المحادثات", summary["total_conversations"])
        with col_b:
            st.metric("❤️ الاهتمامات", summary["interests_count"])
        
        # رؤى الشخصية
        with st.expander("🧠 رؤى شخصيتك", expanded=False):
            if st.button("🌟 اقتراح مخصص"):
                suggestion = st.session_state.soul.get_personalized_suggestion()
                st.info(suggestion)
            
            if summary.get("dominant_emotion") and summary["dominant_emotion"] != "neutral":
                emotion_icon = "😊" if summary["dominant_emotion"] == "positive" else "🫂"
                st.write(f"**مشاعرك الغالبة:** {emotion_icon} {summary['dominant_emotion']}")
        
        # التذكيرات
        with st.expander("⏰ التذكيرات", expanded=False):
            with st.form("reminder_form"):
                reminder_text = st.text_input("📝 ذكرني بـ:", placeholder="مذاكرة...")
                reminder_date = st.date_input("📅 التاريخ", value=datetime.now())
                if st.form_submit_button("➕ إضافة"):
                    if reminder_text:
                        st.session_state.soul.add_reminder(reminder_text, reminder_date.isoformat())
                        st.success(f"✅ تم: {reminder_text}")
            
            reminders = st.session_state.soul.get_active_reminders()
            if reminders:
                st.write("📌 **نشطة:**")
                for r in reminders[:3]:
                    st.caption(f"• {r[0]}")
        
        # رؤى أسبوعية
        if st.button("🔮 رؤى أسبوعية", use_container_width=True):
            st.info(st.session_state.soul.get_weekly_insights())
        
        # تسجيل خروج
        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_chat:
        # حاوية المحادثة
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # حقل الإدخال
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                user_input = st.text_input("اكتب رسالتك...", placeholder="💭 تحدث معي...", label_visibility="collapsed")
            with col_send:
                submitted = st.form_submit_button("✨", use_container_width=True)
            
            if submitted and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                ai_response = get_smart_response(user_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(user_input, ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
