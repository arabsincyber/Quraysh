"""
REPL — الواجهة التفاعلية
=========================

Read-Eval-Print Loop — الواجهة التفاعلية للمستخدم.

الميزات:
- تشغيل تفاعلي (REPL)
- تشغيل ملفات مع فحص العقد الأمني
- عرض بانر جميل
"""

import sys
from pathlib import Path
from .evaluator import Quraysh
from .security import parse_contract, SecurityViolation


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🕋  لسان قريش — Quraysh  🕋          ║
║                                          ║
║   لغة برمجة عربية كاملة                  ║
║   الإصدار 2.0.0                          ║
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

            # الخروج
            if line in ("(انصرف)", "انصرف", "(خروج)", "خروج", "exit", "quit"):
                print("مع السلامة 💙")
                break

            # التقييم
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
#  تشغيل ملف — مع فحص العقد الأمني
# ============================================================

def run_file(path: str):
    """تشغيل ملف مع التحقق من العقد الأمني."""

    # 1. قراءة الملف
    try:
        source = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. فحص العقد الأمني
    print("🔍 فحص العقد الأمني...")
    print()

    try:
        عقد = parse_contract(source)
        print(عقد.ملخص())
        print()

        # إذا ما فيه عقد → تحذير
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

    # 3. التشغيل
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
    # إذا فيه معامل — تشغيل ملف
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        main()
