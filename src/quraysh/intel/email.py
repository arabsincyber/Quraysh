import dns.resolver

def check_email_security(domain: str) -> dict:
    """فحص سجلات SPF و DMARC"""
    result = {"spf": "غير موجود", "dmarc": "غير موجود", "risk": "مرتفع"}
    
    # فحص SPF
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        txt_records = resolver.resolve(domain, 'TXT', lifetime=5)
        for txt in txt_records:
            if "v=spf1" in str(txt):
                result["spf"] = str(txt)
                break
    except Exception:
        pass

    # فحص DMARC
    try:
        dmarc_records = resolver.resolve(f"_dmarc.{domain}", 'TXT', lifetime=5)
        for txt in dmarc_records:
            if "v=DMARC1" in str(txt):
                result["dmarc"] = str(txt)
                break
    except Exception:
        pass

    # تقييم الخطورة
    if result["spf"] != "غير موجود" and result["dmarc"] != "غير موجود":
        result["risk"] = "منخفض (محمي)"
    elif result["spf"] != "غير موجود" or result["dmarc"] != "غير موجود":
        result["risk"] = "متوسط"
    else:
        result["risk"] = "مرتفع (قابل للانتحال)"

    return result
