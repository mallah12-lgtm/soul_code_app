import json
import os
from datetime import datetime
import re

class SoulEngine:
    def __init__(self, user_email):
        self.user_email = user_email
        # تنظيف الإيميل لاستخدامه كاسم ملف
        self.user_id = re.sub(r'[@.]', '_', user_email)
        
        self.data_folder = "data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.profile_file = os.path.join(self.data_folder, f"{self.user_id}_profile.json")
        self.memory_file = os.path.join(self.data_folder, f"{self.user_id}_memories.json")
        
        self.interests = {}
        self.memories = []
        self.user_nickname = "صديقي" # اسم المستخدم
        self.soul_nickname = "Soul Code" # اسم البرنامج
        
        self.load_data()

    def learn_from_conversation(self, user_message, ai_response):
        self.memories.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response
        })
        
        # تحسين استخراج الكلمات: إزالة علامات الترقيم وتحويلها لقائمة
        clean_text = re.sub(r'[^\w\s]', '', user_message)
        words = clean_text.split()
        
        for w in words:
            if len(w) > 3: # الكلمات العربية المفيدة غالباً > 3 حروف
                self.interests[w] = self.interests.get(w, 0) + 1
        
        self.save_data()

    def get_personalized_suggestion(self):
        if self.interests:
            # جلب الأكثر تكراراً وليس أول كلمة فقط
            top_interest = max(self.interests, key=self.interests.get)
            return f"🌟 لاحظت أننا تحدثنا كثيراً عن '{top_interest}'. هل تود التعمق في هذا الموضوع؟ 💙"
        return "🌟 أخبرني عن اهتماماتك لأتعرف عليك أكثر 💙"

    # باقي الدوال تعمل بشكل جيد...
