# app.py - SoulCode واجهة Dashboard عصري مع بحث ذكي
import streamlit as st
from soulcode import SoulEngine
import random
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Soul Code", page_icon="🧠", layout="wide")

# ========== CSS يجبر الوضع الداكن ويلغي تأثير النظام ==========
st.markdown("""
<style>
:root { color-scheme: dark only !important; }
html, body { background-color: #0a0a0f !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%) !important; }
[data-testid="stAppViewContainer"] { background-color: #0a0a0f !important; }
[data-testid="stSidebar"] { background-color: #0a0a0f !important; border-right: 1px solid #1e1e2e !important; }
p, h1, h2, h3, h4, h5, h6, label, span, div, .stMarkdown { color: #e8e8f0 !important; }
.stTextInput > div > div > input { background-color: #1e1e2a !important; color: #ffffff !important; border: 1px solid #3a3a4a !important; border-radius: 12px !important; }
.stTextInput > div > div > input:focus { border-color: #a855f7 !important; box-shadow: 0 0 0 2px rgba(168,85,247,0.2) !important; }
.stButton > button { background: linear-gradient(135deg, #a855f7, #6366f1) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 8px 20px !important; font-weight: bold !important; transition: all 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(168,85,247,0.3) !important; }
.stAlert { background-color: #1e1e2e !important; border: none !important; border-radius: 16px !important; }
.stAlert > div { color: #e8e8f0 !important; }
[data-testid="stMetric"] { background-color: #1a1a25 !important; border-radius: 16px !important; padding: 10px !important; }
[data-testid="stMetric"] label { color: #a855f7 !important; }
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container { padding-top: 20px !important; padding-bottom: 80px !important; }
</style>
""", unsafe_allow_html=True)

# ========== دوال البحث الذكي ==========
def search_duckduckgo(query):
    """البحث في DuckDuckGo (مجاني بدون مفتاح)"""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            snippets = soup.find_all('a', class_='result__snippet')
            
            search_results = []
            for i in range(min(3, len(results))):
                title = results[i].text if i < len(results) else ""
                link = results[i].get('href', '') if i < len(results) else ""
                snippet = snippets[i].text if i < len(snippets) else ""
                search_results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
            return search_results
    except Exception as e:
        print(f"Search error: {e}")
    return []

def search_wikipedia(query):
    """البحث في Wikipedia"""
    try:
        url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('extract'):
                return {
                    "title": data.get('title', query),
                    "summary": data.get('extract', '')[:500],
                    "link": data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }
    except:
        pass
    return None

def get_ai_like_response(user_message, soul):
    """رد ذكي مع بحث في المصادر"""
    
    # تحليل السؤال
    is_question = any(q in user_message for q in ["؟", "?", "شو", "ما", "كيف", "متى", "أين", "لماذا", "وين", "وش"])
    is_search_request = any(s in user_message.lower() for s in ["ابحث", "بحث", "قوقل", "تعريف", "معلومات عن", "أخبار"])
    
    # إذا كان طلب بحث، ابحث في الإنترنت
    if is_question or is_search_request:
        # استخراج كلمات البحث (احذف كلمات الاستفهام)
        search_term = user_message
        for word in ["شو", "ما", "كيف", "متى", "أين", "لماذا", "وين", "وش", "ابحث عن", "بحث عن", "معلومات عن"]:
            search_term = search_term.replace(word, "").strip()
        
        # أولاً: البحث في ويكيبيديا العربية
        wiki_result = search_wikipedia(search_term)
        if wiki_result:
            return f"""📚 **من ويكيبيديا: {wiki_result['title']}**

{wiki_result['summary']}

🔗 [اقرأ المزيد]({wiki_result['link']})

💡 هل تريد معرفة المزيد عن هذا الموضوع؟"""
        
        # ثانياً: البحث في DuckDuckGo
        search_results = search_duckduckgo(search_term)
        if search_results:
            response = f"🔍 **نتائج البحث عن '{search_term}':**\n\n"
            for i, result in enumerate(search_results[:2], 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   📝 {result['snippet'][:200]}...\n"
                response += f"   🔗 [رابط]({result['link']})\n\n"
            response += "✨ هل تريد مني البحث عن شيء أكثر تحديداً؟"
            return response
    
    # ردود محلية للأسئلة العامة
    responses = {
        r"مرحبا|سلام|اهلا": [
            f"مرحباً {soul.soul_nickname}! 🤗 كيف تشعر اليوم؟",
            f"أهلاً وسهلاً {soul.soul_nickname}! 💙 كيف أقدر أساعدك اليوم؟"
        ],
        r"كيف حالك|اخبارك": [
            f"أنا بخير الحمد لله {soul.soul_nickname}! شكراً لسؤالك 💙 الأهم كيف أنت؟",
            f"الحمد لله دائماً بخير لأني أتحدث معك {soul.soul_nickname}! 🫂"
        ],
        r"بخير|تمام|منيحة": [
            f"الحمد لله! فرحتني {soul.soul_nickname} 🎉 أخبرني وش اللي خلاك مبسوط؟",
            f"جميل! هذا يفرحني {soul.soul_nickname} ✨"
        ],
        r"حزين|تعبت|زعلان|تعبانه": [
            f"أنا آسف إنك تحس كذا {soul.soul_nickname} 🫂 أنا هنا معك. تفضل اشرحلي اللي في خاطرك.",
            f"أسمعك {soul.soul_nickname} 💙 لا تتردد تفضفض، أحياناً الكلام يخفف الحمل."
        ],
        r"اسمي مريم|أنا مريم": [
            f"تشرفت بمعرفتك يا مريم! ✨ أنتِ تدرسين علم بيانات، هذا رائع جداً!",
            f"أهلاً مريم! 🤗 أخبريني أكثر عن دراستك وأهدافك."
        ],
        r"علم بيانات|ذكاء اصطناعي|برمجة": [
            f"واو! هذا مجال رائع {soul.soul_nickname}! 🎓 الذكاء الاصطناعي هو مستقبل التكنولوجيا. هل تريدين معلومات عن مجالات معينة فيه؟",
            f"مجال مذهل! 🤖 فيه好多 فروع: تعلم الآلة، معالجة اللغة الطبيعية، رؤية الحاسوب. وش يثير اهتمامك أكثر؟"
        ],
        r"طور|تطوير|فخم|احترافي": [
            f"نفسي أكون فخم معاك {soul.soul_nickname}! 🚀 أنا أتطور معك كل يوم من خلال محادثاتنا.",
            f"هذا حلمي كمان {soul.soul_nickname}! 💪 مع كل سؤال، أنا أتعلم وأصير أذكى."
        ],
        r"شكرا|يسلمو": [
            f"العفو {soul.soul_nickname}! 💙 شكرك يسعدني.",
            f"الله يسلمك {soul.soul_nickname} ✨ أنتِ الشخص اللي بيخليني أتطور."
        ]
    }
    
    for pattern, response_list in responses.items():
        if re.search(pattern, user_message, re.IGNORECASE):
            return random.choice(response_list)
    
    # رد عام ذكي
    return f"أفهمك {soul.soul_nickname} 🤔 سؤالك عن '{user_message[:50]}' مهم. لو تسمحي، أقدر أبحث لك عن معلومات أكثر أو تشرحيلي أكثر عشان أفهمك بعمق؟ 💙"

# ========== تهيئة حالة الجلسة ==========
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "soul" not in st.session_state:
    st.session_state.soul = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== الشاشات ==========
def show_home():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 8px;">✨ Nurture Your Essence,<br>Decode Your Self</div>
        <div style="color: #a855f7; font-size: 14px;">✦ Soul Code - Your Digital Friend ✦</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: rgba(30, 30, 46, 0.6); border-radius: 24px; padding: 20px; transition: all 0.2s; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 16px;">
            <div style="font-size: 36px; margin-bottom: 12px;">🧠</div>
            <div style="font-size: 18px; font-weight: bold; color: #ffffff; margin-bottom: 8px;">Smart Search</div>
            <div style="font-size: 13px; color: #9ca3af;">أبحث في ويكيبيديا والإنترنت</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 30, 46, 0.6); border-radius: 24px; padding: 20px; transition: all 0.2s; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 16px;">
            <div style="font-size: 36px; margin-bottom: 12px;">💬</div>
            <div style="font-size: 18px; font-weight: bold; color: #ffffff; margin-bottom: 8px;">Deep Conversation</div>
            <div style="font-size: 13px; color: #9ca3af;">محادثة عميقة وتعلم مستمر</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.soul:
        summary = st.session_state.soul.get_user_summary()
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("💬 Conversations", summary['total_conversations'])
        with col_b:
            st.metric("❤️ Interests", summary['interests_count'])
        with col_c:
            st.metric("📊 Sessions", len(st.session_state.messages)//2)

def show_chat():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 28px; font-weight: bold; color: #ffffff;">💬 Soul Chat</div>
        <div style="color: #a855f7; font-size: 14px;">تحدث مع صديقك الرقمي - يستطيع البحث في الإنترنت!</div>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div style="background: linear-gradient(135deg, #2a2a3a, #222232); color: #e0e0e8; padding: 12px 18px; border-radius: 20px; margin: 8px 0 8px auto; max-width: 75%; text-align: right;">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background: linear-gradient(135deg, #1e2a2e, #162024); color: #c9e2e8; padding: 12px 18px; border-radius: 20px; margin: 8px auto 8px 0; max-width: 75%; border-left: 3px solid #a855f7;">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="💭 اكتب رسالتك هنا... (مثال: ما هو الذكاء الاصطناعي؟)", label_visibility="collapsed")
        submitted = st.form_submit_button("💫 Send", use_container_width=True)
        
        if submitted and user_input and st.session_state.soul:
            st.session_state.messages.append({"role": "user", "content": user_input})
            ai_response = get_ai_like_response(user_input, st.session_state.soul)
            st.session_state.soul.learn_from_conversation(user_input, ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()

def show_insights():
    if st.session_state.soul:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 28px; font-weight: bold; color: #ffffff;">📊 Insights</div>
            <div style="color: #a855f7; font-size: 14px;">رؤى عن شخصيتك وتطورك</div>
        </div>
        """, unsafe_allow_html=True)
        
        summary = st.session_state.soul.get_user_summary()
        
        if summary.get("dominant_emotion"):
            emotion_icon = "😊" if summary["dominant_emotion"] == "positive" else "🫂"
            st.info(f"**مشاعرك الغالبة:** {emotion_icon} {summary['dominant_emotion']}")
        
        if summary["top_interests"]:
            interests_text = ", ".join([f"• {i[0]}" for i in summary["top_interests"]])
            st.markdown(f"**🎯 اهتماماتك:**\n{interests_text}")
        
        if st.button("🔮 رؤى أسبوعية", use_container_width=True):
            st.info(st.session_state.soul.get_weekly_insights())
    else:
        st.info("✨ سجل الدخول أولاً لترى رؤى شخصيتك")

def show_profile():
    if st.session_state.soul:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 28px; font-weight: bold; color: #ffffff;">👤 Profile</div>
            <div style="color: #a855f7; font-size: 14px;">إعداداتك الشخصية</div>
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
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: rgba(18, 18, 30, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 24px;">
        <div>
            <div style="font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; background-clip: text; color: transparent;">🧠 SoulCode</div>
            <div style="font-size: 12px; color: #6b7280;">Nurture Your Essence, Decode Your Self</div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 40px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #a855f7, #6366f1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">{first_letter}</div>
            <span>{st.session_state.soul.soul_nickname}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: rgba(18, 18, 30, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 24px;">
        <div>
            <div style="font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; background-clip: text; color: transparent;">🧠 SoulCode</div>
            <div style="font-size: 12px; color: #6b7280;">Nurture Your Essence, Decode Your Self</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== المحتوى الرئيسي ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e, #161622); border-radius: 28px; padding: 40px; text-align: center; margin-top: 40px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 32px; font-weight: bold; color: #ffffff; margin-bottom: 16px;">✨ Welcome to Soul Code</div>
            <div style="color: #a855f7; font-size: 14px; margin-bottom: 32px;">Enter your email to continue your journey</div>
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
