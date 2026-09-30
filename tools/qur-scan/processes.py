"""
مراقبة العمليات — 5 خاصيات
"""

import subprocess
from pathlib import Path


def _run(cmd):
    """يشغّل أمر ويعيد الناتج"""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=10
        )
        return r.stdout.strip()
    except Exception as e:
        return f"❌ {e}"


# ═══════════════════════════════════════════════════════════
#  6. Processes — قائمة العمليات
# ═══════════════════════════════════════════════════════════

def processes():
    """processes — قائمة العمليات"""
    print("📋 العمليات الحالية")
    print()

    output = _run("ps aux 2>/dev/null | head -30")

    if not output:
        print("  ⚠️  لا يمكن قراءة العمليات")
        print()
        return

    print(f"  {'PID':<8} {'CPU%':<6} {'MEM%':<6} {'CMD'}")
    print("  " + "-" * 60)

    for line in output.splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            user = parts[0]
            pid = parts[1]
            cpu = parts[2]
            mem = parts[3]
            cmd = parts[10][:35]
            print(f"  {pid:<8} {cpu:<6} {mem:<6} {cmd}")

    print()


# ═══════════════════════════════════════════════════════════
#  7. Top-CPU
# ═══════════════════════════════════════════════════════════

def top_cpu():
    """top-cpu — أعلى استهلاك CPU"""
    print("🔥 أعلى العمليات — CPU")
    print()

    output = _run("ps aux 2>/dev/null | sort -k3 -nr | head -10")

    if not output:
        print("  ⚠️  لا يمكن القراءة")
        print()
        return

    print(f"  {'PID':<8} {'CPU%':<8} {'CMD'}")
    print("  " + "-" * 55)

    for line in output.splitlines():
        parts = line.split(None, 10)
        if len(parts) >= 11:
            pid = parts[1]
            cpu = parts[2]
            cmd = parts[10][:40]
            print(f"  {pid:<8} {cpu:<8} {cmd}")

    print()


# ═══════════════════════════════════════════════════════════
#  8. Top-RAM
# ═══════════════════════════════════════════════════════════

def top_ram():
    """top-ram — أعلى استهلاك RAM"""
    print("🧠 أعلى العمليات — RAM")
    print()

    output = _run("ps aux 2>/dev/null | sort -k4 -nr | head -10")

    if not output:
        print("  ⚠️  لا يمكن القراءة")
        print()
        return

    print(f"  {'PID':<8} {'MEM%':<8} {'CMD'}")
    print("  " + "-" * 55)

    for line in output.splitlines():
        parts = line.split(None, 10)
        if len(parts) >= 11:
            pid = parts[1]
            mem = parts[3]
            cmd = parts[10][:40]
            print(f"  {pid:<8} {mem:<8} {cmd}")

    print()


# ═══════════════════════════════════════════════════════════
#  9. Search — بحث عن عملية
# ═══════════════════════════════════════════════════════════

def search(name):
    """search — بحث عن عملية"""
    print(f"🔍 بحث: {name}")
    print()

    output = _run(f"ps aux 2>/dev/null | grep -i '{name}' | grep -v grep")

    if not output:
        print(f"  ⚠️  لا توجد عمليات بهذا الاسم: {name}")
        print()
        return

    print(f"  {'PID':<8} {'CPU%':<6} {'MEM%':<6} {'CMD'}")
    print("  " + "-" * 60)

    count = 0
    for line in output.splitlines():
        parts = line.split(None, 10)
        if len(parts) >= 11:
            pid = parts[1]
            cpu = parts[2]
            mem = parts[3]
            cmd = parts[10][:40]
            print(f"  {pid:<8} {cpu:<6} {mem:<6} {cmd}")
            count += 1

    print()
    print(f"  ✅ وجد: {count} عملية")
    print()


# ═══════════════════════════════════════════════════════════
#  10. Kill — إنهاء عملية
# ═══════════════════════════════════════════════════════════

def kill(pid):
    """kill — إنهاء عملية (مع تحذير)"""
    print(f"⚠️  إنهاء عملية: PID {pid}")
    print()

    # التحقق من العملية
    check = _run(f"ps -p {pid} -o pid=,comm= 2>/dev/null")

    if not check:
        print(f"  ❌ لا توجد عملية بهذا الـ PID: {pid}")
        print()
        return

    print(f"  العملية: {check}")
    print()

    response = input("  هل أنت متأكد؟ [y/N]: ").strip().lower()
    if response != "y":
        print("  ❌ تم الإلغاء")
        print()
        return

    try:
        result = _run(f"kill {pid} 2>&1")
        if not result or "No such process" not in result:
            print(f"  ✅ تم إرسال إشارة الإنهاء")
        else:
            print(f"  ❌ {result}")
    except Exception as e:
        print(f"  ❌ {e}")

    print()


# ═══════════════════════════════════════════════════════════
#  تشغيل الكل
# ═══════════════════════════════════════════════════════════

def run_all():
    """يشغّل كل خاصيات العمليات"""
    print("═══ مراقبة العمليات ═══")
    print()
    processes()
    top_cpu()
    top_ram()
