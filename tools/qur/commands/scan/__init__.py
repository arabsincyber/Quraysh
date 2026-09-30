"""
qur scan — أداة الفحص الأخلاقي
"""

from . import info

__version__ = "0.1.0"

WARNING = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ⚠️  تحذير — qur scan                                   ║
║                                                          ║
║  هذه الأداة للفحص الأخلاقي فقط.                          ║
║                                                          ║
║  مسموح:                                                  ║
║    ✅  فحص أنظمتك الخاصة.                                 ║
║    ✅  فحص بموافقة كتابية.                                ║
║    ✅  فحص بيئات التدريب.                                 ║
║                                                          ║
║  ممنوع:                                                  ║
║    ❌  فحص أنظمة الآخرين.                                 ║
║    ❌  أي نشاط غير قانوني.                                ║
║                                                          ║
║  من يستخدمها بهذه الطرق — يخالف LICENSE.                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def show_warning():
    print(WARNING)
    print()
    response = input("هل توافق على الشروط؟ [y/N]: ").strip().lower()
    return response == "y"


def run(args):
    """نقطة الدخول — qur scan"""
    if not args:
        print("🔍 qur scan — أداة الفحص الأخلاقي")
        print()
        print("⚠️  للفحص الأخلاقي فقط.")
        print()
        print("الاستخدام:")
        print("  qur scan info <target>      جمع المعلومات (10 خاصيات)")
        print("  qur scan whois <target>     WHOIS")
        print("  qur scan dns <target>       DNS")
        return 0

    أمر = args[0]
    target = args[1] if len(args) > 1 else None

    if not show_warning():
        print("❌ تم إلغاء الفحص")
        return 1

    if أمر == "info" and target:
        info.run_all(target)
    elif أمر == "whois" and target:
        info.whois(target)
    elif أمر == "dns" and target:
        info.dns(target)
    else:
        print(f"❌ أمر غير معروف: {أمر}")
        return 1

    return 0
