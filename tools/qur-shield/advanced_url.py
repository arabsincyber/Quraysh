import requests
import whois
import ssl
import socket
import datetime
from urllib.parse import urlparse

def deep_scan_url(url):
    print(f"\n[*] جاري الفحص المتقدم للرابط: {url}\n")
    
    # 1. فحص التحويلات
    try:
        res = requests.get(url, timeout=10, allow_redirects=True, verify=False)
        print(f"  [+] حالة الاستجابة: {res.status_code}")
        print(f"  [+] الرابط النهائي: {res.url}")
        if res.history:
            print(f"  [+] عدد التحويلات: {len(res.history)}")
            for r in res.history:
                print(f"      - {r.status_code} -> {r.headers.get('Location', 'N/A')}")
    except Exception as e:
        print(f"  [❌] فشل الاتصال: {str(e)[:50]}")
        return

    # 2. فحص WHOIS (عمر النطاق) — مع إصلاح الخطأ
    try:
        domain = urlparse(url).hostname
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        
        if creation:
            # توحيد المنطقة الزمنية
            if creation.tzinfo is None:
                creation = creation.replace(tzinfo=datetime.timezone.utc)
            
            now = datetime.datetime.now(datetime.timezone.utc)
            age_days = (now - creation).days
            print(f"  [+] تاريخ إنشاء النطاق: {creation.strftime('%Y-%m-%d')}")
            print(f"  [+] عمر النطاق: {age_days} يوم")
            if age_days < 7:
                print(f"  [🚨] خطر: النطاق عمره أقل من أسبوع - احتيال محتمل!")
            elif age_days < 30:
                print(f"  [⚠️] تحذير: النطاق جديد (أقل من 30 يوم) - مشبوه!")
    except Exception as e:
        print(f"  [⚠️] لم نتمكن من جلب WHOIS: {str(e)[:50]}")

    # 3. فحص SSL
    try:
        hostname = urlparse(url).hostname
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expire = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expire - datetime.datetime.now()).days
                print(f"  [+] شهادة SSL: صالحة (تنتهي خلال {days_left} يوم)")
    except Exception as e:
        print(f"  [❌] شهادة SSL: غير صالحة أو غير موجودة")
