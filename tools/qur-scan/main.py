"""
qur-scan — نقطة الدخول
"""

import sys
from . import __version__
from . import system


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🔍  qur-scan — فحص الجهاز  🔍       ║
║                                          ║
║   أداة عربية لمراقبة نظامك                ║
║   الإصدار 0.1.0                          ║
║                                          ║
╚══════════════════════════════════════════╝

⚠️  هذه الأداة لجهازك فقط.
"""


# ═══════════════════════════════════════════════════════════
#  الأوامر
# ═══════════════════════════════════════════════════════════

def cmd_info(args):
    """معلومات النظام"""
    system.run_all()
    return 0


def cmd_cpu(args):
    """CPU"""
    system.cpu()
    return 0


def cmd_ram(args):
    """RAM"""
    system.ram()
    return 0


def cmd_storage(args):
    """التخزين"""
    system.storage()
    return 0


def cmd_kernel(args):
    """النواة"""
    system.kernel()
    return 0


def cmd_android(args):
    """أندرويد"""
    system.android()
    return 0


def cmd_list(args):
    """عرض الأوامر"""
    print(BANNER)
    print("🛠️  الأوامر المتاحة:")
    print()
    print("  qur-scan info       معلومات النظام (5)")
    print("  qur-scan cpu        المعالج")
    print("  qur-scan ram        الذاكرة")
    print("  qur-scan storage    التخزين")
    print("  qur-scan kernel     النواة")
    print("  qur-scan android    أندرويد")
    print("  qur-scan list       عرض الأوامر")
    print("  qur-scan version    الإصدار")
    print("  qur-scan help       المساعدة")
    print()
    return 0


def cmd_version(args):
    """الإصدار"""
    print(f"qur-scan — الإصدار {__version__}")
    return 0


def cmd_help(args):
    """المساعدة"""
    print(BANNER)
    cmd_list([])
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

الأوامر = {
    'info': cmd_info,
    'cpu': cmd_cpu,
    'ram': cmd_ram,
    'storage': cmd_storage,
    'kernel': cmd_kernel,
    'android': cmd_android,
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
