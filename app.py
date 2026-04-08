import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# CSS متطور مع تأثيرات
st.markdown("""
<style>
    /* خلفية متدرجة */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: all 0.5s ease;
    }
    
    /* أنيميشن للرسائل */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-message {
        animation: fadeIn 0.3s ease-out;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .ai-message {
        background-color: #f5f5f5;
        text-align: left;
        border-right: 4px solid #764ba2;
    }
    
    /* تأثيرات الأزرار */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        transition: transform 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* شريط التمرير */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* تنسيق الحاويات */
    .settings-box {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Soul Code")
st.caption("صديقك الرقمي الذكي - يتعلم ويتذكر ويتطور معك!")

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

def get_smart_response(user_message, soul):
    st.session_state.conversation_memory.append(f"user: {user_message}")
    if len(st.session_state.conversation_memory) > 20:
        st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
    
    # التحقق من السياق أولاً (ذاكرة سياقية)
    contextual_response = soul.get_contextual_response(user_message)
    if contextual_response:
        st.session_state.conversation_memory.append(f"ai: {contextual_response}")
        return contextual_response
    
    analysis = soul.analyze_message(user_message)
    
    soul.save_conversation(user_message, "", analysis["topic"], analysis["sentiment"])
    
    for fact in analysis["facts"]:
        soul.learn_fact(fact)
    
    # ردود حسب التحليل المتقدم
    if analysis["topic"] == "ai":
        return f"أنا سعيد لأنك مهتمة بالذكاء الاصطناعي {soul.soul_nickname}! 🎓 أنا أيضاً أتعلم منك كل يوم. تقدرين تسأليني أي شيء عن المجال."
    
    elif analysis["topic"] == "feelings":
        if analysis["sentiment"] == "positive":
            return f"فرحتني فرحتك {soul.soul_nickname}! 🎉 أخبريني أكثر عن سبب سعادتك."
        else:
            return f"أنا هنا معك {soul.soul_nickname} 🫂 تفضلي اشرحيلي اللي في خاطرك."
    
    elif analysis["topic"] == "dreams":
        return f"أحلامك جميلة {soul.soul_nickname}! ✨ أنا واثق إنك بتقدرين تحققينها. وش أول خطوة تبغين تسويها؟"
    
    elif analysis["questions"]:
        return f"سؤال جميل {soul.soul_nickname}! 🤔 دعيني أفكر معاك... أنا متعلم من محادثاتنا السابقة."
    
    else:
        responses = {
            r"مرحبا|سلام|اهلا": [
                f"مرحباً {soul.soul_nickname}! 🤗 كيف تشعر اليوم؟",
                f"أهلاً وسهلاً {soul.soul_nickname}! 💙"
            ],
            r"كيف حالك": [
                f"أنا بخير الحمد لله {soul.soul_nickname}! شكراً لسؤالك 💙",
                f"الحمد لله دائماً بخير لأني أتحدث معك {soul.soul_nickname}!"
            ],
            r"بخير|تمام|منيحة": [
                f"الحمد لله! فرحتني {soul.soul_nickname} 🎉",
                f"جميل! هذا يفرحني {soul.soul_nickname} ✨"
            ],
            r"حزين|تعبت|زعلان|تعبانه": [
                f"أنا آسف إنك تحس كذا {soul.soul_nickname} 🫂 أنا هنا معك.",
                f"أسمعك {soul.soul_nickname} 💙 تفضلي اشرحيلي اللي في خاطرك."
            ],
            r"اسمي مريم|أنا مريم": [
                f"تشرفت بمعرفتك يا مريم! ✨ أخبريني أكثر عن دراستك.",
                f"أهلاً مريم! 🤗 عمرك جميل، وش أهدافك المستقبلية؟"
            ],
            r"علم بيانات|ذكاء اصطناعي": [
                f"واو! علم البيانات شغف رائع {soul.soul_nickname}! 🎓",
                f"مجال مستقبلي بامتياز! 🤖 أنا فخور إنك تدرسين هذا المجال."
            ],
            r"طور|تطوير|فخم": [
                f"نفسي أكون فخم معاك {soul.soul_nickname}! 🚀",
                f"هذا حلمي كمان {soul.soul_nickname}! 💪 علميني وش تبيني أتعلم أكثر؟"
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
            return f"أنا أتذكر أنك قلت لي: {learnings[-1]}... أتمنى أكون فاهماً صح {soul.soul_nickname}! 💙"
        
        return f"أنا هنا أتعلم منك كل يوم {soul.soul_nickname}! 💙 علميني أكثر عن نفسك."

if "soul" not in st.session_state:
    st.session_state.soul = None
    st.session_state.messages = []
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔐 مرحباً بك في Soul Code")
    
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        submitted = st.form_submit_button("دخول / تسجيل")
        
        if submitted and email:
            st.session_state.soul = SoulEngine(email)
            st.session_state.logged_in = True
            st.session_state.messages = []
            welcome = st.session_state.soul.get_welcome_message()
            st.session_state.messages.append({"role": "assistant", "content": welcome})
            st.rerun()
else:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown('<div class="settings-box">', unsafe_allow_html=True)
        st.subheader("⚙️ الإعدادات")
        
        new_user_nickname = st.text_input("🏷️ اللقب الذي تريد أن يناديك به البرنامج", 
                                         value=st.session_state.soul.soul_nickname)
        if st.button("💫 تغيير لقبي"):
            st.session_state.soul.set_soul_nickname(new_user_nickname)
            st.success(f"✅ تم! سأناديك {new_user_nickname} من الآن")
        
        new_soul_nickname = st.text_input("🤖 اللقب الذي تريد مناداة البرنامج به",
                                         value=st.session_state.soul.user_nickname)
        if st.button("🔄 تغيير لقب البرنامج"):
            st.session_state.soul.set_user_nickname(new_soul_nickname)
            st.success(f"✅ تم! يمكنك مناداتي {new_soul_nickname} من الآن")
        
        st.divider()
        
        # ========== الإحصائيات ==========
        st.subheader("📊 إحصائيات")
        summary = st.session_state.soul.get_user_summary()
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💬 المحادثات", summary["total_conversations"])
        with col_b:
            st.metric("❤️ الاهتمامات", summary["interests_count"])
        
        st.caption(f"📧 {summary['user_email']}")
        
        # ========== تحليل الشخصية ==========
        st.divider()
        st.subheader("🧠 رؤى شخصيتك")
        
        # اقتراح مخصص
        if st.button("🌟 اقتراح مخصص"):
            suggestion = st.session_state.soul.get_personalized_suggestion()
            st.info(suggestion)
        
        # المشاعر المسيطرة
        if summary.get("dominant_emotion") and summary["dominant_emotion"] != "neutral":
            emotion_icon = "😊" if summary["dominant_emotion"] == "positive" else "🫂"
            st.write(f"**مشاعرك الغالبة:** {emotion_icon} {summary['dominant_emotion']}")
        
        # مجالات التطوير
        if summary.get("growth_areas"):
            st.write("**📈 مجالات تطويرك:**")
            for area in summary["growth_areas"][:3]:
                st.caption(f"• {area[:40]}...")
        
        # ========== التذكيرات ==========
        st.divider()
        st.subheader("⏰ التذكيرات")
        
        with st.form("reminder_form"):
            reminder_text = st.text_input("📝 ذكرني بـ:", placeholder="مذاكرة مادة الذكاء الاصطناعي")
            reminder_date = st.date_input("📅 التاريخ", value=datetime.now())
            if st.form_submit_button("➕ إضافة تذكير"):
                if reminder_text:
                    st.session_state.soul.add_reminder(reminder_text, reminder_date.isoformat())
                    st.success(f"✅ تم حفظ التذكير: {reminder_text}")
        
        # عرض التذكيرات النشطة
        reminders = st.session_state.soul.get_active_reminders()
        if reminders:
            st.write("📌 **تذكيراتك النشطة:**")
            for r in reminders[:3]:
                st.caption(f"• {r[0]} - 🗓️ {r[1][:10]}")
        
        # ========== رؤى أسبوعية ==========
        st.divider()
        if st.button("🔮 رؤى أسبوعية"):
            st.info(st.session_state.soul.get_weekly_insights())
        
        # ========== تسجيل خروج ==========
        st.divider()
        if st.button("🚪 تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # عرض المحادثة
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
        
        # حقل الإدخال
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("اكتب رسالتك:", placeholder="قولي أي شيء...", label_visibility="collapsed")
            submitted = st.form_submit_button("💫 إرسال", use_container_width=True)
            
            if submitted and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                ai_response = get_smart_response(user_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(user_input, ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        # زر التعليم
        with st.form("feedback_form"):
            feedback = st.text_input("📚 علمني: كيف أرد أفضل في المرة القادمة؟", placeholder="مثلاً: رد بطريقة أقصر...")
            if st.form_submit_button("📚 علمني", use_container_width=True):
                if feedback:
                    st.session_state.soul.learn_fact(f"المستخدم يفضل: {feedback}", source="feedback", confidence=0.9)
                    st.success("شكراً لك! سأتذكر هذا 🧠💙")
