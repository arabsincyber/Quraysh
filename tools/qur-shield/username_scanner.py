import re

def scan_username(username: str):
    print(f"\n[*] جاري فحص الحساب: {username}\n")
    
    # الكلمات المشبوهة في أسماء الحسابات
    suspicious_words = [
        "trading", "invest", "crypto", "bitcoin", "giveaway", 
        "free", "profit", "money", "rich", "winner", "prize",
        "support", "verify", "login", "update", "secure"
    ]
    
    found = []
    for word in suspicious_words:
        if word.lower() in username.lower():
            found.append(word)
    
    if found:
        print(f"  [⚠️] تحذير: الاسم يحتوي على كلمات مشبوهة: {', '.join(found)}")
        print("  [🚨] نتيجة: هذا الحساب قد يكون احتيالاً (Scam). لا تتفاعل معه!")
    else:
        print("  [✅] لم يتم اكتشاف كلمات مشبوهة في الاسم.")
    
    # نصائح أمنية
    print("\n  [💡] نصائح أمنية:")
    print("      - لا ترسل أي أموال أو معلومات شخصية.")
    print("      - تحقق من تاريخ إنشاء الحساب (الحسابات الجديدة مشبوهة).")
    print("      - إذا أرسل رابطاً، استخدم الخيار [9] لفحصه.")
    print("      - احظر وأبلغ عن الحساب فوراً.")
