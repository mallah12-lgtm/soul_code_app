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
        
        # تأكد من إنشاء مجلد data أولاً
        self.data_folder = "data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.profile_file = f"{self.data_folder}/{self.user_id}_profile.json"
        self.memory_file = f"{self.data_folder}/{self.user_id}_memories.json"
        
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
        self.preferred_language = "arabic"
        self.nationality = None
        self.user_nickname = "Soul Code"
        self.soul_nickname = "صديقي"
        
        self.profile = self.load_profile()
        self.memories = self.load_memories()
        
        self.user_nickname = self.profile.get("user_nickname", "Soul Code")
        self.soul_nickname = self.profile.get("soul_nickname", "صديقي")
        
        # الذاكرة المتقدمة
        self.context_stack = []
        self.user_personality = {
            "dominant_emotion": "neutral",
            "interests_depth": {},
            "growth_areas": [],
            "frequent_topics": [],
            "emotional_history": [],
            "important_events": [],
            "user_facts": {}
        }
        
        self.init_database()
        self.load_personality_profile()
    
    def sanitize_email(self, email):
        return email.replace('@', '_at_').replace('.', '_dot_')
    
    def detect_language(self, text):
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        if arabic_pattern.search(text):
            return "arabic"
        return "english"
    
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
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
            "preferred_language": "arabic",
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
        
        memory = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response,
            "keywords": self.extract_keywords(user_message),
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
            "context": user_message[:100]
        })
        
        self.save_all()
        return memory
    
    def extract_keywords(self, text):
        words = re.findall(r'\b\w+\b', text)
        return [w for w in words if len(w) > 4][:5]
    
    def get_user_summary(self):
        return {
            "total_conversations": len(self.memories),
            "interests_count": len(self.interests),
            "top_interests": sorted(self.interests.items(), key=lambda x: x[1], reverse=True)[:3],
            "preferred_language": self.preferred_language,
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email
        }
    
    def get_welcome_message(self):
        return f"مرحباً يا قمر {self.soul_nickname}! 🤗💙 أنا {self.user_nickname}، صديقك الرقمي. أنا متحمس أتعرف عليك أكثر 🥰"
    
    def get_weekly_insights(self):
        if len(self.memories) < 5:
            return f"ما زلت أتعرف عليك يا {self.soul_nickname}. تحدث معي أكثر! 💙"
        
        all_keywords = []
        for mem in self.memories[-20:]:
            all_keywords.extend(mem.get("keywords", []))
        
        common_topics = Counter(all_keywords).most_common(3)
        
        return f"""
📊 **نظرة أسبوعية من {self.user_nickname}:**

• أكثر المواضيع التي تهمك: {', '.join([t[0] for t in common_topics]) if common_topics else 'لم تكتشف بعد'}
• تحدثنا {len(self.memories)} مرة!

💡 أنا هنا لك دائماً يا {self.soul_nickname}
"""
    
    def get_personalized_suggestion(self):
        if self.interests:
            top = list(self.interests.keys())[0]
            return f"🌟 أنا لاحظت اهتمامك بـ '{top}'. هذا شيء رائع! استمري في التطور 💙"
        return "🌟 أنا فخور بتطورك معي يومًا بعد يوم. أخبريني عن اهتماماتك 💙"
    
    # ========== دوال قاعدة البيانات ==========
    
    def init_database(self):
        try:
            os.makedirs(self.data_folder, exist_ok=True)
            db_path = os.path.join(self.data_folder, 'learning.db')
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS conversations
                         (id INTEGER PRIMARY KEY,
                          user_message TEXT,
                          ai_response TEXT,
                          timestamp TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS learnings
                         (id INTEGER PRIMARY KEY,
                          fact TEXT,
                          timestamp TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
    
    def learn_fact(self, fact, source="conversation"):
        try:
            db_path = os.path.join(self.data_folder, 'learning.db')
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO learnings (fact, timestamp) VALUES (?, ?)''',
                      (fact, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_all_learnings(self):
        try:
            db_path = os.path.join(self.data_folder, 'learning.db')
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('SELECT fact FROM learnings ORDER BY timestamp DESC')
            facts = c.fetchall()
            conn.close()
            return [f[0] for f in facts]
        except:
            return []
    
    def save_personality_profile(self):
        try:
            profile_path = os.path.join(self.data_folder, f"{self.user_id}_personality.json")
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_personality, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_personality_profile(self):
        try:
            profile_path = os.path.join(self.data_folder, f"{self.user_id}_personality.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    self.user_personality = json.load(f)
        except:
            pass
    
    def analyze_message(self, message):
        return {"topic": "general", "sentiment": "neutral", "intent": "chatting", "facts": []}
    
    def save_conversation(self, user_msg, ai_msg, topic, sentiment):
        pass
