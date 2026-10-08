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
from .tutor import مساعد_لسان_قريش, مساعد_دمج


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🕋  لسان قريش — Quraysh  🕋          ║
║                                          ║
║   لغة برمجة عربية كاملة                  ║
║   الإصدار 3.0.0                          ║
║                                          ║
║   🔒 الأمان بالوضوح                       ║
║                                          ║
╚══════════════════════════════════════════╝

🎓 المساعد الذكي متاح:
   .اشرح <دالة>    — شرح دالة
   .اقترح <موضوع>  — اقتراح أمثلة
   .راجع           — فحص الكود الأخير
   .مساعدة         — عرض المساعدة

اكتب (انصرف) للخروج
"""

PROMPT = "قريش> "


# ============================================================
#  REPL التفاعلي
# ============================================================

# ============================================================
#  أوامر المساعد
# ============================================================

def _اعرض_مساعدة():
    """يعرض قائمة أوامر المساعد"""
    print("""
╔══════════════════════════════════════════╗
║  🎓 أوامر المساعد الذكي                   ║
╠══════════════════════════════════════════╣
║  .اشرح <دالة>      — شرح دالة            ║
║  .اقترح <موضوع>    — أمثلة (تشفير، شبكة) ║
║  .راجع             — فحص الكود الأخير    ║
║  .مساعدة           — هذه القائمة          ║
╚══════════════════════════════════════════╝
""")


def _تعامل_مع_أمر(line, مساعد, سجل_الكود):
    """يتعامل مع أوامر المساعد — يرجع True لو تعامل معها"""
    if not line.startswith("."):
        return False

    أجزاء = line[1:].split(maxsplit=1)
    if not أجزاء:
        return False

    أمر = أجزاء[0]
    وسيط = أجزاء[1] if len(أجزاء) > 1 else ""

    # .مساعدة
    if أمر in ("مساعدة", "help", "؟"):
        _اعرض_مساعدة()
        return True

    # .اشرح
    if أمر in ("اشرح", "شرح"):
        if not وسيط:
            print("⚠️ استخدم: .اشرح <دالة>")
            return True
        نتيجة = مساعد.اشرح_دالة(وسيط)
        if نتيجة:
            print(f"\n📖 {نتيجة['الدالة']}")
            print(f"   {نتيجة['الوصف']}")
            print(f"   مثال: {نتيجة['المثال']}\n")
        else:
            # اقترح بديل
            اقتراح = مساعد.صحّح_دالة(وسيط)
            if اقتراح:
                print(f"\n❌ الدالة '{وسيط}' غير معروفة")
                print(f"🎓 هل قصدت: {اقتراح['البديل']}؟ ({اقتراح['الثقة']}%)")
                print(f"   {اقتراح['الشرح']}")
                print(f"   مثال: {اقتراح['المثال']}\n")
            else:
                print(f"\n❌ الدالة '{وسيط}' غير معروفة\n")
        return True

    # .اقترح
    if أمر in ("اقترح", "أمثلة"):
        if not وسيط:
            print("⚠️ استخدم: .اقترح <موضوع> (تشفير، شبكة، قاعدة، ملف، رياضيات)")
            return True
        نتيجة = مساعد.اقترح_مثال(وسيط)
        if نتيجة:
            print(f"\n💡 أمثلة: {وسيط}")
            for م in نتيجة:
                print(f"   {م['المثال']}")
                print(f"      └ {م['الشرح']}")
            print()
        else:
            print(f"\n⚠️ لا توجد أمثلة لموضوع: {وسيط}\n")
        return True

    # .راجع
    if أمر in ("راجع", "فحص"):
        if not سجل_الكود:
            print("⚠️ لا يوجد كود للمراجعة — اكتب كود أولاً")
            return True
        تقرير = مساعد.اكتب_تقرير(سجل_الكود[-1])
        print(تقرير)
        return True

    return False


# ============================================================
#  REPL
# ============================================================

def main():
    """نقطة الدخول — المفسر التفاعلي."""
    q = Quraysh()
    مساعد = مساعد_دمج()
    سجل_الكود = []  # آخر الأكواد المُدخلة

    print(BANNER)

    while True:
        try:
            line = input(PROMPT).strip()
            if not line:
                continue

            # أوامر الخروج
            if line in ("(انصرف)", "انصرف", "(خروج)", "خروج", "exit", "quit"):
                print("مع السلامة 💙")
                break

            # أوامر المساعد
            if _تعامل_مع_أمر(line, مساعد, سجل_الكود):
                continue

            # تنفيذ عادي
            سجل_الكود.append(line)
            if len(سجل_الكود) > 10:
                سجل_الكود.pop(0)

            try:
                result = q.eval_string(line)
                if result is not None:
                    print(result)
            except Exception as e:
                رسالة = str(e)
                print(f"❌ خطأ: {رسالة}")

                # اقتراح ذكي متعدد المستويات
                نتائج = مساعد.حلّل_خطأ_شامل(رسالة, line)
                if نتائج.get("اقتراحات") or نتائج.get("توقعات"):
                    print()
                    تقرير = مساعد.اكتب_تقرير_شامل(نتائج)
                    print(tقرير)

        except (KeyboardInterrupt, EOFError):
            print()
            print("مع السلامة 💙")
            break
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")


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
