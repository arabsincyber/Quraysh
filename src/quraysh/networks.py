"""
Networks — مكتبة الشبكات
==========================

دوال شبكية للغة "لسان قريش".

المزايا:
- HTTP (GET, POST)
- Download
- Ping
- DNS
- TCP

⚠️  تعليمي فقط.
"""

import urllib.request
import urllib.parse
import socket
import subprocess
import json
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  1. HTTP GET
# ═══════════════════════════════════════════════════════════

def اتصل_بـ(url, headers=None):
    """HTTP GET — يجلب صفحة"""
    try:
        req = urllib.request.Request(url)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode("utf-8", errors="ignore")
            return data

    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  2. HTTP POST
# ═══════════════════════════════════════════════════════════

def أرسل_بيانات(url, data):
    """HTTP POST — يرسل بيانات"""
    try:
        if isinstance(data, dict):
            data = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
        else:
            data = str(data).encode("utf-8")
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8", errors="ignore")

    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  3. Download — تحميل ملف
# ═══════════════════════════════════════════════════════════

def حمّل(url, file_path):
    """تحميل ملف من الإنترنت"""
    try:
        urllib.request.urlretrieve(url, file_path)
        size = Path(file_path).stat().st_size
        return f"✅ تم التحميل: {file_path} ({size} بايت)"
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  4. Ping — اختبار الاتصال
# ═══════════════════════════════════════════════════════════

def بينغ(host, count=2):
    """اختبار الاتصال بـ host"""
    try:
        result = subprocess.run(
            f"ping -c {count} {host}",
            shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  5. DNS — استعلام
# ═══════════════════════════════════════════════════════════

def استعلم_dns(domain):
    """استعلام DNS — يحول النطاق لـ IP"""
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "ip": ip}
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  6. TCP — فتح منفذ
# ═══════════════════════════════════════════════════════════

def افتح_منفذ(host, port, timeout=3):
    """يفتح اتصال TCP — للاختبار"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return f"✅ المنفذ {port} مفتوح"
        else:
            return f"❌ المنفذ {port} مغلق"
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  7. IP الحالي
# ═══════════════════════════════════════════════════════════

def ip_الحالي():
    """يجيب IP الحالي"""
    try:
        data = اتصل_بـ("https://api.ipify.org")
        return f"IP: {data.strip()}"
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  8. معلومات الشبكة
# ═══════════════════════════════════════════════════════════

def معلومات_الشبكة():
    """يجمع معلومات الشبكة"""
    print("🌐 معلومات الشبكة")
    print()
    print(f"  Hostname: {socket.gethostname()}")
    try:
        print(f"  IP: {socket.gethostbyname(socket.gethostname())}")
    except:
        print("  IP: —")
    print(f"  IP العام: {ip_الحالي()}")
    print()


# ═══════════════════════════════════════════════════════════
#  الاختبار
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  🌐 Networks — مكتبة الشبكات")
    print("=" * 60)
    print()

    # 1. IP الحالي
    print("1️⃣ IP الحالي:")
    print(f"   {ip_الحالي()}")
    print()

    # 2. DNS
    print("2️⃣ DNS:")
    print(f"   {استعلم_dns('google.com')}")
    print()

    # 3. Ping
    print("3️⃣ Ping:")
    print(f"   {بينغ('8.8.8.8', count=1)[:100]}")
    print()

    # 4. TCP
    print("4️⃣ TCP:")
    print(f"   {افتح_منفذ('google.com', 443)}")
    print()

    # 5. معلومات الشبكة
    print("5️⃣ معلومات الشبكة:")
    معلومات_الشبكة()
