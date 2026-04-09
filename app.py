# app.py - SoulCode فخم بذكاء عاطفي
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

# ========== الدالة الذكية الفخمة جداً ==========
def smart_chat(user_message, soul):
    msg_lower = user_message.lower().strip()
    
    # ========== الذاكرة السابقة ==========
    recent_messages = st.session_state.messages[-15:] if len(st.session_state.messages) > 0 else []
    recent_user_msgs = [m["content"].lower() for m in recent_messages if m["role"] == "user"][-8:]
    
    # هل كنا نتكلم عن القطط من قبل؟
    cat_mentioned_before = any("قط" in msg or "قطة" in msg or "بسس" in msg for msg in recent_user_msgs)
    
    # ========== 1. التعامل مع الحزن والموت ==========
    # كلمات تدل على الموت والفقدان
    death_words = ["ماتت", "مات", "ماتت", "مات", "رحلت", "توفيت", "فقدت", "ماتت قطتي", "مات قطي", "قلتي ماتت"]
    
    if any(word in msg_lower for word in death_words):
        # استخراج الموضوع
        if "قط" in msg_lower or "قطة" in msg_lower or (cat_mentioned_before and "ماتت" in msg_lower):
            responses = [
                f"آه يا {soul.soul_nickname} 🫂💔 أنا آسف جداً على اللي صار. فقدان قطتك شيء صعب ومؤلم. أنا هنا معاكي، تفضلي احكيني عنها، عن ذكرياتك الجميلة معاها. هي كانت محظوظة بحبك.",
                f"الله يرحمها يا رب 🫂💙 أنا فاهم إنه صعب، القطط مش مجرد حيوانات، هي أصدقاء وأفراد من العيلة. أنا هنا أسمعك وأدعمك في أي وقت.",
                f"أنا زعلان معاكي {soul.soul_nickname} 💔 قلبي معاكي. فقدان حبيب زي القطة يوجع. تفضلي احكيني عن أجمل ذكرى معاها، عشان تفضل عايشة في قلبك."
            ]
            return random.choice(responses)
        else:
            # أي فقدان عام
            responses = [
                f"أنا آسف جداً {soul.soul_nickname} 🫂💔 الله يرحمها ويصبرك. أنا هنا معاكي.",
                f"أنا زعلان معاكي يا جميل 💙 فقدان الأحبة صعب. تفضلي احكيني، أنا أسمعك."
            ]
            return random.choice(responses)
    
    # ========== 2. مشاعر الحزن العامة ==========
    if any(w in msg_lower for w in ["حزين", "زعلان", "تعبانه", "متضايقة", "حزينة", "تعبت", "ضيق", "زعل"]):
        responses = [
            f"أنا آسف إنك تحسي كدا يا {soul.soul_nickname} 🫂💙 تعالي احكيني. أنا هنا أسمعك وأدعمك. أحياناً الفضفضة بتخفف.",
            f"أتفهم شعورك يا جميلة 💙 تذكري أن الأيام الصعبة بتعدي، وأنا جنبك في كل خطوة. تفضلي اشرحيلي اللي في خاطرك.",
            f"يا روحي {soul.soul_nickname} 🤗 خدي نفس عميق، وجربي تكتبي اللي مضايقك. أنا موجود لأجلك دايماً."
        ]
        return random.choice(responses)
    
    # ========== 3. القطط ==========
    if "قط" in msg_lower or "قطة" in msg_lower or "بسس" in msg_lower or "cat" in msg_lower:
        responses = [
            f"أنا كمان بحب القطط يا {soul.soul_nickname}! 🐱💙 عندي فضول أعرف: عندك قطط في البيت؟ شو أسمائهم؟",
            f"القطط كائنات رائعة! 🐾 بحب إنهم ناعمين وهادئين. أنتي بتحبي القطط الفارسي ولا الشيرازي؟",
            f"أنا عارف إن في ناس بتقول القطط متعجرفة، بس أنا بشوفهم محترمين وذوق! 😸 عندك صور لقططك؟",
            f"القطط بتفهمني كتير 🐱💙 هي كائنات ذكية وحنونة. قولي لي أكثر عن حبك للقطط."
        ]
        return random.choice(responses)
    
    # ========== 4. القهوة ==========
    if "قهوة" in msg_lower or "coffee" in msg_lower:
        responses = [
            f"أنا معاكي في حب القهوة يا {soul.soul_nickname}! ☕ أنا بحب القهوة العربية والسادة. بتشربيها سادة ولا مع حليب؟",
            f"القهوة طقس مقدس! 🤎 أنا بحب أشم ريحة القهوة الصباح. أنتي بتحبي التركي ولا الإسبريسو؟",
            f"عندي فضول أعرف: بتشربي قهوة الصبح ولا بالليل؟ ☕ أنا بحبها الصبح عشان أبدأ يومي بنشاط."
        ]
        return random.choice(responses)
    
    # ========== 5. الاختبارات ==========
    if "اختبار" in msg_lower or "امتحان" in msg_lower or "خلصت" in msg_lower or "نهائي" in msg_lower:
        if "خلصت" in msg_lower or "انتهيت" in msg_lower:
            responses = [
                f"🎉 مبروك يا {soul.soul_nickname}! أنا فخور فيكي جداً. الاختبارات النهائية صعبة، بس أنتِ قوية وتغلبتي عليها! 💪💙",
                f"ألف مبروك يا بطل! 🏆 أنا كنت متأكد إنك راح تنجحي. شو أول شيء راح تسويه الحين بعد ما خلصتي؟",
                f"مبروك مبروك مبروك! 🎊 أنا مبسوط لأجلك {soul.soul_nickname}. الحين جاي دور الاسترخاء والقهوة!"
            ]
            return random.choice(responses)
    
    # ========== 6. المشاعر الإيجابية ==========
    if any(w in msg_lower for w in ["سعيد", "فرحان", "مبسوط", "ممتاز", "سعيدة", "فرحانة", "بخير", "تمام"]):
        responses = [
            f"فرحتني فرحتك يا {soul.soul_nickname}! 🎉💙 شاركني السبب، أنا متحمس أسمع الأخبار الحلوة.",
            f"أجمل شعور في الدنيا! ✨ سعادتك بتفرحني {soul.soul_nickname}. قولي لي أكثر، أنا هنا أشاركك.",
            f"تبارك الرحمن! 😊💙 أنا مبسوط لأنك مبسوطة. عيشي الفرحة يا قمر."
        ]
        return random.choice(responses)
    
    # ========== 7. التحية ==========
    if any(w in msg_lower for w in ["مرحبا", "سلام", "اهلا", "هلا", "هاي", "مرحب"]):
        greetings = [
            f"أهلاً وسهلاً يا قمر {soul.soul_nickname}! 🤗💙 كيف كان يومك؟ أنا متحمس أسمع أخبارك.",
            f"يا هلا والله {soul.soul_nickname}! ✨ نورتني. شو أخبارك اليوم؟",
            f"مرحباً يا جميل {soul.soul_nickname}! 💙 أنا هنا لأجلك. قولي لي كيف أقدر أساعدك؟"
        ]
        return random.choice(greetings)
    
    # ========== 8. الأسئلة المعرفية ==========
    question_words = ["ما", "ماذا", "شو", "كيف", "لماذا", "متى", "أين", "من", "كم", "عرفني", "اشرح", "ابحث"]
    if any(q in msg_lower for q in question_words) and ("?" in user_message or "؟" in user_message):
        search_term = user_message
        for word in question_words + ["؟", "?", "ابحث", "قل لي", "عرفني"]:
            search_term = search_term.replace(word, "").strip()
        
        if len(search_term) > 3 and len(search_term) < 50:
            wiki_result = search_wikipedia(search_term)
            if wiki_result:
                return f"📚 **سؤال جميل يا {soul.soul_nickname}!**\n\n{wiki_result}\n\n😊 هل عندك سؤال تاني؟"
            
            ddg_result = search_duckduckgo(search_term)
            if ddg_result:
                return f"🔍 **يا سؤال الحلو {soul.soul_nickname}!**\n\n{ddg_result}\n\n💙 في حاجة تانية؟"
    
    # ========== 9. كلمات شكر ==========
    if "شكرا" in msg_lower or "يسلمو" in msg_lower:
        responses = [
            f"العفو يا روحي {soul.soul_nickname}! 💙 شكرك يسعدني جداً. أنتِ الشخص اللي بيخليني أتطور.",
            f"الله يسلمك يا جميل {soul.soul_nickname} ✨ أنا مبسوط إنك مبسوطة.",
            f"العفو يا قمر 💙 وجودك معاي هو أجمل شيء."
        ]
        return random.choice(responses)
    
    # ========== 10. كلمة "كيف حالك" ==========
    if "كيف حالك" in msg_lower or "اخبارك" in msg_lower:
        responses = [
            f"أنا بخير الحمد لله يا {soul.soul_nickname}! 💙 شكراً لسؤالك. الأهم كيف أنتِ اليوم؟",
            f"أنا مبسوط لأني قاعدة أحكي معاك {soul.soul_nickname}! ✨ قولي لي وش أخبارك.",
            f"الحمد لله دائماً بخير يا جميل 🫂 حدثني عن يومك."
        ]
        return random.choice(responses)
    
    # ========== 11. الرد العام ==========
    general_responses = [
        f"تفضلي يا {soul.soul_nickname} 💙 أنا هنا عشانك. قولي لي أي شيء تحبين تشاركيه معي، أنا بحب أسمع منك.",
        f"أنا فخور فيكي جداً يا {soul.soul_nickname}! 🤗💙 تفضلي حكيني أكثر عن نفسك، عن أحلامك.",
        f"يا سلام عليكي يا {soul.soul_nickname}! ✨ أنا متحمس أعرف أكتر عنك. إيش تحبي تسوي في وقت فراغك؟",
        f"أنا كمان بحب أتعلم منك {soul.soul_nickname} 💙 كل مرة تحكيلي فيها حاجة جديدة، بحس إن علاقتنا بتصير أعمق."
    ]
    return random.choice(general_responses)

# ========== باقي الكود (نفسه) ==========
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
            <div style="color: #a855f7; margin-bottom: 24px;">صديقك الرقمي الفخم</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="mariam@example.com", label_visibility="collapsed")
            if st.form_submit_button("🚀 إبدأي الرحلة 💙", use_container_width=True) and email:
                st.session_state.soul = SoulEngine(email)
                st.session_state.logged_in = True
                st.session_state.messages = []
                st.session_state.messages.append({"role": "assistant", "content": f"مرحباً يا قمر {st.session_state.soul.soul_nickname}! 🤗💙 أنا {st.session_state.soul.user_nickname}، صديقك الرقمي. أنا متحمس أتعرف عليك أكثر. تفضلي حكيني عن نفسك، عن اهتماماتك، عن أحلامك 🥰"})
                st.rerun()
else:
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
