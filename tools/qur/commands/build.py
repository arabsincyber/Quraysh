"""
qur build — البناء
====================

بناء مشاريع "لسان قريش".

الاستخدام:
    qur build              بناء المشروع الحالي
    qur build --check      فحص قبل البناء
    qur build --clean      تنظيف قبل البناء
    qur build -o out.lisp  ملف مخرج
"""

import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  البناء
# ═══════════════════════════════════════════════════════════

def find_lisp_files(directory="."):
    """يجد كل ملفات .lisp"""
    مسار = Path(directory)
    return sorted(مسار.glob("**/*.lisp"))


def read_file(path):
    """يقرأ ملف .lisp"""
    return Path(path).read_text(encoding="utf-8")


def build_project(directory=".", output=None, check=False, clean=False):
    """
    بناء المشروع.

    Args:
        directory: مجلد المشروع
        output: ملف المخرج
        check: فحص قبل البناء
        clean: تنظيف قبل البناء
    """
    مسار = Path(directory)

    if not مسار.exists():
        print(f"❌ المجلد غير موجود: {directory}")
        return 1

    # 1. إيجاد الملفات
    ملفات = find_lisp_files(directory)

    if not ملفات:
        print(f"❌ لا توجد ملفات .lisp في: {directory}")
        return 1

    print(f"🔍 وُجد {len(ملفات)} ملف .lisp")
    print()

    # 2. فحص (اختياري)
    if check:
        print("🔎 فحص الملفات...")
        for ملف in ملفات:
            try:
                src_path = Path(__file__).parent.parent.parent.parent / "src"
                if src_path.exists():
                    sys.path.insert(0, str(src_path))

                from quraysh.lexer import tokenize
                from quraysh.parser import parse_all

                نص = read_file(ملف)
                tokenize(نص)
                parse_all(نص)
                print(f"  ✓ {ملف.name}")
            except Exception as e:
                print(f"  ❌ {ملف.name}: {e}")
                return 1
        print()

    # 3. تنظيف (اختياري)
    if clean:
        print("🧹 تنظيف...")
        out_dir = مسار / "build"
        if out_dir.exists():
            import shutil
            shutil.rmtree(out_dir)
        print("  ✓ تم التنظيف")
        print()

    # 4. البناء
    print("🔨 جاري البناء...")
    print()

    محتوى = []
    محتوى.append("; ═══════════════════════════════════════════")
    محتوى.append("; ملف مُبنى بواسطة qur build")
    محتوى.append("; ═══════════════════════════════════════════")
    محتوى.append("")

    for ملف in ملفات:
        محتوى.append(f"; ─── {ملف.name} ───")
        محتوى.append(read_file(ملف))
        محتوى.append("")

    نتيجة = "\n".join(محتوى)

    # 5. الحفظ
    if output is None:
        output = مسار / "build" / "main.lisp"
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        output = Path(output)

    output.write_text(نتيجة, encoding="utf-8")

    # 6. التقرير
    print(f"✅ تم البناء بنجاح!")
    print()
    print(f"📄 المخرج: {output}")
    print(f"📊 الحجم: {len(نتيجة)} حرف")
    print(f"📁 الملفات: {len(ملفات)}")
    print()
    print("💡 للتشغيل:")
    print(f"   qur run {output}")

    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل build"""
    if not args:
        return build_project(".")

    check = False
    clean = False
    output = None
    directory = "."

    i = 0
    while i < len(args):
        if args[i] == "--check":
            check = True
        elif args[i] == "--clean":
            clean = True
        elif args[i] == "-o" and i + 1 < len(args):
            output = args[i + 1]
            i += 1
        elif not args[i].startswith("-"):
            directory = args[i]
        i += 1

    return build_project(directory, output, check, clean)


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
