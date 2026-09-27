"""
REPL — الواجهة التفاعلية
=========================

Read-Eval-Print Loop — الواجهة التفاعلية للمستخدم.

الميزات:
- تشغيل تفاعلي (REPL)
- تشغيل ملفات مع فحص العقد الأمني
- الصندوق الزجاجي (محاكاة قبل التنفيذ)
"""

import sys
from pathlib import Path
from .evaluator import Quraysh
from .security import parse_contract, SecurityViolation
from .sandbox import Sandbox, عرض_المحاكاة


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🕋  لسان قريش — Quraysh  🕋          ║
║                                          ║
║   لغة برمجة عربية كاملة                  ║
║   الإصدار 2.1.0                          ║
║                                          ║
║   🔒 الأمان بالوضوح                       ║
║                                          ║
╚══════════════════════════════════════════╝

اكتب (انصرف) للخروج
"""

PROMPT = "قريش> "


# ============================================================
#  REPL التفاعلي
# ============================================================

def main():
    """نقطة الدخول — المفسر التفاعلي."""
    q = Quraysh()
    print(BANNER)

    while True:
        try:
            line = input(PROMPT).strip()
            if not line:
                continue

            if line in ("(انصرف)", "انصرف", "(خروج)", "خروج", "exit", "quit"):
                print("مع السلامة 💙")
                break

            try:
                result = q.eval_string(line)
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"خطأ: {e}")

        except (KeyboardInterrupt, EOFError):
            print()
            print("مع السلامة 💙")
            break
        except Exception as e:
            print(f"خطأ غير متوقع: {e}")


# ============================================================
#  تشغيل ملف — مع الصندوق الزجاجي
# ============================================================

def run_file(path: str, skip_sandbox: bool = False):
    """تشغيل ملف مع التحقق الأمني والمحاكاة."""

    # 1. قراءة الملف
    try:
        source = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}", file=sys.stderr)
        sys.exit(1)

    print("🔍 فحص العقد الأمني...")
    print()

    # 2. فحص العقد الأمني
    try:
        عقد = parse_contract(source)
        print(عقد.ملخص())
        print()

        if not عقد.اسم_المطور or عقد.اسم_المطور == "غير معروف":
            print("⚠️  تحذير: الملف لا يحتوي على عقد أمني")
            print()
            response = input("    هل تريد المتابعة على مسؤوليتك؟ [y/N]: ")
            if response.lower() != "y":
                print("🚫 تم إلغاء التشغيل")
                sys.exit(1)
        else:
            print("✅ العقد صحيح")

    except SecurityViolation as e:
        print(f"🚫 انتهاك أمني: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. الصندوق الزجاجي (المحاكاة)
    if not skip_sandbox:
        print()
        print("🔍 جاري تحليل العمليات...")

        sb = Sandbox()
        عمليات = sb.حلل(source)

        print(عرض_المحاكاة(عمليات, sb.الأذونات_المستخدمة))

        # طلب الموافقة
        try:
            response = input("هل تريد التنفيذ الفعلي؟ [Y/n]: ").strip().lower()
            if response and response != "y":
                print("🚫 تم إلغاء التنفيذ")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print()
            print("🚫 تم إلغاء التنفيذ")
            sys.exit(0)

    # 4. التنفيذ
    print()
    print("🚀 التنفيذ:")
    print("─" * 44)
    print()

    q = Quraysh()
    try:
        q.eval_file(path)
    except Exception as e:
        print(f"❌ خطأ في التنفيذ: {e}", file=sys.stderr)
        sys.exit(1)

    print()
    print("─" * 44)
    print("✅ اكتمل التنفيذ بنجاح")


# ============================================================
#  نقطة الدخول
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:]

    # خيار تخطي الصندوق الزجاجي
    skip = "--no-sandbox" in args
    if skip:
        args.remove("--no-sandbox")

    if args:
        run_file(args[0], skip_sandbox=skip)
    else:
        main()
