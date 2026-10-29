import socket
import ssl
import dns.resolver
import whois
import requests
from .subhunter import hunt_with_subfinder, scan_with_httpx, hunt_subdomains_python

def get_whois(domain: str) -> dict:
    try:
        w = whois.whois(domain)
        return {"registrar": w.registrar, "creation_date": str(w.creation_date)}
    except Exception as e:
        return {"error": str(e)}

def get_dns(domain: str) -> dict:
    records = {}
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['8.8.8.8', '1.1.1.1']
    for rtype in ['A', 'MX', 'TXT', 'NS']:
        try:
            records[rtype] = [str(rdata) for rdata in resolver.resolve(domain, rtype, lifetime=5)]
        except: records[rtype] = []
    return records

def get_ip_info(domain: str) -> dict:
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return {"ip": ip, "country": res.get("country"), "isp": res.get("isp")}
    except Exception as e:
        return {"error": str(e)}

# === دوال جلب النطاقات الفرعية ===
def fetch_from_crtsh(domain):
    try:
        res = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=40)
        if res.status_code == 200:
            return set([item['name_value'] for item in res.json()])
    except: pass
    return set()

def fetch_from_hackertarget(domain):
    try:
        res = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=15)
        if res.status_code == 200:
            return set([line.split(',')[0] for line in res.text.strip().split('\n')])
    except: pass
    return set()

def get_subdomains_and_hunt(domain: str) -> dict:
    all_subs = set()
    
    # 1. جلب من subfinder
    print("\n  [+] المصدر 1: subfinder ...", flush=True)
    subs_subfinder = hunt_with_subfinder(domain)
    if subs_subfinder:
        print(f"      ({len(subs_subfinder)} نطاق)")
        all_subs.update(subs_subfinder)
    else:
        print("      (0 نطاق)")

    # 2. جلب من crt.sh (هذا اللي يجيب الآلاف)
    print("  [+] المصدر 2: crt.sh ...", end=" ", flush=True)
    subs_crtsh = fetch_from_crtsh(domain)
    print(f"({len(subs_crtsh)} نطاق)")
    all_subs.update(subs_crtsh)

    # 3. جلب من HackerTarget
    print("  [+] المصدر 3: HackerTarget ...", end=" ", flush=True)
    subs_hacker = fetch_from_hackertarget(domain)
    print(f"({len(subs_hacker)} نطاق)")
    all_subs.update(subs_hacker)

    # تنظيف النطاقات (إزالة المسافات والرموز الغريبة)
    clean_subs = set()
    for s in all_subs:
        for sub in str(s).split('\n'):
            sub = sub.strip().lower()
            if '*' not in sub and '@' not in sub and sub:
                clean_subs.add(sub)

    if not clean_subs:
        return {"error": "فشلت جميع المصادر في جلب النطاقات."}

    # 4. فحص النطاقات باستخدام httpx
    active_subs = scan_with_httpx(list(clean_subs))
    
    # إذا فشل httpx، استخدم بايثون
    if not active_subs:
        active_subs = hunt_subdomains_python(list(clean_subs))

    return {
        "total_found": len(clean_subs),
        "active_found": len(active_subs),
        "sources": "subfinder + crt.sh + HackerTarget",
        "active_list": active_subs
    }
