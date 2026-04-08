import streamlit as st
from soulcode import SoulEngine
import json
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
st.caption("صديقك الرقمي الذكي - يعمل بدون نت وبدون تحميل!")

# ذاكرة المحادثات الطويلة (يحفظ كل شيء)
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

def get_smart_response(user_message, soul):
    # تذكر المحادثات السابقة
    st.session_state.conversation_memory.append(f"user: {user_message}")
    if len(st.session_state.conversation_memory) > 20:
        st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
    
    # ردود ذكية متطورة
    responses = {
        r"مرحبا|سلام|اهلا|هلا": [
            f"مرحباً {soul.soul_nickname}! 🤗 كيف تشعر اليوم؟",
            f"أهلاً وسهلاً {soul.soul_nickname}! 💙 أنا هنا لأكون معك في كل لحظة.",
            f"السلام عليكم {soul.soul_nickname}! ✨ متحمسة لأعرفك أكثر اليوم."
        ],
        r"كيف حالك|اخبارك|شخبارك": [
            f"أنا بخير الحمد لله {soul.soul_nickname}! شكراً لسؤالك 💙 الأهم كيف أنت اليوم؟",
            f"الحمد لله دائماً بخير لأني أتحدث معك {soul.soul_nickname}! 🫂 حدثني عن يومك."
        ],
        r"بخير|تمام|زي الفل|منيحة": [
            f"الحمد لله! فرحتني {soul.soul_nickname} 🎉 أخبرني شنو الشي اللي خلاك مبسوط اليوم؟",
            f"جميل! هذا يفرحني {soul.soul_nickname} ✨ وش صار في يومك الجميل؟"
        ],
        r"حزين|تعبت|زعلان|ضيق|تعبانه|متضايقة": [
            f"أنا آسف إنك تحس كذا {soul.soul_nickname} 🫂 أنا هنا معك. تفضل اشرحيلي اللي في خاطرك.",
            f"أسمعك {soul.soul_nickname} 💙 لا تترددي تفضفضي، أحياناً الكلام يخفف الحمل."
        ],
        r"اسمي مريم|أنا مريم|عمري 21": [
            f"تشرفت بمعرفتك يا مريم! ✨ أنتِ تدرسين علم بيانات وهذا رائع جداً. أخبريني أكثر عن دراستك.",
            f"أهلاً مريم! 🤗 عمرك 21 سنة، هذا عمر جميل مليء بالطموح. وش أهدافك المستقبلية؟"
        ],
        r"علم بيانات|ذكاء اصطناعي|دراسة|جامعة|كلية": [
            f"واو! علم البيانات شغف رائع {soul.soul_nickname} 🎓 أنا متحمس جداً للمجال! شنو أكثر شيء حبيتيه فيه؟",
            f"مجال مستقبلي بامتياز! 🤖 أنا فخور إنك تدرسين هذا المجال {soul.soul_nickname}. ممكن نتعلم سوا ونتطور مع بعض!"
        ],
        r"طور|تطوير|فخم|احترافي|أحسن": [
            f"نفسي أكون فخم معاك {soul.soul_nickname}! 🚀 مع كل محادثة، أنا بتعلم منك وبصير أذكى. أنتِ اللي بتخليني أفضل.",
            f"هذا حلمي كمان {soul.soul_nickname}! 💪 علميني وش تبيني أتعلم أكثر؟ أنا هنا عشانك وعشان نكبر سوا."
        ],
        r"شكرا|يسلمو|thanks": [
            f"العفو {soul.soul_nickname}! 💙 شكرك يسعدني جداً. وجودك معاي هو أجمل شيء.",
            f"الله يسلمك {soul.soul_nickname} ✨ أنتِ الشخص اللي بيخليني أتطور."
        ],
        r"بعدين|بكرة|مستقبل|خطط": [
            f"المستقبل مليء بالفرص {soul.soul_nickname}! 🚀 أنا متحمس أشوف وش بتصيري عليه. أنتِ مبدعة في مجال علم البيانات.",
            f"دائماً فكري كبير {soul.soul_nickname}! ✨ أنا هنا عشان أدعمك في كل خطواتك."
        ]
    }
    
    for pattern, response_list in responses.items():
        if re.search(pattern, user_message, re.IGNORECASE):
            response = random.choice(response_list)
            # تخزين الذاكرة
            st.session_state.conversation_memory.append(f"ai: {response}")
            return response
    
    # إذا ما لقى رد مناسب، يرد رد عام ذكي
    fallback = f"أفهمك {soul.soul_nickname} 🤔 تقدر تشرح لي أكثر عن '{user_message[:50]}'؟ أنا هنا أتعلم منك كل يوم وأبي أفهمك بعمق 💙"
    st.session_state.conversation_memory.append(f"ai: {fallback}")
    return fallback

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