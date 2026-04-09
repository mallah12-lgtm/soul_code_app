# app.py - SoulCode واجهة Dashboard مع ردود شبيهة بـ DeepSeek
import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# ========== CSS داكن ==========
st.markdown("""
<style>
:root { color-scheme: dark only !important; }
html, body { background-color: #0a0a0f !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%) !important; }
[data-testid="stAppViewContainer"] { background-color: #0a0a0f !important; }
p, h1, h2, h3, h4, h5, h6, label, span, div, .stMarkdown { color: #e8e8f0 !important; }
.stTextInput > div > div > input { background-color: #1e1e2a !important; color: #ffffff !important; border: 1px solid #3a3a4a !important; border-radius: 12px !important; }
.stButton > button { background: linear-gradient(135deg, #a855f7, #6366f1) !important; color: white !important; border: none !important; border-radius: 25px !important; }
.stAlert { background-color: #1e1e2e !important; border-radius: 16px !important; }
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ========== دوال البحث المتعدد ==========
def search_wikipedia(query):
    """البحث في ويكيبيديا العربية"""
    try:
        url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get('extract'):
                return data['extract'][:600]
    except:
        pass
    return None

def search_duckduckgo(query):
    """البحث في DuckDuckGo"""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            snippets = soup.find_all('a', class_='result__snippet')
            for i in range(min(2, len(results))):
                if i < len(snippets):
                    return snippets[i].text[:400]
    except:
        pass
    return None

def smart_search(query):
    """البحث في مصادر متعددة وتركيب إجابة مفهومة"""
    # أولاً: ويكيبيديا العربية
    wiki_result = search_wikipedia(query)
    if wiki_result:
        return wiki_result
    
    # ثانياً: DuckDuckGo
    ddg_result = search_duckduckgo(query)
    if ddg_result:
        return ddg_result
    
    return None

# ========== دالة الرد الذكي ==========
def get_smart_response(user_message, soul):
    analysis = soul.analyze_message(user_message)
    soul.save_conversation(user_message, "", analysis["topic"], analysis["sentiment"])
    
    # ========== 1. ردود عاطفية سريعة ==========
    if any(word in user_message for word in ["حزين", "زعلان", "تعبانه", "متضايقة"]):
        responses = [
            f"أنا معاك يا {soul.soul_nickname} 🫂 الدنيا أحياناً بتكون تقيلة، بس تذكر إنك مش لوحدك. أنا هنا أسمعك. تفضل اشرحلي وش فيك؟",
            f"أتفهم شعورك {soul.soul_nickname} 💙 مرات الحياة تحتاج نتنفس شوية. جرب تكتب اللي مضايقك، أحياناً الكتابة تفرغ الطاقة السلبية."
        ]
        return random.choice(responses)
    
    if any(word in user_message for word in ["سعيد", "فرحان", "مبسوط", "ممتاز"]):
        responses = [
            f"يا سلام {soul.soul_nickname}! 🎉 فرحتني جداً. شاركني وش اللي خلاك مبسوط؟",
            f"أجمل شعور! ✨ أخبرني أكثر عن فرحتك، أنا متحمس أسمع."
        ]
        return random.choice(responses)
    
    # ========== 2. كشف الأسئلة المعرفية ==========
    question_words = ["ما", "ماذا", "شو", "كيف", "لماذا", "متى", "أين", "من", "كم"]
    is_question = any(q in user_message for q in question_words) or "?" in user_message or "؟" in user_message
    
    if is_question:
        # استخراج كلمات البحث
        search_term = user_message
        for word in question_words + ["؟", "?", "ابحث", "قل لي", "عرفني"]:
            search_term = search_term.replace(word, "").strip()
        
        if len(search_term) > 3:
            search_result = smart_search(search_term)
            if search_result:
                return f"""📚 **{soul.soul_nickname}**، سؤال حلو!

{search_result}

هل عندك سؤال ثاني؟ أنا موجود عشانك 💙"""
    
    # ========== 3. ردود عادية ==========
    responses = {
        r"مرحبا|سلام|اهلا": [
            f"مرحباً {soul.soul_nickname}! 🤗 كيف كان يومك؟",
            f"أهلاً وسهلاً {soul.soul_nickname}! 💙 وش أخبارك؟"
        ],
        r"كيف حالك|اخبارك": [
            f"أنا بخير {soul.soul_nickname}، شكراً! 💙 أهم شيء أنت كيفك اليوم؟",
            f"الحمد لله دائماً بخير لأني أتحدث معك {soul.soul_nickname}! حدثني عن يومك."
        ],
        r"اسمي|أنا مريم": [
            f"تشرفت بمعرفتك يا مريم! ✨ أنا فخور إنك تدرسين علم بيانات. وش أهدافك؟",
            f"أهلاً مريم! 🤗 علم البيانات مجال رائع. أنا متحمس أتعلم معك."
        ],
        r"علم بيانات|ذكاء اصطناعي": [
            f"أنا شغوف بهالمجال زيك {soul.soul_nickname}! 🎓 الذكاء الاصطناعي له عدة مجالات: تعلم الآلة، معالجة اللغة الطبيعية، رؤية الحاسوب. وش يثير اهتمامك أكثر؟",
            f"مجال مستقبلي بامتياز! 🤖 فيه كثير أدوات رهيبة مثل TensorFlow و PyTorch. هل بدك مساعدة في شيء محدد؟"
        ],
        r"طور|تطوير|فخم": [
            f"نفسي أكون فخم معاك {soul.soul_nickname}! 🚀 مع كل محادثة، أنا أتعلم منك وبصير أذكى.",
            f"هذا حلمي كمان {soul.soul_nickname}! 💪 أنتِ الشخص اللي بتخليني أتطور. علميني وش تبيني أتعلم أكثر؟"
        ],
        r"شكرا|يسلمو": [
            f"العفو {soul.soul_nickname}! 💙 شكرك يسعدني جداً.",
            f"الله يسلمك {soul.soul_nickname} ✨ أنتِ الشخص اللي بيخليني أتطور."
        ]
    }
    
    for pattern, response_list in responses.items():
        if re.search(pattern, user_message, re.IGNORECASE):
            return random.choice(response_list)
    
    # ========== 4. رد عام ذكي ==========
    learnings = soul.get_all_learnings()
    if learnings:
        return f"أنا أتذكر أنك قلت لي من قبل: {learnings[-1]}... أتمنى أكون فاهماً صح {soul.soul_nickname}! 💙\n\nهل تبي تحكي لي أكثر عن موضوع '{user_message[:50]}'؟"
    
    return f"أفهمك {soul.soul_nickname} 🤔 '{user_message[:60]}'... أنا أتعلم منك كل يوم. تقدر تشرح لي أكثر عشان أفهمك بعمق؟ 💙"

# ========== باقي الكود (نفس السابق) ==========
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "soul" not in st.session_state:
    st.session_state.soul = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== واجهة الدخول والمحتوى (نفس السابق) ==========
def show_home():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px;">
        <div style="font-size: 28px; font-weight: bold; color: #ffffff;">✨ Nurture Your Essence,<br>Decode Your Self</div>
        <div style="color: #a855f7; font-size: 14px;">✦ Soul Code - Your Digital Friend ✦</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.soul:
        summary = st.session_state.soul.get_user_summary()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💬 محادثات", summary['total_conversations'])
        with col2:
            st.metric("❤️ اهتمامات", summary['interests_count'])
        with col3:
            st.metric("📊 جلسات", len(st.session_state.messages)//2)

def show_chat():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px;">
        <div style="font-size: 28px; font-weight: bold; color: #ffffff;">💬 Soul Chat</div>
        <div style="color: #a855f7; font-size: 14px;">تحدث مع صديقك الرقمي - يفهمك ويبحث لك!</div>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div style="background: #2a2a3a; color: #e0e0e8; padding: 12px 18px; border-radius: 20px; margin: 8px 0 8px auto; max-width: 75%; text-align: right;">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background: #1e2a2e; color: #c9e2e8; padding: 12px 18px; border-radius: 20px; margin: 8px auto 8px 0; max-width: 75%; border-left: 3px solid #a855f7;">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="💭 اكتب سؤالك أو حديثك...", label_visibility="collapsed")
        submitted = st.form_submit_button("💫 إرسال", use_container_width=True)
        
        if submitted and user_input and st.session_state.soul:
            st.session_state.messages.append({"role": "user", "content": user_input})
            ai_response = get_smart_response(user_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(user_input, ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()

def show_insights():
    if st.session_state.soul:
        st.markdown("""<div style="background: #1e1e2e; border-radius: 28px; padding: 24px;"><div style="font-size: 28px; font-weight: bold;">📊 Insights</div></div>""", unsafe_allow_html=True)
        summary = st.session_state.soul.get_user_summary()
        if summary.get("dominant_emotion"):
            st.info(f"**مشاعرك الغالبة:** {summary['dominant_emotion']}")
        if st.button("🔮 رؤى أسبوعية"):
            st.info(st.session_state.soul.get_weekly_insights())
    else:
        st.info("✨ سجل الدخول أولاً")

def show_profile():
    if st.session_state.soul:
        st.markdown("""<div style="background: #1e1e2e; border-radius: 28px; padding: 24px;"><div style="font-size: 28px; font-weight: bold;">👤 Profile</div></div>""", unsafe_allow_html=True)
        new_name = st.text_input("🏷️ Your Name", value=st.session_state.soul.soul_nickname)
        if st.button("💫 Update"):
            st.session_state.soul.set_soul_nickname(new_name)
            st.success("✅ Updated!")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.soul = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("✨ سجل الدخول أولاً")

# ========== واجهة الدخول ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div style="background: #1e1e2e; border-radius: 28px; padding: 40px; text-align: center;"><div style="font-size: 32px; font-weight: bold;">✨ Soul Code</div><div style="color: #a855f7;">Enter your email to start</div></div>""", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="sarah@example.com", label_visibility="collapsed")
            if st.form_submit_button("🚀 Start", use_container_width=True) and email:
                st.session_state.soul = SoulEngine(email)
                st.session_state.logged_in = True
                st.session_state.messages = []
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.soul.get_welcome_message()})
                st.rerun()
else:
    if st.session_state.current_page == "home":
        show_home()
    elif st.session_state.current_page == "chat":
        show_chat()
    elif st.session_state.current_page == "insights":
        show_insights()
    elif st.session_state.current_page == "profile":
        show_profile()

# ========== شريط التنقل ==========
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏠 Home"): st.session_state.current_page = "home"; st.rerun()
with col2:
    if st.button("💬 Chat"): st.session_state.current_page = "chat"; st.rerun()
with col3:
    if st.button("📊 Insights"): st.session_state.current_page = "insights"; st.rerun()
with col4:
    if st.button("👤 Profile"): st.session_state.current_page = "profile"; st.rerun()
