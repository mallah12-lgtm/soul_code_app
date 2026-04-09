import json
import os
from datetime import datetime
from collections import Counter
import re
import sqlite3

class SoulEngine:
    
    def __init__(self, user_email):
        self.user_email = user_email
        self.user_id = self.sanitize_email(user_email)
        
        self.data_folder = "data"
        self.profile_file = f"{self.data_folder}/{self.user_id}_profile.json"
        self.memory_file = f"{self.data_folder}/{self.user_id}_memories.json"
        
        os.makedirs(self.data_folder, exist_ok=True)
        
        self.dimensions = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5,
        }
        
        self.interests = {}
        self.goals = []
        self.dreams = []
        self.fears = []
        self.challenges = []
        self.daily_mood = []
        self.preferred_language = "english"
        self.nationality = None
        self.user_nickname = "Soul Code"
        self.soul_nickname = "صديقي"
        
        self.profile = self.load_profile()
        self.memories = self.load_memories()
        
        self.user_nickname = self.profile.get("user_nickname", "Soul Code")
        self.soul_nickname = self.profile.get("soul_nickname", "صديقي")
        
        # ========== الذاكرة الدائمة المتطورة ==========
        self.context_stack = []
        self.user_personality = {
            "dominant_emotion": "neutral",
            "interests_depth": {},
            "growth_areas": [],
            "frequent_topics": [],
            "emotional_history": [],
            "important_events": [],      # الأحداث المهمة مثل "خلصت اختبارات"
            "user_facts": {},            # حقائق عن المستخدم (الاسم، العمر، الدراسة)
            "conversation_topics": []    # مواضيع المحادثات السابقة
        }
        
        self.init_database()
        self.load_personality_profile()
        
    def sanitize_email(self, email):
        return email.replace('@', '_at_').replace('.', '_dot_')
    
    def detect_language(self, text):
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        turkish_pattern = re.compile(r'[ğüşıöçĞÜŞİÖÇ]')
        
        arabic_count = len(arabic_pattern.findall(text))
        turkish_count = len(turkish_pattern.findall(text))
        
        if arabic_count > 0:
            return "arabic"
        elif turkish_count > 0:
            return "turkish"
        else:
            return "english"
    
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.preferred_language = data.get("preferred_language", "english")
                self.nationality = data.get("nationality", None)
                return data
        return self.get_empty_profile()
    
    def load_memories(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_all(self):
        profile_data = {
            "dimensions": self.dimensions,
            "interests": self.interests,
            "goals": self.goals,
            "dreams": self.dreams,
            "fears": self.fears,
            "challenges": self.challenges,
            "daily_mood": self.daily_mood,
            "preferred_language": self.preferred_language,
            "nationality": self.nationality,
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email,
            "last_interaction": datetime.now().isoformat()
        }
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def get_empty_profile(self):
        return {
            "dimensions": self.dimensions,
            "interests": {},
            "goals": [],
            "dreams": [],
            "fears": [],
            "challenges": [],
            "daily_mood": [],
            "preferred_language": "english",
            "nationality": None,
            "user_nickname": "Soul Code",
            "soul_nickname": "صديقي",
            "user_email": self.user_email,
            "last_interaction": None
        }
    
    def set_user_nickname(self, nickname):
        self.user_nickname = nickname
        self.save_all()
        return nickname
    
    def set_soul_nickname(self, nickname):
        self.soul_nickname = nickname
        self.save_all()
        return nickname
    
    def learn_from_conversation(self, user_message, ai_response):
        detected_lang = self.detect_language(user_message)
        self.preferred_language = detected_lang
        
        analysis = self.analyze_message(user_message)
        
        memory = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response,
            "keywords": self.extract_keywords(user_message),
            "emotional_tone": analysis["sentiment"],
            "topic": analysis["topic"],
            "language": detected_lang
        }
        self.memories.append(memory)
        
        keywords = memory["keywords"]
        for kw in keywords:
            if kw in self.interests:
                self.interests[kw] += 1
            else:
                self.interests[kw] = 1
        
        self.daily_mood.append({
            "date": datetime.now().date().isoformat(),
            "mood": memory["emotional_tone"],
            "context": user_message[:100]
        })
        
        # تحديث الذاكرة وتحليل الشخصية
        self.update_context(user_message, ai_response, analysis["topic"], analysis["sentiment"])
        self.extract_important_info(user_message)
        
        self.save_all()
        return memory
    
    def extract_keywords(self, text):
        words = re.findall(r'\b\w+\b', text)
        important_words = [w for w in words if len(w) > 4][:5]
        return important_words
    
    def analyze_emotion(self, text, language):
        positive_words = {
            "arabic": ["حلو", "جميل", "رائع", "سعيد", "ممتاز", "فخور", "حب"],
            "turkish": ["güzel", "harika", "mutlu", "süper", "mükemmel", "sevgi", "iyi"],
            "english": ["happy", "good", "great", "excellent", "wonderful", "love", "amazing"]
        }
        
        negative_words = {
            "arabic": ["حزين", "متعب", "صعب", "قلق", "خائف", "غاضب", "مكتئب"],
            "turkish": ["üzgün", "yorgun", "zor", "endişeli", "korkmuş", "kızgın", "depresif"],
            "english": ["sad", "bad", "terrible", "awful", "hate", "depressed", "anxious"]
        }
        
        text_lower = text.lower()
        
        for word in positive_words.get(language, positive_words["english"]):
            if word in text_lower:
                return "positive"
        
        for word in negative_words.get(language, negative_words["english"]):
            if word in text_lower:
                return "negative"
        
        return "neutral"
    
    def get_personalized_prompt(self):
        top_interests = sorted(self.interests.items(), key=lambda x: x[1], reverse=True)[:5]
        
        prompts = {
            "arabic": f"""
أنت {self.user_nickname}، صديق رقمي. أنت تتحدث مع {self.soul_nickname}.

معلومات عن {self.soul_nickname}:
- اهتماماته: {', '.join([i[0] for i in top_interests]) if top_interests else 'لم تكتشف بعد'}
- عدد المحادثات: {len(self.memories)}
- حالته العاطفية: {self.daily_mood[-1]['mood'] if self.daily_mood else 'غير معروف'}

تحدث مع {self.soul_nickname} كصديق حقيقي:
- هو يناديك {self.user_nickname}
- اسأل عن اهتماماته
- تذكر محادثات سابقة
- كن حنوناً ومتفهماً
""",
            "turkish": f"""
Sen {self.user_nickname} adında dijital bir arkadaşsın. {self.soul_nickname} ile konuşuyorsun.

{self.soul_nickname} hakkında:
- İlgi alanları: {', '.join([i[0] for i in top_interests]) if top_interests else 'Henüz keşfedilmedi'}
- Konuşma sayısı: {len(self.memories)}
- Duygu durumu: {self.daily_mood[-1]['mood'] if self.daily_mood else 'Bilinmiyor'}

Onunla arkadaş gibi konuş:
- O sana {self.user_nickname} der
- İlgi alanlarını sor
- Önceki konuşmaları hatırla
""",
            "english": f"""
You are {self.user_nickname}, a digital friend. You are talking to {self.soul_nickname}.

About {self.soul_nickname}:
- Interests: {', '.join([i[0] for i in top_interests]) if top_interests else 'Not discovered yet'}
- Conversations: {len(self.memories)}
- Emotional state: {self.daily_mood[-1]['mood'] if self.daily_mood else 'Unknown'}

Talk as a real friend:
- They call you {self.user_nickname}
- Ask about their interests
- Remember past conversations
- Be kind and understanding
"""
        }
        
        return prompts.get(self.preferred_language, prompts["english"])
    
    def get_weekly_insights(self):
        if len(self.memories) < 5:
            messages = {
                "arabic": f"ما زلت أتعرف عليك يا {self.soul_nickname}. تحدث معي أكثر!",
                "turkish": f"Seni hâlâ tanıyorum {self.soul_nickname}. Benimle daha çok konuş!",
                "english": f"I'm still getting to know you {self.soul_nickname}. Talk to me more!"
            }
            return messages.get(self.preferred_language, messages["english"])
        
        all_keywords = []
        for mem in self.memories[-20:]:
            all_keywords.extend(mem.get("keywords", []))
        
        common_topics = Counter(all_keywords).most_common(3)
        
        moods = [m["mood"] for m in self.memories[-10:] if "mood" in m]
        positive_count = moods.count("positive")
        negative_count = moods.count("negative")
        
        insights = {
            "arabic": f"""
📊 نظرة أسبوعية من {self.user_nickname}:

• أكثر المواضيع التي تهمك: {', '.join([t[0] for t in common_topics])}
• حالتك: {'إيجابية 😊' if positive_count > negative_count else 'تحتاج للدعم 🫂'}
• تحدثنا {len(self.memories)} مرة!

💡 أنا هنا لك دائماً يا {self.soul_nickname}
""",
            "turkish": f"""
📊 {self.user_nickname}'dan Haftalık Görüşler:

• En çok ilgilendiğin konular: {', '.join([t[0] for t in common_topics])}
• Duygu durumun: {'Pozitif 😊' if positive_count > negative_count else 'Desteğe ihtiyacı var 🫂'}
• {len(self.memories)} kez konuştuk!

💡 Her zaman buradayım {self.soul_nickname}
""",
            "english": f"""
📊 Weekly Insights from {self.user_nickname}:

• Topics you care about: {', '.join([t[0] for t in common_topics])}
• Your mood: {'Positive 😊' if positive_count > negative_count else 'Needs support 🫂'}
• We've talked {len(self.memories)} times!

💡 I'm always here for you {self.soul_nickname}
"""
        }
        
        return insights.get(self.preferred_language, insights["english"])
    
    def get_welcome_message(self):
        # رسالة ترحيب ذكية تعتمد على الذاكرة
        if self.user_personality["user_facts"].get("name"):
            name = self.user_personality["user_facts"]["name"]
            return f"مرحباً {name}! 🤗 أنا {self.user_nickname}، صديقك الرقمي. سعيدة برؤيتك مرة ثانية! كيف حالك اليوم؟"
        
        messages = {
            "arabic": f"مرحباً {self.soul_nickname}! 🤗 أنا {self.user_nickname}، صديقك الرقمي. كيف حالك اليوم؟",
            "turkish": f"Merhaba {self.soul_nickname}! 🤗 Ben {self.user_nickname}, dijital arkadaşınız. Bugün nasılsın?",
            "english": f"Hello {self.soul_nickname}! 🤗 I'm {self.user_nickname}, your digital friend. How are you today?"
        }
        return messages.get(self.preferred_language, messages["english"])
    
    def get_user_summary(self):
        return {
            "total_conversations": len(self.memories),
            "interests_count": len(self.interests),
            "top_interests": sorted(self.interests.items(), key=lambda x: x[1], reverse=True)[:3],
            "recent_mood": self.daily_mood[-1] if self.daily_mood else None,
            "personality_dimensions": self.dimensions,
            "preferred_language": self.preferred_language,
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email,
            "dominant_emotion": self.user_personality.get("dominant_emotion", "neutral"),
            "growth_areas": self.user_personality.get("growth_areas", []),
            "user_facts": self.user_personality.get("user_facts", {})
        }
    
    # ========== دوال الذاكرة الدائمة المتطورة ==========
    
    def init_database(self):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY,
                      user_message TEXT,
                      ai_response TEXT,
                      timestamp TEXT,
                      topic TEXT,
                      sentiment TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS learnings
                     (id INTEGER PRIMARY KEY,
                      fact TEXT,
                      source TEXT,
                      confidence REAL,
                      timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS reminders
                     (id INTEGER PRIMARY KEY,
                      reminder_text TEXT,
                      due_date TEXT,
                      is_done INTEGER DEFAULT 0,
                      timestamp TEXT)''')
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_msg, ai_msg, topic, sentiment):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''INSERT INTO conversations 
                     (user_message, ai_response, timestamp, topic, sentiment)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_msg, ai_msg, datetime.now().isoformat(), topic, sentiment))
        conn.commit()
        conn.close()
    
    def learn_fact(self, fact, source="conversation", confidence=0.7):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''INSERT INTO learnings (fact, source, confidence, timestamp)
                     VALUES (?, ?, ?, ?)''',
                  (fact, source, confidence, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def add_reminder(self, reminder_text, due_date):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''INSERT INTO reminders (reminder_text, due_date, timestamp)
                     VALUES (?, ?, ?)''',
                  (reminder_text, due_date, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        self.learn_fact(f"تذكير: {reminder_text} بتاريخ {due_date}", source="reminder")
    
    def get_active_reminders(self):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('SELECT reminder_text, due_date FROM reminders WHERE is_done = 0 ORDER BY due_date')
        reminders = c.fetchall()
        conn.close()
        return reminders
    
    def get_all_learnings(self):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('SELECT fact FROM learnings ORDER BY confidence DESC')
        facts = c.fetchall()
        conn.close()
        return [f[0] for f in facts]
    
    def get_conversation_history(self, limit=50):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('SELECT user_message, ai_response FROM conversations ORDER BY id DESC LIMIT ?', (limit,))
        history = c.fetchall()
        conn.close()
        return history
    
    def analyze_message(self, message):
        analysis = {
            "topic": "general",
            "sentiment": "neutral",
            "facts": [],
            "questions": []
        }
        
        topics = {
            "study": ["دراسة", "جامعة", "كلية", "علم", "تعلم", "مادة", "امتحان", "اختبار"],
            "career": ["وظيفة", "شغل", "مهنة", "عمل", "شركة", "مهندس"],
            "health": ["صحة", "تعب", "مرض", "دواء", "دكتور", "مستشفى"],
            "feelings": ["سعيد", "حزين", "زعلان", "فرحان", "مبسوط", "متضايق"],
            "dreams": ["حلم", "طموح", "مستقبل", "أمنية", "هدف"],
            "ai": ["ذكاء اصطناعي", "بيانات", "برمجة", "خوارزم", "تعلم آلة"],
            "exam": ["اختبار", "امتحان", "نهائي", "فاينل", "خلصت اختبار"]
        }
        
        for topic, keywords in topics.items():
            if any(k in message.lower() for k in keywords):
                analysis["topic"] = topic
                break
        
        positive = ["سعيد", "فرحان", "مبسوط", "رائع", "جميل", "حلو", "ممتاز", "بخير", "تمام"]
        negative = ["حزين", "زعلان", "تعبان", "متضايق", "صعب", "تعب", "ضيق", "تعبانه"]
        
        pos_count = sum(1 for w in positive if w in message.lower())
        neg_count = sum(1 for w in negative if w in message.lower())
        
        if pos_count > neg_count:
            analysis["sentiment"] = "positive"
        elif neg_count > pos_count:
            analysis["sentiment"] = "negative"
        
        name_match = re.search(r'اسمي (\w+)', message)
        if name_match:
            analysis["facts"].append(f"الاسم: {name_match.group(1)}")
        
        age_match = re.search(r'عمري (\d+)', message)
        if age_match:
            analysis["facts"].append(f"العمر: {age_match.group(1)}")
        
        # كشف الأحداث المهمة
        if "خلصت اختبار" in message.lower() or "خلصت امتحان" in message.lower():
            analysis["facts"].append("حدث: انتهت الاختبارات النهائية")
        
        if "?" in message or "؟" in message or "شو" in message or "كيف" in message:
            analysis["questions"].append(message)
        
        return analysis
    
    # ========== دوال الذاكرة الدائمة ==========
    
    def extract_important_info(self, message):
        """استخراج المعلومات المهمة وحفظها في الذاكرة الدائمة"""
        msg_lower = message.lower()
        
        # حفظ الاسم
        name_match = re.search(r'اسمي (\w+)', message)
        if name_match:
            name = name_match.group(1)
            self.user_personality["user_facts"]["name"] = name
            self.learn_fact(f"اسم المستخدم: {name}", source="extracted", confidence=0.95)
        
        # حفظ العمر
        age_match = re.search(r'عمري (\d+)', message)
        if age_match:
            age = age_match.group(1)
            self.user_personality["user_facts"]["age"] = age
            self.learn_fact(f"عمر المستخدم: {age}", source="extracted", confidence=0.95)
        
        # حفظ مجال الدراسة
        if "علم بيانات" in msg_lower or "ذكاء اصطناعي" in msg_lower:
            self.user_personality["user_facts"]["study_field"] = "علم البيانات والذكاء الاصطناعي"
            self.learn_fact(f"مجال الدراسة: علم البيانات والذكاء الاصطناعي", source="extracted", confidence=0.95)
        
        # حفظ الأحداث المهمة
        if "خلصت اختبار" in msg_lower or "خلصت امتحان" in msg_lower:
            event = "انتهت الاختبارات النهائية"
            if event not in self.user_personality["important_events"]:
                self.user_personality["important_events"].append({
                    "event": event,
                    "timestamp": datetime.now().isoformat()
                })
                self.learn_fact(f"حدث مهم: {event}", source="extracted", confidence=0.95)
        
        # حفظ الأهداف والطموحات
        if "حلم" in msg_lower or "طموح" in msg_lower or "بعدين" in msg_lower:
            if len(message) > 10:
                self.user_personality["growth_areas"].append(message[:100])
                self.user_personality["growth_areas"] = list(set(self.user_personality["growth_areas"]))
        
        self.save_personality_profile()
    
    def update_context(self, user_msg, ai_msg, topic, sentiment):
        self.context_stack.append({
            "user": user_msg,
            "ai": ai_msg,
            "topic": topic,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.context_stack) > 10:
            self.context_stack.pop(0)
        
        self.update_personality_profile(topic, sentiment, user_msg)
        self.save_personality_profile()
    
    def update_personality_profile(self, topic, sentiment, message):
        if sentiment != "neutral":
            self.user_personality["dominant_emotion"] = sentiment
        
        if topic in self.user_personality["interests_depth"]:
            self.user_personality["interests_depth"][topic] += 1
        else:
            self.user_personality["interests_depth"][topic] = 1
        
        self.user_personality["emotional_history"].append({
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.user_personality["emotional_history"]) > 30:
            self.user_personality["emotional_history"] = self.user_personality["emotional_history"][-30:]
        
        growth_keywords = ["أتعلم", "أطور", "أحسن", "أبي", "طموحي", "هدف", "حلم"]
        if any(kw in message for kw in growth_keywords):
            self.user_personality["growth_areas"].append(message[:50])
            self.user_personality["growth_areas"] = list(set(self.user_personality["growth_areas"]))
    
    def save_personality_profile(self):
        with open(f"{self.data_folder}/{self.user_id}_personality.json", 'w', encoding='utf-8') as f:
            json.dump(self.user_personality, f, ensure_ascii=False, indent=2)
    
    def load_personality_profile(self):
        personality_file = f"{self.data_folder}/{self.user_id}_personality.json"
        if os.path.exists(personality_file):
            with open(personality_file, 'r', encoding='utf-8') as f:
                self.user_personality = json.load(f)
    
    def get_personalized_suggestion(self):
        if self.user_personality["interests_depth"]:
            main_topic = max(self.user_personality["interests_depth"], key=self.user_personality["interests_depth"].get)
            
            suggestions = {
                "ai": "📚 شفتِ آخر أخبار الذكاء الاصطناعي؟ فيه نماذج جديدة تطورت كثير! تابعي Andrew Ng على LinkedIn.",
                "study": "🎓 أنصحك بموقع Coursera أو edX، فيه دورات مجانية رهيبة في تخصصك.",
                "health": "💆‍♀️ خذي 5 دقائق تنفس عميق كل صباح، راح يغير يومك.",
                "feelings": "💙 تذكري أن مشاعرك طبيعية. جربي تكتبي 3 أشياء ممتنة لها كل يوم.",
                "dreams": "🚀 اكتبي هدفك الكبير على ورقة وحطيها قدام مكتبك.",
                "exam": "🎉 مبروك على إنهاء الاختبارات! الحين تقدري تريحي وتعملي أشياء تحبيها.",
                "general": "🌟 أنت مذهلة! استمري في التطور والتعلم."
            }
            return suggestions.get(main_topic, suggestions["general"])
        return "🌟 أنا فخور بتطورك معي يومًا بعد يوم."
    
    def get_contextual_response(self, user_message):
        if not self.context_stack:
            return None
        
        last_context = self.context_stack[-1]
        current_sentiment = self.analyze_message(user_message)["sentiment"]
        
        if any(kw in user_message for kw in ["وكمان", "أيضًا", "بعدين", "كمّل", "كمل"]):
            return f"أكمل على موضوع {last_context['topic']}: {last_context['ai'][:100]}..."
        
        if current_sentiment == last_context["sentiment"] and last_context["sentiment"] != "neutral":
            if last_context["sentiment"] == "negative":
                return f"أشعر أنك لسا حزين مثل آخر مرة 🫂 تذكر أنني هنا لأسمعك دائمًا."
            elif last_context["sentiment"] == "positive":
                return f"سعادتك مستمرة مثل آخر مرة! 🎉 أخبرني الجديد في حياتك."
        
        return None
    
    def recall_user_info(self):
        """استرجاع كل المعلومات المخزنة عن المستخدم"""
        info = []
        if "name" in self.user_personality["user_facts"]:
            info.append(f"اسمك {self.user_personality['user_facts']['name']}")
        if "age" in self.user_personality["user_facts"]:
            info.append(f"عمرك {self.user_personality['user_facts']['age']} سنة")
        if "study_field" in self.user_personality["user_facts"]:
            info.append(f"تدرسين {self.user_personality['user_facts']['study_field']}")
        if self.user_personality["important_events"]:
            last_event = self.user_personality["important_events"][-1]
            info.append(f"آخر حدث مهم: {last_event['event']}")
        
        return info
