"""
qur update — تحديث الحزم
===========================

تحديث حزم "لسان قريش" المثبّتة.

الاستخدام:
    qur update                    تحديث كل الحزم
    qur update <name>             تحديث حزمة
    qur update --list             عرض المحدّثة
"""

import json
from pathlib import Path
from . import install as install_cmd
from . import publish as publish_cmd


HOME = Path.home()
INSTALL_DB = HOME / ".qur" / "installed.json"
REPO_INDEX = HOME / ".qur" / "repo" / "index.json"


# ═══════════════════════════════════════════════════════════
#  تحديث
# ═══════════════════════════════════════════════════════════

def compare_versions(v1, v2):
    """
    يقارن إصدارين.
    يرجع:
        1  → v1 > v2
        0  → v1 == v2
       -1  → v1 < v2
    """
    parts1 = [int(x) for x in v1.split(".") if x.isdigit()]
    parts2 = [int(x) for x in v2.split(".") if x.isdigit()]

    # املأ بالأصفار
    while len(parts1) < len(parts2):
        parts1.append(0)
    while len(parts2) < len(parts1):
        parts2.append(0)

    for a, b in zip(parts1, parts2):
        if a > b:
            return 1
        elif a < b:
            return -1

    return 0


def update_package(name):
    """يحدّث حزمة واحدة"""
    # 1. الحزمة المثبّتة
    if not INSTALL_DB.exists():
        print("❌ لا توجد حزم مثبّتة")
        return 1

    db = json.loads(INSTALL_DB.read_text(encoding="utf-8"))
    if name not in db:
        print(f"❌ الحزمة غير مثبتة: {name}")
        return 1

    installed_version = db[name].get("version", "0.0.0")

    # 2. الحزمة المنشورة
    if not REPO_INDEX.exists():
        print("❌ لا يوجد مستودع")
        return 1

    repo = json.loads(REPO_INDEX.read_text(encoding="utf-8"))
    if name not in repo:
        print(f"❌ الحزمة غير منشورة: {name}")
        return 1

    latest = repo[name].get("latest", "0.0.0")

    # 3. المقارنة
    print(f"📦 {name}")
    print(f"   المثبّت:   {installed_version}")
    print(f"   الأحدث:   {latest}")

    if compare_versions(latest, installed_version) <= 0:
        print(f"   ✓ محدّث بالفعل")
        return 0

    # 4. التحديث
    print(f"   🔄 جاري التحديث...")

    repo_path = HOME / ".qur" / "repo"
    package_file = repo_path / f"{name}-{latest}.qur"

    if not package_file.exists():
        print(f"   ❌ الملف غير موجود: {package_file}")
        return 1

    # إزالة القديم
    install_cmd.remove_package(name)

    # تثبيت الجديد
    result = install_cmd.install_package(str(package_file))

    if result == 0:
        print(f"   ✅ تم التحديث إلى {latest}")
        return 0
    else:
        print(f"   ❌ فشل التحديث")
        return 1


def update_all():
    """يحدّث كل الحزم"""
    if not INSTALL_DB.exists():
        print("❌ لا توجد حزم مثبّتة")
        return 1

    db = json.loads(INSTALL_DB.read_text(encoding="utf-8"))

    if not db:
        print("❌ لا توجد حزم مثبّتة")
        return 1

    print(f"🔄 تحديث {len(db)} حزمة...")
    print()

    عداد = 0
    for name in db:
        print(f"─── {name} ───")
        if update_package(name) == 0:
            عداد += 1
        print()

    print("=" * 50)
    print(f"  ✅ تم تحديث: {عداد}/{len(db)}")
    print("=" * 50)

    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل update"""
    if not args:
        return update_all()

    if args[0] == "--list":
        return update_all()

    return update_package(args[0])


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
