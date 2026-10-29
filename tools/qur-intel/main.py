import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from quraysh.intel.core import IntelCore
from quraysh.intel import domain as domain_scanner
from quraysh.intel import email as email_scanner
from quraysh.intel import system_scan
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote

def print_banner():
    print("\n╭──────────────────────────────────────────╮")
    print("│   🕵️  لسان قريش - أداة الفحص الاستخباراتي  │")
    print("│        الإصدار v1.3.0 (الشامل)           │")
    print("╰──────────────────────────────────────────╯\n")

def search_duckduckgo(query, max_results=5):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for result in soup.find_all('a', class_='result__a')[:max_results]:
            title = result.get_text()
            link = result.get('href')
            if link and link.startswith('//'): link = 'https:' + link
            results.append({"title": title, "link": link})
    except Exception: pass
    return results

def run_wizard():
    print_banner()
    target = input("أدخل النطاق (Domain) للفحص: ").strip()
    if not target: return print("❌ لم يتم إدخال نطاق.")
    
    auth = input("⚠️ هل أنت مصرح بفحص هذا النطاق؟ (y/n): ").strip().lower()
    if auth != 'y': return print("🛑 تم إلغاء الفحص.")

    core = IntelCore(target, authorized=True)
    
    # الفحوصات الأساسية
    core.run_module("WHOIS", domain_scanner.get_whois, source="python-whois")
    core.run_module("DNS Records", domain_scanner.get_dns, source="dnspython")
    core.run_module("IP & Geo Info", domain_scanner.get_ip_info, source="ip-api.com")
    core.run_module("Email Security", email_scanner.check_email_security, source="DNS TXT")
    
    # فحص الشبكة (جديد)
    print("\n--- [فحص الشبكة والخدمات] ---")
    core.run_module("Open Ports", system_scan.scan_ports, source="naabu")
    core.run_module("SSL Check", system_scan.scan_ssl, source="nmap")
    core.run_module("HTTP Headers", system_scan.get_headers, source="curl")

    # فحص النطاقات الفرعية
    sub_data = core.run_module("Subdomain Hunter", domain_scanner.get_subdomains_and_hunt, source="subfinder+httpx")

    print("\n" + "="*40)
    if input("[?] هل تريد حفظ التقرير الكامل في markdown؟ (y/n): ").strip().lower() == 'y':
        core.export_markdown(f"report_{target}.md")

if __name__ == "__main__":
    run_wizard()
