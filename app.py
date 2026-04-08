import streamlit as st
from soulcode import SoulEngine
import random
import re

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.chat-message { padding: 1rem; border-radius: 1rem; margin: 0.5rem 0; }
.user-message { background-color: #e3f2fd; text-align: right; }
.ai-message { background-color: #f5f5f5; text-align: left; border-right: 4px solid #764ba2; }
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
    
    analysis = soul.analyze_message(user_message)
    
    soul.save_conversation(user_message, "", analysis["topic"], analysis["sentiment"])
    
    for fact in analysis["facts"]:
        soul.learn_fact(fact)
    
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
        st.subheader("⚙️ الإعدادات")
        
        new_user_nickname = st.text_input("اللقب الذي تريد أن يناديك به البرنامج", 
                                         value=st.session_state.soul.soul_nickname)
        if st.button("تغيير لقبي"):
            st.session_state.soul.set_soul_nickname(new_user_nickname)
            st.success(f"تم! سأناديك {new_user_nickname} من الآن")
        
        new_soul_nickname = st.text_input("اللقب الذي تريد مناداة البرنامج به",
                                         value=st.session_state.soul.user_nickname)
        if st.button("تغيير لقب البرنامج"):
            st.session_state.soul.set_user_nickname(new_soul_nickname)
            st.success(f"تم! يمكنك مناداتي {new_soul_nickname} من الآن")
        
        st.divider()
        summary = st.session_state.soul.get_user_summary()
        st.metric("عدد المحادثات", summary["total_conversations"])
        st.metric("عدد الاهتمامات", summary["interests_count"])
        st.write(f"**بريدك:** {summary['user_email']}")
        
        if st.button("🔮 رؤى أسبوعية"):
            st.info(st.session_state.soul.get_weekly_insights())
        
        if st.button("🚪 تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
    
    with col1:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("اكتب رسالتك:", placeholder="قولي أي شيء...")
            submitted = st.form_submit_button("إرسال 💫")
            
            if submitted and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                ai_response = get_smart_response(user_input, st.session_state.soul)
                st.session_state.soul.learn_from_conversation(user_input, ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        # زر التعليم
        with st.form("feedback_form"):
            feedback = st.text_input("📚 علمني: كيف أرد أفضل في المرة القادمة؟", placeholder="مثلاً: رد بطريقة أقصر...")
            if st.form_submit_button("علمني"):
                if feedback:
                    st.session_state.soul.learn_fact(f"المستخدم يفضل: {feedback}", source="feedback")
                    st.success("شكراً لك! سأتذكر هذا 🧠💙")
