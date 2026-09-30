"""
معلومات النظام — 5 خاصيات
"""

import os
import subprocess
from pathlib import Path


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception as e:
        return f"❌ {e}"


def cpu():
    """CPU — المعالج"""
    print("🖥️  CPU — المعالج")
    print()
    cores = os.cpu_count() or 1
    print(f"  الأنوية: {cores}")
    try:
        info = Path("/proc/cpuinfo").read_text()
        for line in info.splitlines():
            if "Hardware" in line or "model name" in line:
                print(f"  الموديل: {line.split(':')[1].strip()}")
                break
    except:
        pass
    print()


def ram():
    """RAM — الذاكرة"""
    print("🧠 RAM — الذاكرة")
    print()
    try:
        meminfo = Path("/proc/meminfo").read_text()
        data = {}
        for line in meminfo.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

        total = int(data.get("MemTotal", "0").split()[0]) / 1024
        available = int(data.get("MemAvailable", "0").split()[0]) / 1024
        used = total - available
        pct = (used / total * 100) if total > 0 else 0

        print(f"  الإجمالي:   {total:.1f} MB")
        print(f"  المستخدم:   {used:.1f} MB")
        print(f"  المتاح:     {available:.1f} MB")
        print(f"  الاستخدام:  {pct:.1f}%")

        if pct > 90:
            print("  ⚠️  تحذير: الذاكرة ممتلئة!")
        elif pct > 75:
            print("  🟡 ملاحظة: الاستخدام مرتفع.")
        else:
            print("  ✅ الحالة: طبيعية.")
    except Exception as e:
        print(f"  ⚠️  {e}")
    print()


def storage():
    """Storage — التخزين"""
    print("💾 Storage — التخزين")
    print()
    print(_run("df -h 2>/dev/null | grep -E 'Filesystem|/data|/storage' | head -5") or "  ⚠️  لا يمكن القراءة")
    print()


def kernel():
    """Kernel — النواة"""
    print("⚙️  Kernel — النواة")
    print()
    print(f"  النواة:    {_run('uname -r')}")
    print(f"  المعمارية: {_run('uname -m')}")
    print(f"  الاسم:    {_run('hostname')}")
    print()


def android():
    """Android — إصدار أندرويد"""
    print("📱 Android — إصدار أندرويد")
    print()
    print(f"  الإصدار:  {_run('getprop ro.build.version.release') or '—'}")
    print(f"  SDK:       {_run('getprop ro.build.version.sdk') or '—'}")
    print(f"  الموديل:   {_run('getprop ro.product.model') or '—'}")
    print(f"  العلامة:   {_run('getprop ro.product.brand') or '—'}")
    print()


def run_all():
    """يشغّل كل خاصيات النظام"""
    print("═══ معلومات النظام ═══")
    print()
    cpu()
    ram()
    storage()
    kernel()
    android()
