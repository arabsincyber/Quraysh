import requests
import socket
import ssl
from urllib.parse import urlparse
import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scan_url(url: str) -> dict:
    result = {
        "url": url, "status_code": None, "redirects": [],
        "final_url": None, "ssl_valid": None, "server": None,
        "risk_score": 0, "warnings": []
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=False)
        result["status_code"] = response.status_code
        result["final_url"] = response.url
        result["server"] = response.headers.get('server', 'Unknown')

        for r in response.history:
            result["redirects"].append({"from": r.url, "to": r.headers.get('Location', 'N/A'), "status": r.status_code})
            if r.status_code in [301, 302, 307, 308]:
                result["risk_score"] += 5

        if url.startswith("https://"):
            try:
                hostname = urlparse(url).hostname
                context = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        result["ssl_valid"] = True
                        expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_left = (expire_date - datetime.datetime.now()).days
                        if days_left < 30:
                            result["warnings"].append(f"شهادة SSL تنتهي قريباً ({days_left} يوم)")
                            result["risk_score"] += 15
            except Exception as e:
                result["ssl_valid"] = False
                result["warnings"].append(f"خطأ في شهادة SSL: {str(e)[:50]}")
                result["risk_score"] += 30
        else:
            result["warnings"].append("الرابط لا يستخدم HTTPS (غير آمن)")
            result["risk_score"] += 20

        shorteners = ['bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'ow.ly', 'is.gd', 'buff.ly']
        hostname = urlparse(url).hostname or ""
        if hostname in shorteners:
            result["warnings"].append(f"الرابط يستخدم خدمة اختصار ({hostname})")
            result["risk_score"] += 15

        try:
            socket.inet_aton(hostname)
            result["warnings"].append("الرابط يستخدم IP مباشر بدلاً من نطاق")
            result["risk_score"] += 10
        except socket.error:
            pass

        suspicious_words = ['login', 'verify', 'secure', 'account', 'update', 'confirm', 'banking', 'signin']
        for word in suspicious_words:
            if word in url.lower():
                result["warnings"].append(f"كلمة مشبوهة في الرابط: {word}")
                result["risk_score"] += 5
                break

    except Exception as e:
        result["warnings"].append(f"فشل الاتصال: {str(e)[:80]}")
        result["risk_score"] = 100

    if result["risk_score"] >= 50: result["risk_level"] = "🔴 مرتفع"
    elif result["risk_score"] >= 25: result["risk_level"] = "🟡 متوسط"
    else: result["risk_level"] = "🟢 منخفض"

    return result
