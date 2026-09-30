"""
qur — نقطة الدخول
"""

import sys
from pathlib import Path

from . import __version__
from .commands import pkg, fmt, build, doc, test, pack


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║         🛠️  qur — أدوات قريش  🛠️         ║
║                                          ║
║   مركز الأدوات الرسمي للغة                ║
║                                          ║
╚══════════════════════════════════════════╝
"""


def cmd_new(args):
    if not args:
        print("❌ الاستخدام: qur new <اسم>")
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
    return 0


def cmd_init(args):
    مسار = Path.cwd()
    (مسار / "src").mkdir(exist_ok=True)
    (مسار / "tests").mkdir(exist_ok=True)
    (مسار / "examples").mkdir(exist_ok=True)
    if not (مسار / "README.md").exists():
        (مسار / "README.md").write_text(f"# {مسار.name}\n\nمشروع.\n")
    if not (مسار / "main.lisp").exists():
        (مسار / "main.lisp").write_text("(اطبع \"السلام عليكم\")\n")
    print(f"✅ تم تهيئة المشروع في: {مسار}")
    return 0


def cmd_run(args):
    if not args:
        print("❌ الاستخدام: qur run <ملف>")
        return 1
    ملف = Path(args[0])
    if not ملف.exists():
        print(f"❌ الملف غير موجود: {ملف}")
        return 1
    try:
        src_path = Path(__file__).parent.parent.parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        from quraysh.repl import run_file
        skip = "--no-sandbox" in args
        run_file(str(ملف), skip_sandbox=skip)
        return 0
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return 1


def cmd_check(args):
    if not args:
        print("❌ الاستخدام: qur check <ملف>")
        return 1
    ملف = Path(args[0])
    if not ملف.exists():
        print(f"❌ الملف غير موجود: {ملف}")
        return 1
    try:
        src_path = Path(__file__).parent.parent.parent / "src"
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


def cmd_pkg(args):
    return pkg.run(args)


def cmd_fmt(args):
    return fmt.run(args)


def cmd_build(args):
    return build.run(args)


def cmd_doc(args):
    return doc.run(args)


def cmd_test(args):
    return test.run(args)


def cmd_pack(args):
    return pack.run(args)


def cmd_list(args):
    print(BANNER)
    print("🛠️  الأوامر المتاحة:")
    print()
    print("  qur new <اسم>              إنشاء مشروع جديد")
    print("  qur init                   تهيئة مشروع")
    print("  qur run <file>             تشغيل ملف")
    print("  qur check <file>           فحص ملف")
    print("  qur pkg <أمر>              مدير الحزم")
    print("  qur fmt <أمر>              منسّق الكود")
    print("  qur build [--check]        بناء المشروع")
    print("  qur doc <file|--all>       توليد الوثائق")
    print("  qur test [dir]             تشغيل الاختبارات")
    print("  qur pack [dir]             تغليف المشروع")
    print("  qur list                   عرض الأوامر")
    print("  qur version                عرض الإصدار")
    print("  qur help                   المساعدة")
    print()
    return 0


def cmd_version(args):
    print(f"qur — الإصدار {__version__}")
    print("لسان قريش — مركز الأدوات")
    return 0


def cmd_help(args):
    print(BANNER)
    print("الاستخدام:")
    print("  qur <أمر> [خيارات]")
    print()
    cmd_list([])
    return 0


الأوامر = {
    'new': cmd_new,
    'init': cmd_init,
    'run': cmd_run,
    'check': cmd_check,
    'pkg': cmd_pkg,
    'fmt': cmd_fmt,
    'build': cmd_build,
    'doc': cmd_doc,
    'test': cmd_test,
    'pack': cmd_pack,
    'list': cmd_list,
    'version': cmd_version,
    'help': cmd_help,
}


def main():
    args = sys.argv[1:]
    if not args:
        print(BANNER)
        cmd_list([])
        return 0
    if args[0] in ('--version', '-v'):
        return cmd_version([])
    if args[0] in ('--help', '-h'):
        return cmd_help([])
    if args[0] in ('--list', '-l'):
        return cmd_list([])
    أمر = args[0]
    if أمر not in الأوامر:
        print(f"❌ أمر غير معروف: {أمر}")
        print()
        cmd_list([])
        return 1
    return الأوامر[أمر](args[1:])


if __name__ == "__main__":
    sys.exit(main())
