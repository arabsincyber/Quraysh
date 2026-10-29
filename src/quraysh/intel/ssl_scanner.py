import socket
import ssl
import datetime

def check_ssl(host: str, port: int = 443) -> dict:
    """فحص شهادة SSL لنطاق معين"""
    result = {
        "host": host,
        "issuer": None,
        "subject": None,
        "valid_from": None,
        "valid_to": None,
        "days_left": None,
        "status": "آمن",
        "warnings": []
    }

    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                # استخراج البيانات
                result["issuer"] = dict(x[0] for x in cert['issuer'])
                result["subject"] = dict(x[0] for x in cert['subject'])
                result["valid_from"] = cert['notBefore']
                result["valid_to"] = cert['notAfter']
                
                # حساب الأيام المتبقية
                expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expire_date - datetime.datetime.now()).days
                result["days_left"] = days_left

                if days_left < 0:
                    result["status"] = "🔴 منتهية الصلاحية"
                    result["warnings"].append("الشهادة منتهية الصلاحية! الموقع غير آمن.")
                elif days_left < 30:
                    result["status"] = "🟡 تنتهي قريباً"
                    result["warnings"].append(f"الشهادة تنتهي خلال {days_left} يوم. يرجى التجديد.")
                else:
                    result["status"] = "🟢 سارية"

    except ssl.SSLCertVerificationError:
        result["status"] = "🔴 خطأ في التحقق"
        result["warnings"].append("فشل التحقق من الشهادة (قد تكون مزيفة أو غير موثوقة).")
    except Exception as e:
        result["status"] = "❌ فشل الاتصال"
        result["warnings"].append(f"تعذر الاتصال: {str(e)[:50]}")
        
    return result
