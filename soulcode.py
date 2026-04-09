import json
import os
from datetime import datetime
import re

class SoulEngine:
    def __init__(self, user_email):
        self.user_email = user_email
        self.user_id = re.sub(r'[@.]', '_', user_email)
        
        self.data_folder = "data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.profile_file = os.path.join(self.data_folder, f"{self.user_id}_profile.json")
        self.memory_file = os.path.join(self.data_folder, f"{self.user_id}_memories.json")
        
        self.interests = {}
        self.memories = []
        self.user_nickname = "صديقي"
        self.soul_nickname = "Soul Code"
        
        self.load_data()

    def load_data(self):
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.interests = data.get("interests", {})
                    self.user_nickname = data.get("user_nickname", "صديقي")
                    self.soul_nickname = data.get("soul_nickname", "Soul Code")
            except: pass

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except: pass

    def save_data(self):
        profile_data = {
            "interests": self.interests,
            "user_nickname": self.user_nickname,
            "soul_nickname": self.soul_nickname,
            "user_email": self.user_email,
            "last_update": datetime.now().isoformat()
        }
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def learn_from_conversation(self, user_message, ai_response):
        self.memories.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response
        })
        
        clean_text = re.sub(r'[^\w\s]', '', user_message)
        words = clean_text.split()
        for w in words:
            if len(w) > 3:
                self.interests[w] = self.interests.get(w, 0) + 1
        
        self.save_data()

    def get_welcome_message(self):
        return f"مرحباً بك يا {self.user_nickname}! أنا {self.soul_nickname}، كيف يمكنني مساعدتك اليوم؟ 💙"

    def get_weekly_insights(self):
        return f"📊 لقد قمنا بتبادل {len(self.memories)} رسالة حتى الآن!"

    def get_personalized_suggestion(self):
        if self.interests:
            top_interest = max(self.interests, key=self.interests.get)
            return f"🌟 لاحظت اهتمامك بـ '{top_interest}'. هل ندردش عنه؟"
        return "🌟 أخبرني عن يومك 💙"
