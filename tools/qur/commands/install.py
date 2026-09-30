"""
qur install — تثبيت الحزم
============================

تثبيت حزم "لسان قريش" من ملفات .qur.

الاستخدام:
    qur install <file.qur>              تثبيت من ملف
    qur install <file.qur> --to <dir>   تثبيت في مجلد
    qur install --list                  عرض المثبّتة
    qur install --remove <name>         إزالة حزمة
"""

import tarfile
import json
import shutil
from pathlib import Path


HOME = Path.home()
INSTALL_DIR = HOME / ".qur" / "installed"
INSTALL_DB = HOME / ".qur" / "installed.json"
PACKAGE_EXT = ".qur"


# ═══════════════════════════════════════════════════════════
#  قاعدة البيانات
# ═══════════════════════════════════════════════════════════

def ensure_dirs():
    """التأكد من وجود المجلدات"""
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    if not INSTALL_DB.exists():
        INSTALL_DB.write_text("{}", encoding="utf-8")


def load_db():
    """تحميل قاعدة البيانات"""
    ensure_dirs()
    try:
        return json.loads(INSTALL_DB.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_db(db):
    """حفظ قاعدة البيانات"""
    ensure_dirs()
    INSTALL_DB.write_text(
        json.dumps(db, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ═══════════════════════════════════════════════════════════
#  التثبيت
# ═══════════════════════════════════════════════════════════

def read_metadata(archive_path):
    """يقرأ metadata من الحزمة"""
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            try:
                member = tar.getmember(".qur-metadata.json")
                f = tar.extractfile(member)
                return json.loads(f.read().decode("utf-8"))
            except KeyError:
                return None
    except Exception as e:
        print(f"❌ خطأ في قراءة الحزمة: {e}")
        return None


def install_package(archive_path, target=None):
    """يثبّت حزمة من ملف .qur"""
    ملف = Path(archive_path)

    if not ملف.exists():
        print(f"❌ الملف غير موجود: {archive_path}")
        return 1

    if not ملف.name.endswith(PACKAGE_EXT):
        print(f"⚠️  تحذير: الامتداد ليس {PACKAGE_EXT}")

    # 1. قراءة metadata
    print(f"📦 جاري التثبيت: {ملف.name}")
    print()

    metadata = read_metadata(ملف)
    if metadata is None:
        print("❌ لا توجد بيانات وصفية في الحزمة")
        return 1

    name = metadata.get("name", ملف.stem)
    version = metadata.get("version", "?")
    file_count = metadata.get("count", 0)

    print(f"  📝 الاسم:    {name}")
    print(f"  🔢 الإصدار:  {version}")
    print(f"  📁 الملفات:  {file_count}")
    print()

    # 2. تحديد المجلد
    if target is None:
        target = INSTALL_DIR / f"{name}-{version}"
    else:
        target = Path(target)

    # إزالة القديم إذا موجود
    if target.exists():
        print(f"  ⚠️  إزالة النسخة القديمة: {target}")
        shutil.rmtree(target)

    target.mkdir(parents=True, exist_ok=True)

    # 3. فك الضغط
    try:
        with tarfile.open(ملف, "r:gz") as tar:
            # استخراج بدون metadata
            members = [
                m for m in tar.getmembers()
                if m.name != ".qur-metadata.json"
            ]
            tar.extractall(path=target, members=members)

        # إزالة الاسم الأصلي من المسارات
        # (لأن الملفات انضغطت بـ "مشروعي/main.lisp")
        _flatten_dir(target)

        # 4. حفظ في قاعدة البيانات
        db = load_db()
        db[name] = {
            "name": name,
            "version": version,
            "installed": str(target),
            "date": metadata.get("created", ""),
        }
        save_db(db)

        print(f"✅ تم التثبيت بنجاح!")
        print()
        print(f"  📁 المسار:   {target}")
        print(f"  📊 الإجمالي: {len(db)} حزمة مثبّتة")

        return 0

    except Exception as e:
        print(f"❌ فشل التثبيت: {e}")
        if target.exists():
            shutil.rmtree(target)
        return 1


def _flatten_dir(directory):
    """يفرد مجلد الحزمة — يزيل المستوى الإضافي"""
    directory = Path(directory)
    subdirs = [d for d in directory.iterdir() if d.is_dir()]

    # إذا فيه مجلد واحد فقط — ننقله للأعلى
    if len(subdirs) == 1 and not any(directory.glob("*.lisp")):
        subdir = subdirs[0]
        for item in subdir.iterdir():
            target = directory / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
        subdir.rmdir()


def list_installed():
    """يعرض الحزم المثبّتة"""
    db = load_db()

    if not db:
        print("📦 لا توجد حزم مثبّتة.")
        print()
        print("💡 للتثبيت:")
        print("   qur install <file.qur>")
        return 0

    print("📦 الحزم المثبّتة:")
    print()
    print(f"  {'الاسم':<20} {'الإصدار':<10} {'المسار'}")
    print("  " + "-" * 60)

    for name, info in db.items():
        version = info.get("version", "?")
        path = info.get("installed", "?")
        print(f"  {name:<20} {version:<10} {path}")

    print()
    print(f"  الإجمالي: {len(db)} حزمة")
    return 0


def remove_package(name):
    """يزيل حزمة"""
    db = load_db()

    if name not in db:
        print(f"❌ الحزمة غير مثبتة: {name}")
        return 1

    info = db[name]
    path = Path(info.get("installed", ""))

    # إزالة المجلد
    if path.exists():
        shutil.rmtree(path)
        print(f"  🗑️  تم إزالة المجلد: {path}")

    # إزالة من قاعدة البيانات
    del db[name]
    save_db(db)

    print(f"✅ تم إزالة: {name}")
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل install"""
    if not args:
        print("📦 qur install — تثبيت الحزم")
        print()
        print("الاستخدام:")
        print("  qur install <file.qur>              تثبيت من ملف")
        print("  qur install <file.qur> --to <dir>   تثبيت في مجلد")
        print("  qur install --list                  عرض المثبّتة")
        print("  qur install --remove <name>         إزالة حزمة")
        return 0

    target = None
    file_path = None
    list_flag = False
    remove_name = None

    i = 0
    while i < len(args):
        if args[i] == "--list":
            list_flag = True
        elif args[i] == "--remove" and i + 1 < len(args):
            remove_name = args[i + 1]
            i += 1
        elif args[i] == "--to" and i + 1 < len(args):
            target = args[i + 1]
            i += 1
        elif not args[i].startswith("-"):
            file_path = args[i]
        i += 1

    if list_flag:
        return list_installed()

    if remove_name:
        return remove_package(remove_name)

    if file_path:
        return install_package(file_path, target)

    print("❌ الاستخدام: qur install <file.qur>")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
