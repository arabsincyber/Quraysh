"""
qur fmt — منسّق الكود
=======================

تنسيق ملفات "لسان قريش".

الاستخدام:
    qur fmt <file>             تنسيق ملف
    qur fmt --all              تنسيق كل الملفات
    qur fmt --check <file>     فحص التنسيق
"""

import re
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  التنسيق
# ═══════════════════════════════════════════════════════════

def format_code(source):
    """
    تنسيق كود "لسان قريش".

    القواعد:
    1. مسافة واحدة بين العناصر
    2. سطر جديد بعد كل تعبير رئيسي
    3. إزالة المسافات الزائدة
    """
    lines = []
    for line in source.splitlines():
        # إزالة المسافات الزائدة
        line = line.rstrip()
        if not line:
            lines.append("")
            continue

        # تجاهل التعليقات
        if line.strip().startswith(";"):
            lines.append(line)
            continue

        # إزالة المسافات المتعددة
        line = re.sub(r'[ \t]+', ' ', line)

        # إضافة مسافة بين الأقواس
        line = line.replace('(', '( ').replace(' )', ')')
        line = re.sub(r'\(\s+', '(', line)
        line = re.sub(r'\s+\)', ')', line)

        lines.append(line)

    # إزالة الأسطر الفارغة الزائدة
    result = []
    prev_empty = False
    for line in lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue
        result.append(line)
        prev_empty = is_empty

    return "\n".join(result)


# ═══════════════════════════════════════════════════════════
#  الأوامر
# ═══════════════════════════════════════════════════════════

def fmt_file(path):
    """تنسيق ملف واحد"""
    ملف = Path(path)

    if not ملف.exists():
        print(f"❌ الملف غير موجود: {path}")
        return 1

    # قراءة
    try:
        source = ملف.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ خطأ في القراءة: {e}")
        return 1

    # تنسيق
    result = format_code(source)

    # إذا ما تغير شي
    if result == source:
        print(f"✓ لا يحتاج تنسيق: {path}")
        return 0

    # حفظ
    try:
        ملف.write_text(result, encoding="utf-8")
        print(f"✅ تم تنسيق: {path}")
    except Exception as e:
        print(f"❌ خطأ في الكتابة: {e}")
        return 1

    return 0


def check_file(path):
    """فحص التنسيق"""
    ملف = Path(path)

    if not ملف.exists():
        print(f"❌ الملف غير موجود: {path}")
        return 1

    source = ملف.read_text(encoding="utf-8")
    result = format_code(source)

    if result == source:
        print(f"✓ التنسيق صحيح: {path}")
        return 0
    else:
        print(f"⚠️  التنسيق غير صحيح: {path}")
        print()
        print("💡 للتصحيح:")
        print(f"   qur fmt {path}")
        return 1


def fmt_all(directory="."):
    """تنسيق كل الملفات"""
    مسار = Path(directory)
    ملفات = list(مسار.glob("**/*.lisp"))

    if not ملفات:
        print(f"❌ لا توجد ملفات .lisp في: {directory}")
        return 1

    عداد = 0
    for ملف in ملفات:
        if fmt_file(str(ملف)) == 0:
            عداد += 1

    print()
    print(f"✅ تم تنسيق {عداد} ملف")
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل fmt"""
    if not args:
        print("🎨 qur fmt — منسّق الكود")
        print()
        print("الاستخدام:")
        print("  qur fmt <file>             تنسيق ملف")
        print("  qur fmt --all              تنسيق كل الملفات")
        print("  qur fmt --check <file>     فحص التنسيق")
        return 0

    # --all
    if args[0] == "--all":
        return fmt_all(args[1] if len(args) > 1 else ".")

    # --check
    if args[0] == "--check":
        if len(args) < 2:
            print("❌ الاستخدام: qur fmt --check <file>")
            return 1
        return check_file(args[1])

    # ملف واحد
    return fmt_file(args[0])


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
