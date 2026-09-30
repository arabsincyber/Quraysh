"""
qur-scan — نقطة الدخول
"""

import sys
from . import __version__
from . import system
from . import processes
from . import live


BANNER = """
╔══════════════════════════════════════════╗
║                                          ║
║      🔍  qur-scan — فحص الجهاز  🔍       ║
║                                          ║
║   أداة عربية لمراقبة نظامك                ║
║   الإصدار 0.3.0                          ║
║                                          ║
╚══════════════════════════════════════════╝

⚠️  هذه الأداة لجهازك فقط.
"""


def cmd_info(args):
    system.run_all(); return 0


def cmd_cpu(args):
    system.cpu(); return 0


def cmd_ram(args):
    system.ram(); return 0


def cmd_storage(args):
    system.storage(); return 0


def cmd_kernel(args):
    system.kernel(); return 0


def cmd_android(args):
    system.android(); return 0


def cmd_processes(args):
    processes.processes(); return 0


def cmd_top_cpu(args):
    processes.top_cpu(); return 0


def cmd_top_ram(args):
    processes.top_ram(); return 0


def cmd_search(args):
    if not args:
        print("❌ الاستخدام: qur-scan search <name>")
        return 1
    processes.search(args[0]); return 0


def cmd_kill(args):
    if not args:
        print("❌ الاستخدام: qur-scan kill <PID>")
        return 1
    processes.kill(args[0]); return 0


def cmd_live_cpu(args):
    live.live_cpu(interval=1, count=5); return 0


def cmd_live_ram(args):
    live.live_ram(interval=1, count=5); return 0


def cmd_live_processes(args):
    live.live_processes(interval=1, count=5); return 0


def cmd_environment(args):
    live.environment(); return 0


def cmd_report(args):
    live.report(); return 0


def cmd_list(args):
    print(BANNER)
    print("🛠️  الأوامر المتاحة:")
    print()
    print("  📊 النظام:")
    print("    qur-scan info           معلومات النظام (5)")
    print("    qur-scan cpu            المعالج")
    print("    qur-scan ram            الذاكرة")
    print("    qur-scan storage        التخزين")
    print("    qur-scan kernel         النواة")
    print("    qur-scan android        أندرويد")
    print()
    print("  📋 العمليات:")
    print("    qur-scan processes      قائمة العمليات")
    print("    qur-scan top-cpu        أعلى CPU")
    print("    qur-scan top-ram        أعلى RAM")
    print("    qur-scan search         بحث")
    print("    qur-scan kill           إنهاء عملية")
    print()
    print("  📡 المراقبة:")
    print("    qur-scan live-cpu       مراقبة CPU")
    print("    qur-scan live-ram       مراقبة RAM")
    print("    qur-scan live-processes العمليات")
    print("    qur-scan environment    البيئة")
    print("    qur-scan report         تقرير")
    print()
    print("  🔧 عام:")
    print("    qur-scan list           الأوامر")
    print("    qur-scan version        الإصدار")
    print("    qur-scan help           المساعدة")
    print()
    return 0


def cmd_version(args):
    print(f"qur-scan — الإصدار {__version__}")
    return 0


def cmd_help(args):
    print(BANNER)
    cmd_list([])
    return 0


الأوامر = {
    'info': cmd_info,
    'cpu': cmd_cpu,
    'ram': cmd_ram,
    'storage': cmd_storage,
    'kernel': cmd_kernel,
    'android': cmd_android,
    'processes': cmd_processes,
    'top-cpu': cmd_top_cpu,
    'top-ram': cmd_top_ram,
    'search': cmd_search,
    'kill': cmd_kill,
    'live-cpu': cmd_live_cpu,
    'live-ram': cmd_live_ram,
    'live-processes': cmd_live_processes,
    'environment': cmd_environment,
    'report': cmd_report,
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
