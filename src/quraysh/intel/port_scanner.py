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
    danger_ports = []
    
    # تصنيف المنافذ الخطيرة
    if 3389 in open_ports: 
        warnings.append("⚠️ RDP مفتوح (خطر اختراق عالي - يسمح بالتحكم الكامل)")
        danger_ports.append(3389)
    if 5900 in open_ports: 
        warnings.append("⚠️ VNC مفتوح (تحكم عن بعد - غير مشفر غالباً)")
        danger_ports.append(5900)
    if 1433 in open_ports: 
        warnings.append("⚠️ MSSQL مفتوح (قاعدة بيانات مكشوفة - خطر تسريب بيانات)")
        danger_ports.append(1433)
    if 3306 in open_ports: 
        warnings.append("⚠️ MySQL مفتوح (قاعدة بيانات مكشوفة - خطر تسريب بيانات)")
        danger_ports.append(3306)
    if 21 in open_ports:
        warnings.append("⚠️ FTP مفتوح (غير مشفر - يمكن اعتراض البيانات)")
        danger_ports.append(21)

    # التنبيه الأخلاقي
    if danger_ports:
        ethical_warning = (
            "\n" + "="*50 + "\n"
            "🛑 تنبيه أخلاقي وقانوني:\n"
            "تم اكتشاف منافذ خطيرة مفتوحة. هذا يعني أن النظام قد يكون معرضاً للاختراق.\n"
            "يجب عليك:\n"
            "  1. إغلاق هذه المنافذ فوراً إذا كان النظام ملكك.\n"
            "  2. الإبلاغ الفوري للمركز الوطني للأمن السيبراني (NCA) عبر: cert@nca.gov.sa\n"
            "  3. عدم محاولة استغلال هذه الثغرات، لأن ذلك يعتبر جريمة إلكترونية.\n"
            + "="*50
        )
        warnings.append(ethical_warning)
    
    return {"open_ports": open_ports, "warnings": warnings, "danger_ports": danger_ports}
