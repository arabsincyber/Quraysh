import subprocess

def scan_ports(domain):
    """فحص المنافذ باستخدام naabu"""
    print(f"\n  [+] جاري فحص المنافذ لـ {domain} ...", end=" ", flush=True)
    try:
        # استدعاء naabu مع أهم 100 منفذ
        result = subprocess.run(["naabu", "-host", domain, "-top-ports", "100", "-silent"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            ports = result.stdout.strip().split('\n')
            print(f"✅ (تم اكتشاف {len(ports)} منفذ)")
            return {"open_ports": ports}
    except FileNotFoundError:
        print("❌ (naabu غير مثبت)")
    except Exception:
        print("❌ (فشل الفحص)")
    return {"open_ports": []}

def scan_ssl(domain):
    """فحص شهادة SSL باستخدام nmap"""
    print(f"  [+] جاري فحص SSL لـ {domain} ...", end=" ", flush=True)
    try:
        result = subprocess.run(["nmap", "--script", "ssl-enum-ciphers", "-p", "443", domain], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅")
            # استخراج ملخص بسيط
            lines = result.stdout.split('\n')
            summary = "\n".join([line for line in lines if "TLSv" in line or "least strength" in line])
            return {"ssl_info": summary}
    except FileNotFoundError:
        print("❌ (nmap غير مثبت)")
    except Exception:
        print("❌ (فشل الفحص)")
    return {"ssl_info": "غير متوفر"}

def get_headers(domain):
    """جلب الترويسات باستخدام curl"""
    print(f"  [+] جاري جلب الترويسات لـ {domain} ...", end=" ", flush=True)
    try:
        result = subprocess.run(["curl", "-s", "-I", f"https://{domain}"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅")
            return {"headers": result.stdout}
    except Exception:
        print("❌")
    return {"headers": "فشل جلب الترويسات"}
