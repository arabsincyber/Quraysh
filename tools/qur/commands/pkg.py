"""
qur pkg — مدير الحزم
======================

إدارة حزم "لسان قريش".

الاستخدام:
    qur pkg install <اسم>      تثبيت حزمة
    qur pkg remove <اسم>       إزالة حزمة
    qur pkg list               عرض الحزم
    qur pkg search <كلمة>      بحث
    qur pkg info <اسم>         معلومات حزمة
"""

import json
import os
from pathlib import Path


# مجلد الحزم
HOME = Path.home()
PKG_DIR = HOME / ".qur" / "packages"
PKG_DB = HOME / ".qur" / "packages.json"


# ═══════════════════════════════════════════════════════════
#  قاعدة بيانات الحزم
# ═══════════════════════════════════════════════════════════

def ensure_dirs():
    """التأكد من وجود المجلدات"""
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    if not PKG_DB.exists():
        PKG_DB.write_text("{}", encoding="utf-8")


def load_db():
    """تحميل قاعدة البيانات"""
    ensure_dirs()
    try:
        return json.loads(PKG_DB.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_db(db):
    """حفظ قاعدة البيانات"""
    ensure_dirs()
    PKG_DB.write_text(
        json.dumps(db, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ═══════════════════════════════════════════════════════════
#  أوامر pkg
# ═══════════════════════════════════════════════════════════

def cmd_install(args):
    """تثبيت حزمة"""
    if not args:
        print("❌ الاستخدام: qur pkg install <اسم>")
        return 1

    اسم = args[0]

    print(f"📦 جاري تثبيت الحزمة: {اسم}")
    print()

    # للأغراض التعليمية — نسجّل الحزمة فقط
    db = load_db()
    db[اسم] = {
        "الاسم": اسم,
        "الإصدار": "1.0.0",
        "التاريخ": "2026-09-28",
        "الوصف": "حزمة تعليمية",
    }
    save_db(db)

    # إنشاء مجلد الحزمة
    pkg_path = PKG_DIR / اسم
    pkg_path.mkdir(exist_ok=True)

    print(f"✅ تم تثبيت: {اسم}")
    print(f"📁 المسار: {pkg_path}")
    print()
    print(f"💡 للاستخدام:")
    print(f"   import {اسم}")
    return 0


def cmd_remove(args):
    """إزالة حزمة"""
    if not args:
        print("❌ الاستخدام: qur pkg remove <اسم>")
        return 1

    اسم = args[0]

    db = load_db()
    if اسم not in db:
        print(f"❌ الحزمة غير مثبتة: {اسم}")
        return 1

    # إزالة من القاعدة
    del db[اسم]
    save_db(db)

    # إزالة المجلد
    pkg_path = PKG_DIR / اسم
    if pkg_path.exists():
        import shutil
        shutil.rmtree(pkg_path)

    print(f"✅ تم إزالة: {اسم}")
    return 0


def cmd_list(args):
    """عرض الحزم"""
    db = load_db()

    if not db:
        print("📦 لا توجد حزم مثبتة.")
        print()
        print("💡 للتثبيت:")
        print("   qur pkg install <اسم>")
        return 0

    print("📦 الحزم المثبتة:")
    print()
    print(f"  {'الاسم':<20} {'الإصدار':<10}")
    print("  " + "-" * 35)

    for اسم, معلومات in db.items():
        إصدار = معلومات.get("الإصدار", "?")
        print(f"  {اسم:<20} {إصدار:<10}")

    print()
    print(f"  الإجمالي: {len(db)} حزمة")
    return 0


def cmd_search(args):
    """بحث في الحزم"""
    if not args:
        print("❌ الاستخدام: qur pkg search <كلمة>")
        return 1

    كلمة = args[0]
    db = load_db()

    نتائج = [
        اسم for اسم in db
        if كلمة in اسم
    ]

    if not نتائج:
        print(f"❌ لا توجد نتائج: {كلمة}")
        return 0

    print(f"🔍 نتائج البحث عن '{كلمة}':")
    print()
    for اسم in نتائج:
        print(f"  📦 {اسم}")
    return 0


def cmd_info(args):
    """معلومات حزمة"""
    if not args:
        print("❌ الاستخدام: qur pkg info <اسم>")
        return 1

    اسم = args[0]
    db = load_db()

    if اسم not in db:
        print(f"❌ الحزمة غير مثبتة: {اسم}")
        return 1

    معلومات = db[اسم]
    print(f"📦 معلومات الحزمة: {اسم}")
    print()
    for مفتاح, قيمة in معلومات.items():
        print(f"  {مفتاح}: {قيمة}")
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

الأوامر = {
    'install': cmd_install,
    'remove': cmd_remove,
    'list': cmd_list,
    'search': cmd_search,
    'info': cmd_info,
}


def run(args):
    """تشغيل pkg"""
    if not args:
        print("📦 qur pkg — مدير الحزم")
        print()
        print("الاستخدام:")
        print("  qur pkg install <اسم>      تثبيت حزمة")
        print("  qur pkg remove <اسم>       إزالة حزمة")
        print("  qur pkg list               عرض الحزم")
        print("  qur pkg search <كلمة>      بحث")
        print("  qur pkg info <اسم>         معلومات")
        return 0

    أمر = args[0]
    if أمر not in الأوامر:
        print(f"❌ أمر غير معروف: pkg {أمر}")
        return 1

    return الأوامر[أمر](args[1:])


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
