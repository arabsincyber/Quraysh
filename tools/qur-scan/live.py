"""
المراقبة المباشرة — 5 خاصيات
"""

import time
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception as e:
        return f"❌ {e}"


def _read_mem():
    try:
        data = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        total = int(data.get("MemTotal", "0").split()[0]) / 1024
        available = int(data.get("MemAvailable", "0").split()[0]) / 1024
        return total, total - available, available
    except:
        return 0, 0, 0


def live_cpu(interval=1, count=5):
    print("🖥️  Live CPU")
    print(f"  (كل {interval} ثانية — {count} مرات)")
    print("  " + "-" * 40)
    try:
        for i in range(count):
            load = _run("top -bn1 | grep 'Cpu' | head -1")
            print(f"  [{i+1}/{count}] {load[:60]}")
            if i < count - 1:
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  ⏹️  توقف")
    print()


def live_ram(interval=1, count=5):
    print("🧠 Live RAM")
    print(f"  (كل {interval} ثانية — {count} مرات)")
    print("  " + "-" * 40)
    try:
        for i in range(count):
            total, used, available = _read_mem()
            pct = (used / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"  [{i+1}/{count}] {used:.0f}/{total:.0f} MB ({pct:.1f}%) {bar}")
            if i < count - 1:
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  ⏹️  توقف")
    print()


def live_processes(interval=1, count=5):
    print("📋 Live Processes")
    print(f"  (كل {interval} ثانية — {count} مرات)")
    print("  " + "-" * 40)
    try:
        for i in range(count):
            n = _run("ps aux 2>/dev/null | wc -l")
            print(f"  [{i+1}/{count}] عدد العمليات: {n}")
            if i < count - 1:
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  ⏹️  توقف")
    print()


def environment():
    """environment — البيئة (بدل network)"""
    print("🌍 Environment — البيئة")
    print()

    print("  📋 متغيرات:")
    print(f"    HOME:    {os.environ.get('HOME', '—')}")
    print(f"    PREFIX:  {os.environ.get('PREFIX', '—')}")
    print(f"    USER:    {os.environ.get('USER', '—')}")
    print()

    print("  🐍 Python:")
    print(f"    الإصدار: {sys.version.split()[0]}")
    print(f"    المسار:  {sys.executable}")
    print()

    print("  💻 الجهاز:")
    print(f"    الموديل:  {_run('getprop ro.product.model') or '—'}")
    print(f"    أندرويد:  {_run('getprop ro.build.version.release') or '—'}")
    print()


def report():
    print("📄 تقرير النظام الكامل")
    print()
    print("═" * 50)
    print(f"  📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 50)
    print()

    print("🖥️  CPU:")
    print(f"  الأنوية: {os.cpu_count() or 1}")
    print()

    total, used, available = _read_mem()
    pct = (used / total * 100) if total > 0 else 0
    print("🧠 RAM:")
    print(f"  الإجمالي: {total:.1f} MB")
    print(f"  المستخدم: {used:.1f} MB")
    print(f"  المتاح: {available:.1f} MB")
    print(f"  الاستخدام: {pct:.1f}%")
    print()

    print("💾 Storage:")
    print(_run("df -h 2>/dev/null | grep -E '/data$|/storage' | head -3") or "  ⚠️  لا يوجد")
    print()

    print("⚙️  Kernel:")
    print(f"  {_run('uname -r')}")
    print()

    print("📱 Android:")
    print(f"  الإصدار: {_run('getprop ro.build.version.release') or '—'}")
    print(f"  الموديل: {_run('getprop ro.product.model') or '—'}")
    print()

    ps_count = _run("ps aux 2>/dev/null | wc -l")
    print(f"📋 العمليات: {ps_count}")
    print()

    print("═" * 50)
    print("  ✅ نهاية التقرير")
    print("═" * 50)
    print()


def run_all():
    print("═══ المراقبة المباشرة ═══")
    print()
    live_cpu(interval=1, count=3)
    live_ram(interval=1, count=3)
    environment()
    report()
