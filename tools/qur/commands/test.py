"""
qur test — إطار الاختبارات
============================

تشغيل اختبارات "لسان قريش".

الاستخدام:
    qur test                    كل الاختبارات
    qur test <dir>              مجلد
    qur test <file>             ملف
    qur test --verbose          تفصيلي
"""

import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  تشغيل الاختبارات
# ═══════════════════════════════════════════════════════════

def load_quraysh():
    """تحميل مفسر قريش"""
    src_path = Path(__file__).parent.parent.parent.parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    from quraysh.evaluator import Quraysh
    return Quraysh()


def extract_tests(source):
    """
    يستخرج الاختبارات من الكود.

    الشكل:
        (اختبار "اسم الاختبار"
            (نظير (تعبير) قيمة))
    """
    import re

    tests = []

    # نمط: (اختبار "..." (نظير ... ...))
    pattern = re.compile(
        r'\(اختبار\s+"([^"]+)"\s+\(نظير\s+(.+?)\)\)',
        re.DOTALL
    )

    for match in pattern.finditer(source):
        اسم = match.group(1)
        جسم = match.group(2)

        # نقسم الجسم إلى تعبيرين
        parts = split_expression(جسم)
        if len(parts) >= 2:
            tests.append({
                'name': اسم,
                'actual': parts[0].strip(),
                'expected': parts[1].strip(),
            })

    return tests


def split_expression(text):
    """يقسم تعبير إلى جزءين — حسب التوازن"""
    balance = 0
    parts = []
    current = []

    for char in text:
        if char == '(':
            balance += 1
            current.append(char)
        elif char == ')':
            balance -= 1
            current.append(char)
            if balance == 0 and current:
                parts.append(''.join(current))
                current = []
        elif balance == 0 and char.isspace():
            if current:
                parts.append(''.join(current))
                current = []
        else:
            current.append(char)

    if current:
        parts.append(''.join(current))

    return parts


def run_test(q, test, verbose=False):
    """يشغّل اختبار واحد"""
    اسم = test['name']

    try:
        # تقييم الفعلي
        actual = q.eval_string(test['actual'])

        # تقييم المتوقع
        expected = q.eval_string(test['expected'])

        # المقارنة
        passed = (actual == expected)

        if passed:
            print(f"  ✓ {اسم}")
        else:
            print(f"  ❌ {اسم}")
            print(f"      المتوقع: {expected}")
            print(f"      الفعلي:  {actual}")

        return passed

    except Exception as e:
        print(f"  ❌ {اسم} — خطأ:")
        print(f"      {e}")
        return False


def run_tests(مسار, verbose=False):
    """يشغّل الاختبارات من ملف أو مجلد"""
    مسار = Path(مسار)

    # تحديد الملفات
    if مسار.is_file():
        ملفات = [مسار]
    elif مسار.is_dir():
        ملفات = sorted(مسار.glob("**/*.lisp"))
    else:
        print(f"❌ غير موجود: {مسار}")
        return 1

    if not ملفات:
        print(f"❌ لا توجد ملفات .lisp")
        return 1

    print(f"🧪 اختبار: {مسار}")
    print()

    # تحميل المفسر
    try:
        q = load_quraysh()
    except Exception as e:
        print(f"❌ فشل تحميل المفسر: {e}")
        return 1

    الإجمالي = 0
    الناجحة = 0
    الملفات_باختبارات = 0

    for ملف in ملفات:
        try:
            source = ملف.read_text(encoding="utf-8")
            tests = extract_tests(source)

            if not tests:
                if verbose:
                    print(f"📄 {ملف.name} — لا توجد اختبارات")
                continue

            الملفات_باختبارات += 1
            print(f"📄 {ملف.name} ({len(tests)} اختبار)")

            for test in tests:
                الإجمالي += 1
                if run_test(q, test, verbose):
                    الناجحة += 1
            print()

        except Exception as e:
            print(f"❌ خطأ في {ملف.name}: {e}")
            print()

    # التقرير
    print("=" * 50)
    print(f"  📊 النتيجة:")
    print()
    print(f"     الملفات:   {الملفات_باختبارات}")
    print(f"     الاختبارات: {الإجمالي}")
    print(f"     الناجحة:    {الناجحة}")
    print(f"     الفاشلة:    {الإجمالي - الناجحة}")
    print("=" * 50)

    if الإجمالي == 0:
        print()
        print("⚠️  لا توجد اختبارات.")
        print()
        print("💡 لكتابة اختبار:")
        print('   (اختبار "اسم الاختبار"')
        print('       (نظير (تعبير) قيمة))')
        return 1

    if الناجحة == الإجمالي:
        print()
        print("🎉 كل الاختبارات نجحت!")
        return 0
    else:
        print()
        print(f"❌ فشل {الإجمالي - الناجحة} اختبار")
        return 1


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل test"""
    verbose = False
    مسار = "tests"

    for arg in args:
        if arg == "--verbose" or arg == "-v":
            verbose = True
        elif not arg.startswith("-"):
            مسار = arg

    # إذا ما فيه مجلد — نبحث عن tests
    if not Path(مسار).exists():
        if Path(".").exists():
            مسار = "."

    return run_tests(مسار, verbose)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
