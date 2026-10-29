import sys
import subprocess
import requests

def run_subfinder_all(domain):
    print(f"\n[*] جاري جلب النطاقات عبر subfinder (كل المصادر المجانية)...")
    
    subs = set()
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-all", "-silent", "-recursive"], 
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line: subs.add(line.strip().lower())
            print(f"  [+] تم جلب {len(subs)} نطاق من subfinder.")
    except Exception as e:
        print(f"  [!] خطأ في subfinder: {e}")
        
    return list(subs)

def fetch_from_hackertarget(domain):
    print("  [+] المصدر الإضافي: HackerTarget ...", end=" ", flush=True)
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

def main():
    print("\n╭──────────────────────────────────────────╮")
    print("│   🕵️  لسان قريش - صياد النطاقات (Hunter)  │")
    print("│       (بدون مفاتيح API - مجاني 100%)     │")
    print("│              الإصدار v2.0.0              │")
    print("╰──────────────────────────────────────────╯\n")
    
    target = input("أدخل النطاق (Domain) للاستخراج: ").strip()
    if not target: return print("❌ لم يتم إدخال نطاق.")
    
    auth = input("⚠️ هل أنت مصرح بفحص هذا النطاق؟ (y/n): ").strip().lower()
    if auth != 'y': return print("🛑 تم إلغاء الفحص.")

    subs = run_subfinder_all(target)
    ht_subs = fetch_from_hackertarget(target)
    subs.extend(list(ht_subs))
    unique_subs = sorted(list(set(subs)))

    if not unique_subs:
        print("\n❌ لم يتم العثور على أي نطاقات.")
        return

    filename = f"hunter_{target}.txt"
    with open(filename, "w") as f:
        for sub in unique_subs:
            f.write(f"{sub}\n")

    print(f"\n{'='*50}")
    print(f"✅ تم استخراج {len(unique_subs)} نطاق فرعي فريد!")
    print(f"💾 تم حفظ النتائج في: {filename}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
