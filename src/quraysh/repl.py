"""
REPL — الواجهة التفاعلية
=========================

Read-Eval-Print Loop — الواجهة التفاعلية للمستخدم.
"""

import sys
from .evaluator import Quraysh


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🕋  لسان قريش — Quraysh  🕋          ║
║                                          ║
║   لغة برمجة عربية كاملة                  ║
║   الإصدار 2.0.0                          ║
║                                          ║
╚══════════════════════════════════════════╝

اكتب (انصرف) للخروج
"""

PROMPT = "قريش> "


def main():
    """نقطة الدخول — المفسر التفاعلي."""
    q = Quraysh()

    print(BANNER)

    while True:
        try:
            # قراءة السطر
            line = input(PROMPT).strip()

            # تجاهل الفراغ
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


def run_file(path: str):
    """تشغيل ملف."""
    q = Quraysh()
    try:
        q.eval_file(path)
    except FileNotFoundError:
        print(f"الملف غير موجود: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"خطأ: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # إذا فيه معامل — تشغيل ملف
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        main()
