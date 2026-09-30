"""جمع المعلومات — 10 خاصيات"""

import socket
import subprocess


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"❌ {e}"


def whois(target):
    print(f"🔍 WHOIS: {target}")
    print(_run(f"whois {target} 2>/dev/null | head -30") or "  ⚠️  لا توجد معلومات")
    print()


def dns(target):
    print(f"🔍 DNS: {target}")
    print(f"  A:   {_run(f'dig +short A {target}') or '—'}")
    print(f"  MX:  {_run(f'dig +short MX {target}') or '—'}")
    print(f"  NS:  {_run(f'dig +short NS {target}') or '—'}")
    print(f"  TXT: {_run(f'dig +short TXT {target}') or '—'}")
    print()


def reverse_dns(ip):
    print(f"🔍 Reverse DNS: {ip}")
    try:
        print(f"  → {socket.gethostbyaddr(ip)[0]}")
    except:
        print("  ⚠️  لا يوجد")
    print()


def subdomains(target):
    print(f"🔍 Subdomains: {target}")
    print(_run(f"subfinder -d {target} -silent 2>/dev/null | head -20") or "  ⚠️  لا توجد")
    print()


def http_headers(target):
    print(f"🔍 HTTP Headers: {target}")
    print(_run(f"curl -sI https://{target} 2>/dev/null | head -15") or "  ⚠️  لا توجد")
    print()


def robots(target):
    print(f"🔍 robots.txt: {target}")
    out = _run(f"curl -s https://{target}/robots.txt 2>/dev/null | head -20")
    print(out if out and "404" not in out else "  ⚠️  لا يوجد")
    print()


def sitemap(target):
    print(f"🔍 sitemap.xml: {target}")
    out = _run(f"curl -s https://{target}/sitemap.xml 2>/dev/null | head -20")
    print(out if out and "<?xml" in out else "  ⚠️  لا يوجد")
    print()


def technology(target):
    print(f"🔍 Technology: {target}")
    print(_run(f"httpx -u https://{target} -tech-detect -silent 2>/dev/null") or "  ⚠️  httpx غير مثبت")
    print()


def ip_info(target):
    print(f"🔍 IP Info: {target}")
    try:
        print(f"  IP: {socket.gethostbyname(target)}")
    except:
        print("  ⚠️  لا يمكن الحصول على IP")
    print()


def emails(target):
    print(f"🔍 Emails: {target}")
    out = _run(f"curl -s https://{target} 2>/dev/null | grep -oE '[a-zA-Z0-9._%+-]+@{target}' | head -10")
    print(out or "  ⚠️  لا توجد")
    print()


def run_all(target):
    print(f"═══ جمع المعلومات: {target} ═══")
    print()
    whois(target)
    dns(target)
    try:
        reverse_dns(socket.gethostbyname(target))
    except:
        pass
    subdomains(target)
    http_headers(target)
    robots(target)
    sitemap(target)
    technology(target)
    ip_info(target)
    emails(target)
