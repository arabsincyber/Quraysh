"""
Files — مكتبة الملفات
========================

دوال ملفات للغة "لسان قريش".
"""

from pathlib import Path
import shutil
import os

# المجلد الأساسي — متاح للكتابة
HOME = Path.home()


def اقرأ(file_path):
    """يقرأ ملف نصي"""
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        return f"❌ خطأ: {e}"


def اكتب(file_path, content):
    """يكتب ملف نصي"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(str(content), encoding="utf-8")
        return f"✅ تم الكتابة: {file_path}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def ضمّ(file_path, content):
    """يضيف لملف موجود"""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(str(content) + "\n")
        return f"✅ تم الإضافة: {file_path}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def انسخ(source, dest):
    """ينسخ ملف أو مجلد"""
    try:
        if Path(source).is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        return f"✅ تم النسخ: {source} → {dest}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def احذف(file_path):
    """يحذف ملف أو مجلد"""
    try:
        p = Path(file_path)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"✅ تم الحذف: {file_path}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def موجود(file_path):
    """يتحقق إذا كان الملف موجود"""
    return Path(file_path).exists()


def أنشئ_مجلد(dir_path):
    """ينشئ مجلد"""
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return f"✅ تم إنشاء المجلد: {dir_path}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def اذكر(dir_path="."):
    """يعرض محتويات مجلد"""
    try:
        p = Path(dir_path)
        if not p.exists():
            return f"❌ غير موجود: {dir_path}"
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        return [f"{'📁' if i.is_dir() else '📄'} {i.name}" for i in items]
    except Exception as e:
        return f"❌ خطأ: {e}"


def حجم(file_path):
    """يعرض حجم ملف بالبايت"""
    try:
        return Path(file_path).stat().st_size
    except Exception as e:
        return f"❌ خطأ: {e}"


def سطور(file_path):
    """يعدّ سطور ملف"""
    try:
        return len(Path(file_path).read_text(encoding="utf-8").splitlines())
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  الاختبار — يستخدم مجلد المنزل
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
#  سجل الدوال — للربط بالمفسّر
# ═══════════════════════════════════════════════════════════

دوال_الملفات = {
    "اقرأ": اقرأ,
    "اكتب": اكتب,
    "ضمّ": ضمّ,
    "انسخ": انسخ,
    "احذف": احذف,
    "موجود": موجود,
    "أنشئ_مجلد": أنشئ_مجلد,
    "اذكر": اذكر,
    "حجم": حجم,
    "سطور": سطور,
}

if __name__ == "__main__":
    print("=" * 60)
    print("  📁 Files — مكتبة الملفات")
    print("=" * 60)
    print()

    test_file = str(HOME / "test_files.txt")
    test_dir = str(HOME / "test_dir")

    print(f"📂 المسار: {test_file}")
    print()

    # 1. كتابة
    print("1️⃣ كتابة ملف:")
    print(f"   {اكتب(test_file, 'السلام عليكم')}")
    print()

    # 2. قراءة
    print("2️⃣ قراءة ملف:")
    print(f"   {اقرأ(test_file)}")
    print()

    # 3. إضافة
    print("3️⃣ إضافة:")
    print(f"   {ضمّ(test_file, 'أهلاً بك')}")
    print()

    # 4. حجم
    print("4️⃣ الحجم:")
    print(f"   {حجم(test_file)} بايت")
    print()

    # 5. سطور
    print("5️⃣ السطور:")
    print(f"   {سطور(test_file)}")
    print()

    # 6. موجود؟
    print("6️⃣ موجود؟:")
    print(f"   {موجود(test_file)}")
    print()

    # 7. مجلد
    print("7️⃣ إنشاء مجلد:")
    print(f"   {أنشئ_مجلد(test_dir)}")
    print()

    # 8. ذكر
    print("8️⃣ محتويات المنزل (أول 5):")
    for item in اذكر(str(HOME))[:5]:
        print(f"   {item}")
    print()

    # 9. حذف
    print("9️⃣ حذف:")
    print(f"   {احذف(test_file)}")
    print(f"   {احذف(test_dir)}")
    print()

    print("=" * 60)
