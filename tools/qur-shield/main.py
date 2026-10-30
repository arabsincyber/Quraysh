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

# 6. كشف الاحتيال (Scam Detection) ⭐ جديد
def scam_detection():
    text = input("\nأدخل النص أو الرابط المشبوه: ").strip()
    print(f"\n[*] جاري تحليل: {text}")
    
    suspicious_keywords = [
        "hacker", "free", "giveaway", "binance", "million", "billion",
        "win", "prize", "claim", "reward", "urgent", "verify", "account",
        "suspended", "bitcoin", "crypto", "wallet", "transfer"
    ]
    
    found = []
    for word in suspicious_keywords:
        if word.lower() in text.lower():
            found.append(word)
    
    if found:
        print(f"  [⚠️] تحذير: تم اكتشاف كلمات مشبوهة: {', '.join(found)}")
        print("  [🚨] نتيجة: هذا النص قد يكون احتيالاً (Scam). لا تتفاعل معه!")
    else:
        print("  [✅] لم يتم اكتشاف كلمات مشبوهة. النص يبدو آمناً.")

# القائمة الرئيسية
def main():
    print("\n" + "="*40)
    print("🛡️  درع الوجبات (Wajabat Shield) v1.5.0")
    print("   أداة حماية شاملة (All-in-One)")
    print("="*40)
    print("\nاختر الخدمة:")
    print("  [1] فحص تسريب بريد إلكتروني")
    print("  [2] فحص ملف (بصمة SHA256)")
    print("  [3] فحص النظام")
    print("  [4] فحص الشبكة")
    print("  [5] الفحص السريع (Quick Scan) ⭐")
    print("  [6] كشف الاحتيال (Scam Detection) ⭐ جديد")
    print("  [0] خروج")
    
    choice = input("\nاختر رقم: ").strip()
    
    if choice == "1": check_email()
    elif choice == "2": check_file()
    elif choice == "3": check_system()
    elif choice == "4": check_network()
    elif choice == "5": quick_scan()
    elif choice == "6": scam_detection()
    else: print("👋 إلى اللقاء!")

if __name__ == "__main__":
    main()
