"""
qur pack — تغليف المشاريع
============================

تغليف مشاريع "لسان قريش" لنشرها.

الاستخدام:
    qur pack                    تغليف المشروع الحالي
    qur pack -o name.qur        اسم مخرج
    qur pack --list             عرض الحزم المثبتة
    qur pack --info <file>      معلومات حزمة
"""

import tarfile
import json
from pathlib import Path
from datetime import datetime


PACKAGE_EXT = ".qur"
DEFAULT_VERSION = "1.0.0"


# ═══════════════════════════════════════════════════════════
#  جمع الملفات
# ═══════════════════════════════════════════════════════════

def collect_files(directory="."):
    """يجمع ملفات المشروع"""
    مسار = Path(directory)
    ignore = {"build", "__pycache__", ".git", "dist", "node_modules", ".venv"}

    ملفات = []
    for f in مسار.rglob("*"):
        if not f.is_file():
            continue
        # تجاهل المجلدات المستثناة
        if any(p in f.parts for p in ignore):
            continue
        # تجاهل الملفات المؤقتة
        if f.suffix in (".pyc", ".pyo", ".tmp", ".log"):
            continue
        ملفات.append(f)

    return sorted(ملفات)


def detect_name(directory="."):
    """يكتشف اسم المشروع"""
    مسار = Path(directory)

    # من README
    readme = مسار / "README.md"
    if readme.exists():
        first = readme.read_text(encoding="utf-8").splitlines()[0]
        if first.startswith("# "):
            return first[2:].strip().replace(" ", "-")

    # من اسم المجلد
    return مسار.resolve().name


def detect_version(directory="."):
    """يكتشف الإصدار"""
    مسار = Path(directory)

    version_file = مسار / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()

    return DEFAULT_VERSION


# ═══════════════════════════════════════════════════════════
#  التغليف
# ═══════════════════════════════════════════════════════════

def create_metadata(name, version, files):
    """يولّد metadata.json"""
    return {
        "name": name,
        "version": version,
        "created": datetime.now().isoformat(),
        "files": [str(f) for f in files],
        "count": len(files),
    }


def pack_project(directory=".", output=None):
    """يغلّف المشروع"""
    مسار = Path(directory)

    if not مسار.exists():
        print(f"❌ المجلد غير موجود: {directory}")
        return 1

    # 1. المعلومات
    name = detect_name(directory)
    version = detect_version(directory)
    files = collect_files(directory)

    if not files:
        print(f"❌ لا توجد ملفات في: {directory}")
        return 1

    # 2. الاسم الافتراضي
    if output is None:
        output = f"{name}-{version}{PACKAGE_EXT}"
    output = Path(output)

    print(f"📦 جاري التغليف...")
    print()
    print(f"  📝 الاسم:    {name}")
    print(f"  🔢 الإصدار:  {version}")
    print(f"  📁 الملفات:  {len(files)}")
    print(f"  💾 المخرج:   {output}")
    print()

    # 3. metadata
    metadata = create_metadata(name, version, files)
    metadata_file = مسار / ".qur-metadata.json"
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 4. التغليف
    try:
        with tarfile.open(output, "w:gz") as tar:
            # نضيف metadata
            tar.add(metadata_file, arcname=".qur-metadata.json")

            # نضيف الملفات
            for f in files:
                arcname = str(f.relative_to(مسار))
                tar.add(f, arcname=arcname)
                print(f"  ✓ {arcname}")

        # 5. إزالة metadata المؤقت
        metadata_file.unlink()

        # 6. التقرير
        size = output.stat().st_size
        size_kb = size / 1024

        print()
        print(f"✅ تم التغليف بنجاح!")
        print()
        print(f"  📦 الملف:   {output}")
        print(f"  📊 الحجم:   {size_kb:.2f} KB")
        print(f"  📁 الملفات: {len(files)}")

        return 0

    except Exception as e:
        print(f"❌ فشل التغليف: {e}")
        # تنظيف
        if metadata_file.exists():
            metadata_file.unlink()
        return 1


def list_packages(directory="."):
    """يعرض الحزم في المجلد"""
    مسار = Path(directory)
    حزم = sorted(مسار.glob(f"*{PACKAGE_EXT}"))

    if not حزم:
        print(f"📦 لا توجد حزم في: {directory}")
        return 0

    print(f"📦 الحزم المتوفرة في {directory}:")
    print()

    for حزمة in حزم:
        size = حزمة.stat().st_size / 1024
        print(f"  📦 {حزمة.name} ({size:.2f} KB)")

    print()
    print(f"  الإجمالي: {len(حزم)} حزمة")
    return 0


def show_info(file_path):
    """يعرض معلومات حزمة"""
    ملف = Path(file_path)

    if not ملف.exists():
        print(f"❌ غير موجود: {file_path}")
        return 1

    try:
        with tarfile.open(ملف, "r:gz") as tar:
            # ابحث عن metadata
            try:
                metadata_member = tar.getmember(".qur-metadata.json")
                f = tar.extractfile(metadata_member)
                metadata = json.loads(f.read().decode("utf-8"))
            except KeyError:
                print("⚠️  لا توجد بيانات وصفية")
                return 0

            print(f"📦 معلومات الحزمة:")
            print()
            print(f"  📝 الاسم:    {metadata.get('name', '?')}")
            print(f"  🔢 الإصدار:  {metadata.get('version', '?')}")
            print(f"  📅 التاريخ:  {metadata.get('created', '?')}")
            print(f"  📁 الملفات:  {metadata.get('count', '?')}")
            print()
            print("  📄 قائمة الملفات:")
            for f in metadata.get("files", []):
                print(f"    - {f}")

    except Exception as e:
        print(f"❌ خطأ: {e}")
        return 1

    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل pack"""
    if not args:
        return pack_project(".")

    output = None
    directory = "."
    list_flag = False
    info_file = None

    i = 0
    while i < len(args):
        if args[i] == "--list":
            list_flag = True
        elif args[i] == "--info" and i + 1 < len(args):
            info_file = args[i + 1]
            i += 1
        elif args[i] == "-o" and i + 1 < len(args):
            output = args[i + 1]
            i += 1
        elif not args[i].startswith("-"):
            directory = args[i]
        i += 1

    if list_flag:
        return list_packages(directory)

    if info_file:
        return show_info(info_file)

    return pack_project(directory, output)


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
