"""
qur — نقطة الدخول
==================

مركز أدوات "لسان قريش".
"""

import sys
import os
from pathlib import Path

from . import __version__


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║         🛠️  qur — أدوات قريش  🛠️         ║
║                                          ║
║   مركز الأدوات الرسمي للغة                ║
║                                          ║
╚══════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════
#  الأوامر
# ═══════════════════════════════════════════════════════════

def cmd_new(args):
    """إنشاء مشروع جديد"""
    if not args:
        print("❌ الاستخدام: qur new <اسم-المشروع>")
        return 1

    اسم = args[0]
    مسار = Path(اسم)

    if مسار.exists():
        print(f"❌ المجلد موجود: {اسم}")
        return 1

    مسار.mkdir(parents=True)
    (مسار / "src").mkdir()
    (مسار / "tests").mkdir()
    (مسار / "examples").mkdir()

    (مسار / "README.md").write_text(f"# {اسم}\n\nمشروع مكتوب بـ لسان قريش.\n")
    (مسار / "main.lisp").write_text("; مشروع جديد\n(اطبع \"السلام عليكم\")\n")
    (مسار / ".gitignore").write_text("__pycache__/\n*.pyc\n")

    print(f"✅ تم إنشاء المشروع: {اسم}")
    print(f"📁 المسار: {مسار.absolute()}")
    print()
    print("للبدء:")
    print(f"  cd {اسم}")
    print("  qur run main.lisp")
    return 0


def cmd_init(args):
    """تهيئة مشروع في المجلد الحالي"""
    مسار = Path.cwd()

    (مسار / "src").mkdir(exist_ok=True)
    (مسار / "tests").mkdir(exist_ok=True)
    (مسار / "examples").mkdir(exist_ok=True)

    if not (مسار / "README.md").exists():
        (مسار / "README.md").write_text(f"# {مسار.name}\n\nمشروع مكتوب بـ لسان قريش.\n")

    if not (مسار / "main.lisp").exists():
        (مسار / "main.lisp").write_text("; مشروع جديد\n(اطبع \"السلام عليكم\")\n")

    print(f"✅ تم تهيئة المشروع في: {مسار}")
    return 0


def cmd_run(args):
    """تشغيل ملف"""
    if not args:
        print("❌ الاستخدام: qur run <ملف>")
        return 1

    ملف = Path(args[0])
    if not ملف.exists():
        print(f"❌ الملف غير موجود: {ملف}")
        return 1

    # استدعاء المفسر
    try:
        # إضافة مسار src إلى sys.path
        src_path = Path(__file__).parent.parent.parent.parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))

        from quraysh.repl import run_file
        run_file(str(ملف), skip_sandbox=False)
        return 0
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return 1
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        return 1


def cmd_check(args):
    """فحص ملف"""
    if not args:
        print("❌ الاستخدام: qur check <ملف>")
        return 1

    ملف = Path(args[0])
    if not ملف.exists():
        print(f"❌ الملف غير موجود: {ملف}")
        return 1

    # فحص نحوي (بسيط)
    try:
        src_path = Path(__file__).parent.parent.parent.parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))

        from quraysh.lexer import tokenize
        from quraysh.parser import parse_all

        نص = ملف.read_text(encoding="utf-8")
        رموز = tokenize(نص)
        تعبيرات = parse_all(نص)

        print(f"✅ الفحص نجح: {ملف}")
        print(f"   الرموز: {len(رموز)}")
        print(f"   التعبيرات: {len(تعبيرات)}")
        return 0
    except Exception as e:
        print(f"❌ فشل الفحص: {e}")
        return 1


def cmd_list(args):
    """عرض الأدوات المتاحة"""
    print(BANNER)
    print("🛠️  الأوامر المتاحة:")
    print()
    print("  qur new <اسم>       إنشاء مشروع جديد")
    print("  qur init            تهيئة مشروع")
    print("  qur run <file>      تشغيل ملف")
    print("  qur check <file>    فحص ملف")
    print("  qur list            عرض الأوامر")
    print("  qur version         عرض الإصدار")
    print("  qur help            المساعدة")
    print()
    return 0


def cmd_version(args):
    """عرض الإصدار"""
    print(f"qur — الإصدار {__version__}")
    print("لسان قريش — مركز الأدوات")
    return 0


def cmd_help(args):
    """المساعدة"""
    print(BANNER)
    print("الاستخدام:")
    print("  qur <أمر> [خيارات]")
    print()
    cmd_list([])
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

الأوامر = {
    'new': cmd_new,
    'init': cmd_init,
    'run': cmd_run,
    'check': cmd_check,
    'list': cmd_list,
    'version': cmd_version,
    'help': cmd_help,
}


def main():
    """نقطة الدخول الرئيسية"""
    args = sys.argv[1:]

    # بدون أوامر
    if not args:
        print(BANNER)
        cmd_list([])
        return 0

    # خيارات خاصة
    if args[0] in ('--version', '-v'):
        return cmd_version([])

    if args[0] in ('--help', '-h'):
        return cmd_help([])

    if args[0] in ('--list', '-l'):
        return cmd_list([])

    # الأوامر
    أمر = args[0]
    if أمر not in الأوامر:
        print(f"❌ أمر غير معروف: {أمر}")
        print()
        cmd_list([])
        return 1

    return الأوامر[أمر](args[1:])


if __name__ == "__main__":
    sys.exit(main())
