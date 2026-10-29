import subprocess
import json
import random
import time
import concurrent.futures
import requests
from fake_useragent import UserAgent
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()

def get_random_delay():
    """تأخير عشوائي بين 0.5 و 2.5 ثانية"""
    return random.uniform(0.5, 2.5)

def hunt_with_subfinder(domain: str) -> list:
    try:
        result = subprocess.run(["subfinder", "-d", domain, "-silent"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            subs = list(set(result.stdout.strip().split('\n')))
            return [s for s in subs if s]
    except Exception:
        pass
    return []

def scan_with_httpx(subdomains: list) -> list:
    if not subdomains:
        return []
    
    print(f"\n[*] جاري فحص {len(subdomains)} نطاق باستخدام httpx (سريع)...\n")
    print(f"{'النطاق الفرعي':<45} | {'الحالة':<8} | {'السيرفر':<15}")
    print("-" * 75)

    active_subs = []
    try:
        input_data = "\n".join(subdomains)
        process = subprocess.Popen(
            ["httpx", "-silent", "-json", "-status-code", "-tech-detect", "-server"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, _ = process.communicate(input=input_data, timeout=600)

        for line in stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    sub = data.get("input")
                    status = data.get("status_code")
                    server = data.get("webserver", "Unknown")
                    
                    active_subs.append({"subdomain": sub, "status": status, "server": server})
                    print(f"\r{sub:<45} | {status:<8} | {server:<15}")
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return active_subs

def hunt_subdomains_python(subdomains: list) -> list:
    """دالة احتياطية مع إخفاء الهوية وتأخير عشوائي"""
    def check(sub):
        # تأخير عشوائي لتخطي كشف الـ WAF
        time.sleep(get_random_delay())
        
        headers = {'User-Agent': ua.random}
        try:
            res = requests.get(f"https://{sub}", timeout=5, verify=False, headers=headers)
            return {"subdomain": sub, "status": res.status_code, "server": res.headers.get('server', 'Unknown')}
        except: return None

    active = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor: # قللنا الخيوط عشان ما ننكشف
        for res in executor.map(check, subdomains[:500]):
            if res and res.get("status"):
                active.append(res)
                print(f"\r{res['subdomain']:<45} | {res['status']:<8} | {res['server']:<15}")
    return active
