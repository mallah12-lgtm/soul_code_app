import json
import os
from datetime import datetime
from collections import Counter
import re

class SoulEngine:
    
    def __init__(self, user_email):
        self.user_email = user_email
        self.user_id = user_email.replace('@', '_at_').replace('.', '_dot_')
        
        self.data_folder = "data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.profile_file = f"{self.data_folder}/{self.user_id}_profile.json"
        self.memory_file = f"{self.data_folder}/{self.user_id}_memories.json"
        
        self.interests = {}
        self.memories = []
        self.user_nickname = "Soul Code"
        self.soul_nickname = "صديقي"
        
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.interests = data.get("interests", {})
                self.user_nickname = data.get("user_nickname", "Soul Code")
                self.soul_nickname = data.get("soul_nickname", "صديقي")
        
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memories = json.load(f)
    
    def save_data(self):
        data = {
            "interests": self.interests,
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email,
            "last_update": datetime.now().isoformat()
        }
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def learn_from_conversation(self, user_message, ai_response):
        self.memories.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response
        })
        
        # استخراج كلمات مفتاحية
        words = user_message.split()
        for w in words:
            if len(w) > 4:
                self.interests[w] = self.interests.get(w, 0) + 1
        
        self.save_data()
    
    def set_user_nickname(self, nickname):
        self.user_nickname = nickname
        self.save_data()
    
    def set_soul_nickname(self, nickname):
        self.soul_nickname = nickname
        self.save_data()
    
    def get_user_summary(self):
        return {
            "total_conversations": len(self.memories),
            "interests_count": len(self.interests),
            "top_interests": sorted(self.interests.items(), key=lambda x: x[1], reverse=True)[:3],
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email
        }
    
    def get_welcome_message(self):
        return f"مرحباً يا قمر {self.soul_nickname}! 🤗💙 أنا {self.user_nickname}، صديقك الرقمي. أنا متحمس أتعرف عليك أكثر 🥰"
    
    def get_weekly_insights(self):
        if len(self.memories) < 5:
            return f"ما زلت أتعرف عليك يا {self.soul_nickname}. تحدث معي أكثر! 💙"
        return f"📊 تحدثنا {len(self.memories)} مرة حتى الآن! 💙"
    
    def get_personalized_suggestion(self):
        if self.interests:
            top = list(self.interests.keys())[0]
            return f"🌟 أنا لاحظت اهتمامك بـ '{top}'. استمري في التطور 💙"
        return "🌟 أخبريني عن اهتماماتك 💙"
