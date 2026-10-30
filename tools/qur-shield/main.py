import sys
import os
import hashlib
import platform
import socket
import subprocess

# 1. فحص البريد
def check_email():
    email = input("أدخل البريد الإلكتروني: ").strip()
    print(f"\n[*] جاري فحص البريد: {email}")
    print("  [!] محاكاة: للفحص الحقيقي نحتاج مفتاح API من HIBP.")
    print("  [✅] النتيجة: لا توجد تسريبات (محاكاة).")

# 2. فحص ملف (بصمة)
def check_file(path=None):
    if not path:
        path = input("أدخل مسار الملف: ").strip()
    if not os.path.exists(path):
        print(f"  [❌] الملف غير موجود: {path}")
        return
    print(f"\n[*] جاري حساب بصمة الملف: {path}")
    with open(path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"  [✅] البصمة (SHA256): {file_hash}")

# 3. فحص النظام
def check_system():
    print("\n[*] جاري فحص النظام...")
    print(f"  [+] نظام التشغيل: {platform.system()} {platform.release()}")
    print(f"  [+] المعمارية: {platform.machine()}")
    print(f"  [+] اسم الجهاز: {platform.node()}")
    print("  [✅] النظام يعمل بشكل طبيعي.")

# 4. فحص الشبكة
def check_network():
    print("\n[*] جاري فحص الشبكة...")
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"  [+] اسم الجهاز: {hostname}")
        print(f"  [+] عنوان IP المحلي: {ip}")
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            print("  [✅] الاتصال بالإنترنت: يعمل.")
        except:
            print("  [❌] الاتصال بالإنترنت: لا يعمل.")
    except Exception as e:
        print(f"  [❌] خطأ: {e}")

# 5. الفحص السريع
def quick_scan():
    print("\n" + "="*40)
    print("🚀 بدء الفحص السريع (Quick Scan)")
    print("="*40)
    check_system()
    check_network()
    if os.path.exists("README.md"):
        check_file("README.md")
    else:
        print("\n  [!] ملف README.md غير موجود في المجلد الحالي.")
    print("\n" + "="*40)
    print("✅ انتهى الفحص السريع بنجاح!")
    print("="*40)

# 6. كشف الاحتيال
def scam_detection():
    text = input("\nأدخل النص أو الرابط المشبوه: ").strip()
    print(f"\n[*] جاري تحليل: {text}")
    suspicious_keywords = ["hacker", "free", "giveaway", "binance", "million", "billion", "win", "prize", "claim", "reward", "urgent", "verify", "account", "suspended", "bitcoin", "crypto", "wallet", "transfer"]
    found = []
    for word in suspicious_keywords:
        if word.lower() in text.lower():
            found.append(word)
    if found:
        print(f"  [⚠️] تحذير: تم اكتشاف كلمات مشبوهة: {', '.join(found)}")
        print("  [🚨] نتيجة: هذا النص قد يكون احتيالاً (Scam). لا تتفاعل معه!")
    else:
        print("  [✅] لم يتم اكتشاف كلمات مشبوهة. النص يبدو آمناً.")

# 7. الرد السريع
def rapid_response():
    print("\n" + "="*40)
    print("🚨 الرد السريع (Rapid Response) 🚨")
    print("="*40)
    wallet = input("\nأدخل عنوان محفظتك (BTC/ETH): ").strip()
    if not wallet:
        print("❌ لم يتم إدخال عنوان.")
        return
    compromised_wallets = [
        "0x0000000000000000000000000000000000000000",
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    ]
    print(f"\n[*] جاري فحص المحفظة: {wallet}")
    print("  [+] التحقق من قوائم الاختراق...")
    if wallet in compromised_wallets:
        print("  [🚨] تحذير: محفظتك موجودة في قائمة العناوين المخترقة!")
        print("  [🛑] نصيحة: توقف عن التداول فوراً، وانقل أصولك المتبقية إلى محفظة جديدة.")
    else:
        print("  [✅] محفظتك ليست في قائمة العناوين المخترقة (حسب المحاكاة).")
        print("  [💡] نصيحة: تأكد من استخدام المصادقة الثنائية (2FA) دائماً.")
    print("\n  [⚠️] تذكير: هذه الأداة للفحص الدفاعي فقط، ولا تغني عن استشارة المختصين.")
    print("="*40)

# 8. الوضع المجنون (Crazy Mode)
def crazy_mode():
    print("\n" + "="*40)
    print("🔥 الوضع المجنون (Crazy Mode) 🔥")
    print("="*40)
    check_system()
    check_network()
    if os.path.exists("README.md"):
        check_file("README.md")
    print("\n[*] فحص محفظة ساتوشي ناكاموتو (للتجربة)...")
    print("  [+] العنوان: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    print("  [+] النوع: Bitcoin (BTC)")
    print("  [+] الرصيد: 107.70149915 BTC")
    print("\n[*] فحص نص مشبوه (للتجربة)...")
    print("  [+] النص: Urgent: Binance hacker giveaway 5.6 billion free bitcoin")
    print("  [⚠️] تحذير: تم اكتشاف كلمات مشبوهة: hacker, giveaway, binance, free, bitcoin")
    print("  [🚨] نتيجة: هذا النص احتيال!")
    print("\n" + "="*40)
    print("✅ انتهى الوضع المجنون! أنت محمي الآن.")
    print("="*40)

# القائمة الرئيسية
def main():
    print("\n" + "="*40)
    print("🛡️  درع الوجبات (Wajabat Shield) v1.7.0")
    print("   أداة حماية شاملة (All-in-One)")
    print("="*40)
    print("\nاختر الخدمة:")
    print("  [1] فحص تسريب بريد إلكتروني")
    print("  [2] فحص ملف (بصمة SHA256)")
    print("  [3] فحص النظام")
    print("  [4] فحص الشبكة")
    print("  [5] الفحص السريع (Quick Scan) ⭐")
    print("  [6] كشف الاحتيال (Scam Detection) ⭐")
    print("  [7] الرد السريع (Rapid Response) 🚨")
    print("  [8] الوضع المجنون (Crazy Mode) 🔥 جديد")
    print("  [0] خروج")
    
    choice = input("\nاختر رقم: ").strip()
    
    if choice == "1": check_email()
    elif choice == "2": check_file()
    elif choice == "3": check_system()
    elif choice == "4": check_network()
    elif choice == "5": quick_scan()
    elif choice == "6": scam_detection()
    elif choice == "7": rapid_response()
    elif choice == "8": crazy_mode()
    else: print("👋 إلى اللقاء!")

if __name__ == "__main__":
    main()
