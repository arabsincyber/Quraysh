import sys
import subprocess
import requests
import os
import time

def fetch_crtsh_massive(domain):
    """جلب آلاف النطاقات مباشرة من crt.sh"""
    print(f"\n[*] جاري السحب الشامل (Massive) لـ {domain} من crt.sh...")
    print("    (هذا قد يستغرق دقيقة أو أكثر حسب حجم النطاق...)")
    
    subs = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # محاولات متعددة لأن crt.sh مزاجي
    for attempt in range(1, 4):
        print(f"  [+] المحاولة {attempt} ...", end=" ", flush=True)
        try:
            res = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=120, headers=headers)
            if res.status_code == 200:
                data = res.json()
                for item in data:
                    for sub in item['name_value'].split('\n'):
                        clean_sub = sub.strip().lower()
                        if '*' not in clean_sub and '@' not in clean_sub and clean_sub:
                            subs.add(clean_sub)
                print(f"✅ (جلب {len(subs)} نطاق حتى الآن)")
                if len(subs) > 500: # إذا جبنا عدد كبير، نكمل
                    break
            else:
                print(f"❌ (كود: {res.status_code})")
                time.sleep(5)
        except Exception as e:
            print(f"❌ ({str(e)[:30]})")
            time.sleep(5)
            
    return sorted(list(subs))

def run_subfinder(domain):
    """استخدام subfinder كاحتياطي إذا فشل crt.sh"""
    print(f"\n[*] جاري جلب النطاقات عبر subfinder...")
    subs = set()
    try:
        result = subprocess.run(["subfinder", "-d", domain, "-all", "-silent"], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line: subs.add(line.strip().lower())
    except Exception:
        pass
    return list(subs)

def main():
    print("\n╭──────────────────────────────────────────╮")
    print("│   🕵️  لسان قريش - أداة الاستخراج الشامل   │")
    print("│          (Massive Subdomain Extractor)   │")
    print("│              الإصدار v1.0.0              │")
    print("╰──────────────────────────────────────────╯\n")
    
    target = input("أدخل النطاق (Domain) للاستخراج الشامل: ").strip()
    if not target: return print("❌ لم يتم إدخال نطاق.")
    
    auth = input("⚠️ هل أنت مصرح بفحص هذا النطاق؟ (y/n): ").strip().lower()
    if auth != 'y': return print("🛑 تم إلغاء الفحص.")

    # 1. جلب شامل من crt.sh
    subs = fetch_crtsh_massive(target)
    
    # 2. إذا فشل crt.sh أو جاب عدد قليل، نستخدم subfinder
    if len(subs) < 50:
        print("\n[!] عدد النطاقات قليل من crt.sh. جاري استخدام subfinder كاحتياطي...")
        sub_subs = run_subfinder(target)
        for s in sub_subs:
            subs.append(s)
        
        # إزالة التكرار
        subs = sorted(list(set(subs)))

    if not subs:
        print("\n❌ لم يتم العثور على أي نطاقات.")
        return

    # 3. حفظ النتائج
    filename = f"mass_{target}.txt"
    with open(filename, "w") as f:
        for sub in subs:
            f.write(f"{sub}\n")

    print(f"\n{'='*50}")
    print(f"✅ تم استخراج {len(subs)} نطاق فرعي فريد!")
    print(f"💾 تم حفظ النتائج في: {filename}")
    print(f"{'='*50}")
    
    # 4. خيار الفحص بـ httpx
    check = input("\n❓ هل تريد فحصها الآن (حي/ميت) عبر httpx؟ (y/n): ").strip().lower()
    if check == 'y':
        print(f"\n[*] جاري فحص {len(subs)} نطاق عبر httpx...\n")
        try:
            input_data = "\n".join(subs)
            process = subprocess.Popen(
                ["httpx", "-silent", "-status-code", "-title", "-tech-detect"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, _ = process.communicate(input=input_data, timeout=900)
            print(stdout)
            
            live_filename = f"live_mass_{target}.txt"
            with open(live_filename, "w") as f:
                f.write(stdout)
            print(f"\n✅ تم حفظ النتائج في: {live_filename}")
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()
