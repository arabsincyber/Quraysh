import requests

def get_http_info(domain: str) -> dict:
    """محاكاة httpx - جلب حالة الموقع والترويسات"""
    try:
        # نستخدم User-Agent عادي لتجنب الحظر
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(f"https://{domain}", timeout=5, headers=headers, allow_redirects=True)
        
        # استخراج التقنيات الأولية من الترويسات
        tech = []
        if 'server' in res.headers:
            tech.append(res.headers['server'])
        if 'x-powered-by' in res.headers:
            tech.append(res.headers['x-powered-by'])
            
        return {
            "status_code": res.status_code,
            "final_url": res.url,
            "server": res.headers.get('server', 'Unknown'),
            "tech": tech,
            "hsts": "HSTS" if 'strict-transport-security' in res.headers else "No HSTS"
        }
    except Exception as e:
        return {"error": str(e)}

def get_headers(domain: str) -> dict:
    """محاكاة curl -I - جلب ترويسات HTTP"""
    try:
        res = requests.head(f"https://{domain}", timeout=5, allow_redirects=True)
        return dict(res.headers)
    except Exception as e:
        return {"error": str(e)}
