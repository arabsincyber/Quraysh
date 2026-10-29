import compileall
import os
import shutil
import glob

print("╭──────────────────────────────────────────╮")
print("│   🔐 لسان قريش - مشفر الكود              │")
print("│       (النسخة المضمونة 100%)             │")
print("╰──────────────────────────────────────────╯\n")

# مسح المجلد القديم إذا وجد
if os.path.exists("dist_intel"):
    shutil.rmtree("dist_intel")

# إنشاء مجلدات جديدة
os.makedirs("dist_intel/qur-intel", exist_ok=True)
os.makedirs("dist_intel/quraysh/intel", exist_ok=True)

# 1. تجميع ملفات main.py
print("[*] جاري تشفير ملف main.py...")
compileall.compile_file("tools/qur-intel/main.py", quiet=1)
# نسخ ملف main.pyc الناتج
main_pyc = glob.glob("tools/qur-intel/__pycache__/main*.pyc")
if main_pyc:
    shutil.copy(main_pyc[0], "dist_intel/qur-intel/main.pyc")
    print("  ✅ main.pyc")

# 2. تجميع ملفات مجلد src/quraysh/intel
print("[*] جاري تشفير ملفات intel...")
compileall.compile_dir("src/quraysh/intel", quiet=1)
# نسخ الملفات المشفرة
intel_pyc = glob.glob("src/quraysh/intel/__pycache__/*.pyc")
for f in intel_pyc:
    filename = os.path.basename(f)
    if filename != "__init__.cpython-313.pyc":
        shutil.copy(f, f"dist_intel/quraysh/intel/{filename}")
        print(f"  ✅ {filename}")

print("\n✅ تم التشفير بنجاح!")
print("💾 الملفات المشفرة في: dist_intel/")
print("\n💡 لتشغيل النسخة المشفرة:")
print("   PYTHONPATH=dist_intel python3 dist_intel/qur-intel/main.pyc")
