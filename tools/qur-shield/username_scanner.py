import re
import requests

def scan_username(username: str, platform: str = "tiktok"):
    print(f"\n[*] جاري فحص الحساب: {username} (المنصة: {platform})\n")
    
    # 1. فحص الكلمات المشبوهة
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
    
    # 2. التحقق من وجود الحساب (محاولة فتح الرابط)
    print(f"\n  [*] محاولة التحقق من وجود الحساب على {platform}...")
    urls = {
        "tiktok": f"https://www.tiktok.com/@{username}",
        "instagram": f"https://www.instagram.com/{username}/",
        "x": f"https://x.com/{username}"
    }
    
    if platform in urls:
        try:
            res = requests.get(urls[platform], timeout=10, allow_redirects=True)
            if res.status_code == 200:
                print(f"  [✅] الحساب موجود على {platform}.")
            else:
                print(f"  [❌] الحساب غير موجود أو محظور (كود: {res.status_code}).")
        except Exception as e:
            print(f"  [⚠️] لم نتمكن من التحقق: {str(e)[:50]}")
    else:
        print(f"  [⚠️] المنصة {platform} غير مدعومة حالياً.")

    # 3. نصائح أمنية
    print("\n  [💡] نصائح أمنية:")
    print("      - لا ترسل أي أموال أو معلومات شخصية.")
    print("      - تحقق من تاريخ إنشاء الحساب (الحسابات الجديدة مشبوهة).")
    print("      - إذا أرسل رابطاً، استخدم الخيار [9] لفحصه.")
    print("      - احظر وأبلغ عن الحساب فوراً.")
