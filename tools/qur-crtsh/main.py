import sys
import requests
import time

def fetch_crtsh(domain):
    print(f"\n[*] جاري سحب النطاقات من crt.sh للنطاق: {domain}")
    print("    (قد يستغرق بعض الوقت حسب حجم النطاق...)")
    
    subs = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # محاولة 3 مرات
    for attempt in range(1, 4):
        print(f"  [+] المحاولة رقم {attempt} ...", end=" ", flush=True)
        try:
            # زيادة المهلة
            res = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=120, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                for item in data:
                    for sub in item['name_value'].split('\n'):
                        clean_sub = sub.strip().lower()
                        if '*' not in clean_sub and '@' not in clean_sub and clean_sub:
                            subs.add(clean_sub)
                print("✅ نجحت!")
                return sorted(list(subs))
            else:
                print(f"❌ (كود: {res.status_code})")
                time.sleep(5) # انتظر 5 ثواني قبل المحاولة التالية
                
        except requests.exceptions.Timeout:
            print("❌ (انتهى الوقت)")
            time.sleep(5)
        except Exception as e:
            print(f"❌ (خطأ: {e})")
            time.sleep(5)
            
    print("\n[!] فشلت جميع المحاولات. موقع crt.sh قد يكون متعطلاً حالياً.")
    return []

def main():
    print("\n╭──────────────────────────────────────────╮")
    print("│   🕵️  لسان قريش - صياد crt.sh المباشر    │")
    print("│              الإصدار v1.1.0              │")
    print("╰──────────────────────────────────────────╯\n")
    
    target = input("أدخل النطاق (Domain) للاستخراج: ").strip()
    if not target: return print("❌ لم يتم إدخال نطاق.")
    
    auth = input("⚠️ هل أنت مصرح بفحص هذا النطاق؟ (y/n): ").strip().lower()
    if auth != 'y': return print("🛑 تم إلغاء الفحص.")

    # جلب البيانات
    subs = fetch_crtsh(target)
    
    if not subs:
        print("\n❌ لم يتم العثور على أي نطاقات فرعية.")
        return

    # حفظ النتائج
    filename = f"crtsh_{target}.txt"
    with open(filename, "w") as f:
        for sub in subs:
            f.write(f"{sub}\n")

    print(f"\n{'='*50}")
    print(f"✅ تم استخراج {len(subs)} نطاق فرعي بنجاح!")
    print(f"💾 تم حفظ النتائج في الملف: {filename}")
    print(f"{'='*50}")
    
    # سؤال للفحص
    check = input("\n❓ هل تريد فحص هذه النطاقات (حي/ميت) الآن باستخدام httpx؟ (y/n): ").strip().lower()
    if check == 'y':
        import subprocess
        print(f"\n[*] جاري فحص {len(subs)} نطاق عبر httpx...\n")
        try:
            input_data = "\n".join(subs)
            process = subprocess.Popen(
                ["httpx", "-silent", "-status-code", "-title", "-tech-detect"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, _ = process.communicate(input=input_data, timeout=600)
            print(stdout)
            
            # حفظ النتائج الحية
            live_filename = f"live_{target}.txt"
            with open(live_filename, "w") as f:
                f.write(stdout)
            print(f"\n✅ تم حفظ النطاقات الحية في: {live_filename}")
            
        except Exception as e:
            print(f"❌ خطأ في httpx: {e}")

if __name__ == "__main__":
    main()
