import socket

def scan_ports(host, ports_to_scan=[21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5900]):
    """فحص المنافذ المفتوحة (دفاعياً)"""
    open_ports = []
    print(f"[*] جاري فحص المنافذ لـ {host} ...")
    for port in ports_to_scan:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5) 
                result = s.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"  [+] المنفذ {port} مفتوح")
        except Exception:
            pass
    return open_ports

def check_ports_report(host):
    open_ports = scan_ports(host)
    if not open_ports:
        return {"status": "آمن", "message": "لا توجد منافذ مفتوحة من القائمة المفحوصة."}
    
    warnings = []
    if 3389 in open_ports: warnings.append("⚠️ RDP مفتوح (خطر اختراق عالي)")
    if 5900 in open_ports: warnings.append("⚠️ VNC مفتوح (تحكم عن بعد)")
    if 1433 in open_ports: warnings.append("⚠️ MSSQL مفتوح (قاعدة بيانات مكشوفة)")
    if 3306 in open_ports: warnings.append("⚠️ MySQL مفتوح (قاعدة بيانات مكشوفة)")
    
    return {"open_ports": open_ports, "warnings": warnings}
