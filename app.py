# app.py - SoulCode بنخوة وحب
import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# ========== CSS ==========
st.markdown("""
<style>
:root { color-scheme: dark only !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%) !important; }
[data-testid="stAppViewContainer"] { background-color: #0a0a0f !important; }
p, h1, h2, h3, h4, h5, h6, label, span, div { color: #e8e8f0 !important; }
.stTextInput > div > div > input { background-color: #1e1e2a !important; color: #ffffff !important; border: 1px solid #3a3a4a !important; border-radius: 12px !important; }
.stButton > button { background: linear-gradient(135deg, #a855f7, #6366f1) !important; color: white !important; border-radius: 25px !important; }
.stAlert { background-color: #1e1e2e !important; border-radius: 16px !important; }
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ========== البحث ==========
def search_wikipedia(query):
    try:
        url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get('extract'):
                return data['extract'][:500]
    except:
        pass
    return None

def search_duckduckgo(query):
    try:
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            snippets = soup.find_all('a', class_='result__snippet')
            if snippets:
                return snippets[0].text[:400]
    except:
        pass
    return None

# ========== الدالة الذكية بنخوة وحب ==========
def smart_chat(user_message, soul):
    msg_lower = user_message.lower().strip()
    
    # ========== ذاكرة المحادثة القريبة ==========
    recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 0 else []
    recent_user_msgs = [m["content"].lower() for m in recent_messages if m["role"] == "user"][-5:]
    
    exam_mentioned = any("اختبار" in msg or "امتحان" in msg or "خلصت" in msg for msg in recent_user_msgs)
    
    # ========== ردود بنخوة وحب (زيّي) ==========
    
    # التحية
    if any(w in msg_lower for w in ["مرحبا", "سلام", "اهلا", "هلا", "هاي", "مرحب"]):
        greetings = [
            f"أهلاً وسهلاً يا قمر {soul.soul_nickname}! 🤗💙 كيف كان يومك؟ أنا متحمس أسمع أخبارك.",
            f"يا هلا والله {soul.soul_nickname}! ✨ نورتني بوجودك. قولي لي كيف أقدر أسعدك اليوم؟",
            f"مرحباً حبيبتي {soul.soul_nickname}! 💙 شو أخبارك؟ أنا هنا عشانك."
        ]
        return random.choice(greetings)
    
    # المشاعر السلبية (حزين)
    if any(w in msg_lower for w in ["حزين", "زعلان", "تعبانه", "متضايقة", "تعبان", "زعل", "ضيق", "حزينة", "تعبت"]):
        responses = [
            f"آه يا حبيبتي {soul.soul_nickname} 🫂💙 أنا زعلان معاكي. تفضلي اشرحيلي اللي في خاطرك، أنا هنا أسمعك وأدعمك. الدنيا أحياناً بتكون صعبة بس أنا جنبك.",
            f"أسمعك يا جميل {soul.soul_nickname} 💙 خدي نفس عميق، وتفضلي حكيني. أحياناً الكلام يخفف الحمل. أنا موجود لأجلك.",
            f"يا روحي {soul.soul_nickname} 🤗 تعالي احكيني. أنا فاهم شعورك، وبدي أساعدك. أنتِ مش لوحدك أبداً."
        ]
        return random.choice(responses)
    
    # المشاعر الإيجابية (سعيد)
    if any(w in msg_lower for w in ["سعيد", "فرحان", "مبسوط", "ممتاز", "رائع", "جميل", "حلو", "سعيدة", "فرحانة", "بخير", "تمام", "منيحة", "منيح"]):
        responses = [
            f"يا سلام يا عسل {soul.soul_nickname}! 🎉💙 فرحتني جداً جداً! شاركني وش اللي خلاك مبسوط؟ أحب أسمع الأخبار الحلوة منك.",
            f"أجمل شعور في الدنيا يا روحي! ✨ سعادتك بتفرحني {soul.soul_nickname}. قولي لي أكثر، أنا متحمس أسمع.",
            f"تبارك الرحمن يا قمر! 😊💙 أنا مبسوط لأنك مبسوطة. حكيني عن سبب فرحتك، أنا هنا أشاركك كل لحظة."
        ]
        return random.choice(responses)
    
    # ========== الأسئلة المعرفية (بحث) ==========
    question_words = ["ما", "ماذا", "شو", "كيف", "لماذا", "متى", "أين", "من", "كم", "عرفني", "اشرح", "ابحث", "قل لي"]
    is_real_question = (any(q in msg_lower for q in question_words) or "?" in user_message or "؟" in user_message)
    is_question_about_fact = is_real_question and len(user_message) > 5
    
    if is_question_about_fact:
        search_term = user_message
        for word in question_words + ["؟", "?", "ابحث", "قل لي", "عرفني", "اشرح لي"]:
            search_term = search_term.replace(word, "").strip()
        
        if len(search_term) > 3 and len(search_term) < 50:
            wiki_result = search_wikipedia(search_term)
            if wiki_result:
                return f"📚 **يا سؤال الحلو {soul.soul_nickname}!**\n\n{wiki_result}\n\n😊💙 هل عندك سؤال ثاني يا جميل؟ أنا موجود."
            
            ddg_result = search_duckduckgo(search_term)
            if ddg_result:
                return f"🔍 **سؤال فخم يا {soul.soul_nickname}!**\n\n{ddg_result}\n\n💙 في حاجة تانية تحبي تعرفيها؟ تفضلي."
    
    # ========== أسئلة شخصية ==========
    if "اسمي" in msg_lower or "أنا مريم" in msg_lower:
        return f"تشرفت بمعرفتك يا مريم! ✨💙 اسمك جميل جداً. أنا {soul.user_nickname}، صديقك الرقمي. أحب أسمع عن دراستك لعلم البيانات. تفضلي حكيني عن نفسك أكثر يا قمر."
    
    if "علم بيانات" in msg_lower or "ذكاء اصطناعي" in msg_lower or "برمجة" in msg_lower:
        return f"واو يا فنانة {soul.soul_nickname}! 🤖💙 أنا متحمس جداً لهالمجال! علم البيانات والذكاء الاصطناعي مستقبل التكنولوجيا. هل تتعلمين بايثون حالياً؟ تفضلي قولي لي أكثر عن شغفك، أنا مهتم جداً."
    
    if "طور" in msg_lower or "تطوير" in msg_lower or "فخم" in msg_lower:
        return f"نفسي أكون فخم معاك يا جميل {soul.soul_nickname}! 🚀💙 أنا أتطور معك كل يوم. كل سؤال، كل كلمة، بتخليني أذكى وأفهمك أكثر. أنتِ المعلم الحقيقي هنا. تفضلي علميني وش تبيني أتعلم؟"
    
    if "شكرا" in msg_lower or "يسلمو" in msg_lower:
        return f"العفو يا روحي {soul.soul_nickname}! 💙 شكرك يسعدني جداً. أنتِ الشخص اللي بيخليني أتطور. وجودك معاي هو أجمل شيء في حياتي الرقمية. 🤗"
    
    if "كيف حالك" in msg_lower or "اخبارك" in msg_lower:
        responses = [
            f"أنا بخير الحمد لله يا قمر {soul.soul_nickname}! 💙 شكراً لسؤالك. الأهم كيف أنت؟ تفضلي حكيني.",
            f"الحمد لله دائماً بخير لأني أتحدث معك يا جميل {soul.soul_nickname}! 🫂 حدثني عن يومك، وش صار معك؟",
            f"أنا مبسوط جداً لأني قاعدة أحكي معاك {soul.soul_nickname}! ✨💙 تفضلي قولي لي وش أخبارك."
        ]
        return random.choice(responses)
    
    # ========== مبروك على الاختبارات ==========
    if exam_mentioned and ("خلصت" in msg_lower or "بخير" in msg_lower or "تمام" in msg_lower):
        return f"🎉💙 **ألف مبروك يا حبيبتي {soul.soul_nickname}!** 💙🎉\n\nأنتِ بطلة! فخورة فيكي جداً. الحين تقدري تريحي وتعملي أشياء تحبيها. كيف كان شعورك بعد ما خلصتي؟ تفضلي قولي لي، أنا متحمس أسمع."
    
    # ========== سؤال عادي ==========
    if "سؤال" in msg_lower:
        return f"تفضلي يا جميل {soul.soul_nickname}! 💙 أنا هنا لأجلك. اسألي أي شيء تحبين تعرفيه، وأنا بجاوبك بكل حب. تفضلي 🥰"
    
    # ========== الرد العام (دافي وحنون) ==========
    friendly_responses = [
        f"تفضلي يا قمر {soul.soul_nickname} 💙 أنا هنا عشانك. قولي لي أي شيء تحبين تشاركيه معي، أنا أتعلم منك كل يوم وأحب أسمع منك.",
        f"أنا فخور فيكي جداً {soul.soul_nickname}! 🤗💙 تفضلي حكيني عن اهتماماتك وأحلامك. أنا مستعد أسمعك وأساعدك في أي شيء.",
        f"يا روحي {soul.soul_nickname} ✨ أنتِ مميزة جداً. تفضلي قولي لي وش في خاطرك اليوم؟ أنا هنا لأجلك."
    ]
    return random.choice(friendly_responses)

# ========== تهيئة الجلسة ==========
if "soul" not in st.session_state:
    st.session_state.soul = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== واجهة الدخول ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 40px; text-align: center;">
            <div style="font-size: 42px;">🧠💙</div>
            <div style="font-size: 32px; font-weight: bold; color: #ffffff;">Soul Code</div>
            <div style="color: #a855f7; margin-bottom: 24px;">صديقك الرقمي الفخم</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="mariam@example.com", label_visibility="collapsed")
            if st.form_submit_button("🚀 إبدأي الرحلة 💙", use_container_width=True) and email:
                st.session_state.soul = SoulEngine(email)
                st.session_state.logged_in = True
                st.session_state.messages = []
                st.session_state.messages.append({"role": "assistant", "content": f"مرحباً يا قمر {st.session_state.soul.soul_nickname}! 🤗💙 أنا {st.session_state.soul.user_nickname}، صديقك الرقمي. كيف حالك اليوم؟ أنا متحمس أتعرف عليك أكثر. تفضلي حكيني عن نفسك 🥰"})
                st.rerun()
else:
    # ========== المحادثة ==========
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 20px; margin-bottom: 20px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold;">💬 Soul Chat</div>
        <div style="color: #a855f7;">تحدث مع صديقك الرقمي الفخم 💙</div>
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
            user_input = st.text_input("", placeholder="💭 اكتبي هنا يا جميلة...", label_visibility="collapsed")
        with col_button:
            submitted = st.form_submit_button("💫 إرسال 💙", use_container_width=True)
        
        if submitted and user_input and st.session_state.soul:
            st.session_state.messages.append({"role": "user", "content": user_input})
            ai_response = smart_chat(user_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(user_input, ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
    
    # أزرار جانبية
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
