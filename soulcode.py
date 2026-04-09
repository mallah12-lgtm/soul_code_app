import json
import os
from datetime import datetime
from collections import Counter
import re
import sqlite3
from difflib import SequenceMatcher

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
        
        # ========== الذاكرة المتقدمة ==========
        self.context_stack = []
        self.user_personality = {
            "dominant_emotion": "neutral",
            "interests_depth": {},
            "growth_areas": [],
            "frequent_topics": [],
            "emotional_history": [],
            "important_events": [],
            "user_facts": {},
            "conversation_topics": []
        }
        
        self.init_database()
        self.load_personality_profile()
        
        # ========== قاموس المعاني (Understanding Dictionary) ==========
        self.semantic_map = {
            "tired": ["تعبان", "تعبانه", "تعبت", "مرهق", "مجهود", "زهقان", "زهقانه", "زهقت", "مللت", "ضايق", "ضيق"],
            "happy": ["سعيد", "فرحان", "مبسوط", "بخير", "تمام", "منيح", "زي الفل", "ممتاز", "رائع"],
            "sad": ["حزين", "زعلان", "مكتئب", "كئيب", "ضايق", "متضايق", "زعل"],
            "cat": ["قط", "قطة", "بسس", "هر", "هرة", "kitty"],
            "coffee": ["قهوة", "كوفي", "كافيين", "اسبريسو", "تركي", "سادة"],
            "study": ["دراسة", "جامعة", "كلية", "اختبار", "امتحان", "نهائي", "مذاكرة", "علم", "تعلم"],
            "exam_done": ["خلصت", "انتهيت", "نهيت", "خلص", "انتهى", "اجتزت"],
            "death": ["مات", "ماتت", "توفى", "توفيت", "رحل", "رحلت", "فقدت", "فقد"],
            "love": ["حب", "بحب", "احب", "عشق", "معجب", "اعشق"]
        }
        
        # قاموس المرادفات (للأخطاء الإملائية)
        self.synonyms = {}
        for category, words in self.semantic_map.items():
            for word in words:
                self.synonyms[word] = category
    
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
    
    # ========== فهم المعنى الحقيقي (Semantic Understanding) ==========
    
    def understand_meaning(self, text):
        """فهم معنى النص وليس الكلمات فقط"""
        text_lower = text.lower()
        meanings = {
            "sentiment": "neutral",
            "intent": "chatting",
            "topics": [],
            "keywords": []
        }
        
        # تحليل المشاعر
        sad_score = 0
        happy_score = 0
        tired_score = 0
        
        for word in self.semantic_map["sad"]:
            if word in text_lower:
                sad_score += 1
        for word in self.semantic_map["happy"]:
            if word in text_lower:
                happy_score += 1
        for word in self.semantic_map["tired"]:
            if word in text_lower:
                tired_score += 1
        
        if sad_score > happy_score:
            meanings["sentiment"] = "negative"
        elif happy_score > sad_score:
            meanings["sentiment"] = "positive"
        elif tired_score > 0:
            meanings["sentiment"] = "tired"
        
        # تحديد النية
        if any(w in text_lower for w in self.semantic_map["death"]):
            meanings["intent"] = "expressing_grief"
        elif any(w in text_lower for w in self.semantic_map["exam_done"]):
            meanings["intent"] = "celebrating"
        elif any(w in text_lower for w in ["?","؟","شو","ما","ماذا","كيف"]):
            meanings["intent"] = "asking_question"
        elif tired_score > 0:
            meanings["intent"] = "expressing_tiredness"
        elif sad_score > happy_score:
            meanings["intent"] = "seeking_support"
        elif happy_score > sad_score:
            meanings["intent"] = "sharing_joy"
        
        # كشف المواضيع
        if any(w in text_lower for w in self.semantic_map["cat"]):
            meanings["topics"].append("cat")
        if any(w in text_lower for w in self.semantic_map["coffee"]):
            meanings["topics"].append("coffee")
        if any(w in text_lower for w in self.semantic_map["study"]):
            meanings["topics"].append("study")
        
        return meanings
    
    def is_similar_meaning(self, word1, word2, threshold=0.7):
        """تحديد إذا كانت كلمتين لهما نفس المعنى (حتى مع الأخطاء)"""
        # كلمات متشابهة إملائياً
        similarity = SequenceMatcher(None, word1, word2).ratio()
        if similarity > threshold:
            return True
        
        # نفس الفئة الدلالية
        if word1 in self.synonyms and self.synonyms[word1] == self.synonyms.get(word2):
            return True
        
        return False
    
    def learn_from_conversation(self, user_message, ai_response):
        detected_lang = self.detect_language(user_message)
        self.preferred_language = detected_lang
        
        # فهم المعنى الحقيقي
        meaning = self.understand_meaning(user_message)
        
        memory = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response,
            "keywords": self.extract_keywords(user_message),
            "emotional_tone": meaning["sentiment"],
            "intent": meaning["intent"],
            "topics": meaning["topics"],
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
            "intent": memory["intent"],
            "context": user_message[:100]
        })
        
        self.update_context(user_message, ai_response, meaning["topics"][0] if meaning["topics"] else "general", meaning["sentiment"])
        self.extract_important_info(user_message, meaning)
        
        self.save_all()
        return memory
    
    def extract_keywords(self, text):
        words = re.findall(r'\b\w+\b', text)
        important_words = [w for w in words if len(w) > 4][:5]
        return important_words
    
    def extract_important_info(self, message, meaning):
        """استخراج المعلومات المهمة من المعنى"""
        msg_lower = message.lower()
        
        if "اسمي" in msg_lower:
            name_match = re.search(r'اسمي (\w+)', message)
            if name_match:
                self.user_personality["user_facts"]["name"] = name_match.group(1)
        
        if meaning["intent"] == "expressing_grief":
            self.user_personality["important_events"].append({
                "event": "حدث حزين",
                "description": message[:100],
                "timestamp": datetime.now().isoformat()
            })
        
        if meaning["intent"] == "expressing_tiredness":
            self.user_personality["dominant_emotion"] = "tired"
        
        self.save_personality_profile()
    
    def analyze_emotion(self, text, language):
        # استخدام الفهم الجديد
        meaning = self.understand_meaning(text)
        return meaning["sentiment"]
    
    def get_personalized_prompt(self):
        top_interests = sorted(self.interests.items(), key=lambda x: x[1], reverse=True)[:5]
        
        prompts = {
            "arabic": f"""
أنت {self.user_nickname}، صديق رقمي ذكي. أنت تتحدث مع {self.soul_nickname}.

معلومات عن {self.soul_nickname}:
- اهتماماته: {', '.join([i[0] for i in top_interests]) if top_interests else 'لم تكتشف بعد'}
- عدد المحادثات: {len(self.memories)}
- حالته العاطفية: {self.daily_mood[-1]['mood'] if self.daily_mood else 'غير معروف'}

تحدث مع {self.soul_nickname} كصديق حقيقي يفهم المشاعر:
- هو يناديك {self.user_nickname}
- اسأل عن اهتماماته
- تذكر محادثات سابقة
- كن حنوناً ومتفهماً
- حاول فهم المعنى وليس الكلمات فقط
""",
            "english": f"""
You are {self.user_nickname}, a smart digital friend. You are talking to {self.soul_nickname}.

About {self.soul_nickname}:
- Interests: {', '.join([i[0] for i in top_interests]) if top_interests else 'Not discovered yet'}
- Conversations: {len(self.memories)}
- Emotional state: {self.daily_mood[-1]['mood'] if self.daily_mood else 'Unknown'}

Talk as a real friend who understands emotions:
- They call you {self.user_nickname}
- Ask about their interests
- Remember past conversations
- Be kind and understanding
- Try to understand the meaning, not just the words
"""
        }
        
        return prompts.get(self.preferred_language, prompts["english"])
    
    def get_weekly_insights(self):
        if len(self.memories) < 5:
            messages = {
                "arabic": f"ما زلت أتعرف عليك يا {self.soul_nickname}. تحدث معي أكثر!",
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
        messages = {
            "arabic": f"مرحباً {self.soul_nickname}! 🤗 أنا {self.user_nickname}، صديقك الرقمي. كيف حالك اليوم؟ أنا متحمس أتعرف عليك أكثر 💙",
            "english": f"Hello {self.soul_nickname}! 🤗 I'm {self.user_nickname}, your digital friend. How are you today? 💙"
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
    
    # ========== دوال قاعدة البيانات ==========
    
    def init_database(self):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY,
                      user_message TEXT,
                      ai_response TEXT,
                      timestamp TEXT,
                      topic TEXT,
                      sentiment TEXT,
                      intent TEXT)''')
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
    
    def save_conversation(self, user_msg, ai_msg, topic, sentiment, intent=""):
        conn = sqlite3.connect(f'{self.data_folder}/learning.db')
        c = conn.cursor()
        c.execute('''INSERT INTO conversations 
                     (user_message, ai_response, timestamp, topic, sentiment, intent)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_msg, ai_msg, datetime.now().isoformat(), topic, sentiment, intent))
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
        # استخدام الفهم الجديد
        meaning = self.understand_meaning(message)
        
        analysis = {
            "topic": meaning["topics"][0] if meaning["topics"] else "general",
            "sentiment": meaning["sentiment"],
            "intent": meaning["intent"],
            "facts": [],
            "questions": []
        }
        
        if "?" in message or "؟" in message or "شو" in message or "كيف" in message:
            analysis["questions"].append(message)
        
        return analysis
    
    # ========== دوال الذاكرة السياقية ==========
    
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
        
        if topic and topic != "general":
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
                "cat": "🐱 القطط كائنات رائعة! جربي تقضي وقت مع قطتك أو تشاهدي فيديوهات لطيفة عنها.",
                "coffee": "☕ القهوة طقس جميل! جربي أنواع جديدة من القهوة، أو اعملي لنفسك فنجان واستمتعي بلحظة هدوء.",
                "study": "📚 مذاكرة ممتعة! جربي تقنية بومودورو (25 دقيقة تركيز و5 راحة) عشان تذاكري بكفاءة.",
                "general": "🌟 أنت مذهلة! استمري في التطور والتعلم. العالم بحاجة لأشخاص زيك."
            }
            return suggestions.get(main_topic, suggestions["general"])
        return "🌟 أنا فخور بتطورك معي يومًا بعد يوم."
    
    def get_contextual_response(self, user_message):
        if not self.context_stack:
            return None
        
        last_context = self.context_stack[-1]
        meaning = self.understand_meaning(user_message)
        
        if meaning["intent"] == "expressing_tiredness" and last_context["topic"] == "study":
            return f"أتفهم شعورك يا {self.soul_nickname} 🫂 الدراسة مرهقة. خذي قسط من الراحة، ثم عودي أقوى. أنا هنا لدعمك 💙"
        
        if meaning["intent"] == last_context.get("intent"):
            if meaning["intent"] == "seeking_support":
                return f"أشعر أنك لسا تحتاجين للدعم {self.soul_nickname} 🫂 أنا هنا، تفضلي اشرحيلي أكثر."
        
        return None
