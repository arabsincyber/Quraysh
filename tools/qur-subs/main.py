import sys
import os
import requests
import subprocess
import time

def fetch_from_crtsh(domain):
    print("  [+] المصدر 1: crt.sh ...", end=" ", flush=True)
    subs = set()
    # محاولة مرتين لضمان النجاح
    for attempt in range(2):
        try:
            # زيادة وقت الانتظار وتغيير User-Agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=90, headers=headers)
            if res.status_code == 200:
                for item in res.json():
                    for sub in item['name_value'].split('\n'):
                        subs.add(sub.strip().lower())
                break # إذا نجح، اخرج من المحاولة
        except Exception:
            time.sleep(3) # انتظر 3 ثواني قبل المحاولة الثانية
    print(f"({len(subs)} نطاق)")
    return subs

def fetch_from_hackertarget(domain):
    print("  [+] المصدر 2: HackerTarget ...", end=" ", flush=True)
    subs = set()
    try:
        res = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=30)
        if res.status_code == 200:
            for line in res.text.strip().split('\n'):
                if ',' in line:
                    subs.add(line.split(',')[0].strip().lower())
    except Exception:
        pass
    print(f"({len(subs)} نطاق)")
    return subs

def fetch_from_alienvault(domain):
    print("  [+] المصدر 3: AlienVault OTX ...", end=" ", flush=True)
    subs = set()
    try:
        res = requests.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", timeout=30)
        if res.status_code == 200:
            for item in res.json().get('passive_dns', []):
                subs.add(item['hostname'].strip().lower())
    except Exception:
        pass
    print(f"({len(subs)} نطاق)")
    return subs

def fetch_from_subfinder(domain):
    print("  [+] المصدر 4: subfinder ...", end=" ", flush=True)
    subs = set()
    try:
        result = subprocess.run(["subfinder", "-d", domain, "-silent"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line: subs.add(line.strip().lower())
    except Exception:
        pass
    print(f"({len(subs)} نطاق)")
    return subs

def main():
    print("\n╭──────────────────────────────────────────╮")
    print("│   🕵️  لسان قريش - صياد النطاقات الفرعية   │")
    print("│              الإصدار v1.1.0              │")
    print("╰──────────────────────────────────────────╯\n")
    
    target = input("أدخل النطاق (Domain) للاستخراج: ").strip()
    if not target: return print("❌ لم يتم إدخال نطاق.")
    
    auth = input("⚠️ هل أنت مصرح بفحص هذا النطاق؟ (y/n): ").strip().lower()
    if auth != 'y': return print("🛑 تم إلغاء الفحص.")

    print(f"\n[*] جاري استخراج النطاقات الفرعية للنطاق: {target}\n")
    
    all_subs = set()
    all_subs.update(fetch_from_subfinder(target))
    all_subs.update(fetch_from_crtsh(target))
    all_subs.update(fetch_from_hackertarget(target))
    all_subs.update(fetch_from_alienvault(target))

    clean_subs = set()
    for s in all_subs:
        if '*' not in s and '@' not in s and s:
            clean_subs.add(s)

    sorted_subs = sorted(list(clean_subs))
    filename = f"all_subs_{target}.txt"
    
    with open(filename, "w") as f:
        for sub in sorted_subs:
            f.write(f"{sub}\n")

    print(f"\n{'='*50}")
    print(f"✅ تم استخراج {len(sorted_subs)} نطاق فرعي فريد.")
    print(f"💾 تم حفظ النتائج في الملف: {filename}")
    print(f"{'='*50}")
    
if __name__ == "__main__":
    main()
