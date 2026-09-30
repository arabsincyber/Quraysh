"""
qur publish — نشر الحزم
==========================

نشر حزم "لسان قريش" إلى مستودع محلي.

الاستخدام:
    qur publish <file.qur>              نشر حزمة
    qur publish <file.qur> --repo <dir> مستودع مخصص
    qur publish --list                  عرض المنشورة
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


HOME = Path.home()
REPO_DIR = HOME / ".qur" / "repo"
REPO_INDEX = REPO_DIR / "index.json"


# ═══════════════════════════════════════════════════════════
#  قاعدة البيانات
# ═══════════════════════════════════════════════════════════

def ensure_dirs(repo=None):
    """التأكد من وجود المجلدات"""
    repo_path = Path(repo) if repo else REPO_DIR
    repo_path.mkdir(parents=True, exist_ok=True)
    index = repo_path / "index.json"
    if not index.exists():
        index.write_text("{}", encoding="utf-8")
    return repo_path


def load_index(repo=None):
    """تحميل الفهرس"""
    repo_path = ensure_dirs(repo)
    index = repo_path / "index.json"
    try:
        return json.loads(index.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_index(data, repo=None):
    """حفظ الفهرس"""
    repo_path = ensure_dirs(repo)
    index = repo_path / "index.json"
    index.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ═══════════════════════════════════════════════════════════
#  النشر
# ═══════════════════════════════════════════════════════════

def read_metadata(archive_path):
    """يقرأ metadata من الحزمة"""
    import tarfile
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            try:
                member = tar.getmember(".qur-metadata.json")
                f = tar.extractfile(member)
                return json.loads(f.read().decode("utf-8"))
            except KeyError:
                return None
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None


def publish_package(archive_path, repo=None):
    """ينشر حزمة إلى المستودع"""
    ملف = Path(archive_path)

    if not ملف.exists():
        print(f"❌ الملف غير موجود: {archive_path}")
        return 1

    print(f"📤 جاري النشر: {ملف.name}")
    print()

    # 1. قراءة metadata
    metadata = read_metadata(ملف)
    if metadata is None:
        print("❌ لا توجد بيانات وصفية في الحزمة")
        return 1

    name = metadata.get("name", ملف.stem)
    version = metadata.get("version", "1.0.0")

    print(f"  📝 الاسم:    {name}")
    print(f"  🔢 الإصدار:  {version}")
    print()

    # 2. نسخ الملف إلى المستودع
    repo_path = ensure_dirs(repo)
    target_file = repo_path / f"{name}-{version}.qur"

    try:
        shutil.copy2(ملف, target_file)
        print(f"  ✓ نسخ إلى: {target_file}")
    except Exception as e:
        print(f"❌ فشل النسخ: {e}")
        return 1

    # 3. تحديث الفهرس
    index = load_index(repo)

    if name not in index:
        index[name] = {
            "name": name,
            "versions": [],
            "latest": version,
        }

    if version not in index[name]["versions"]:
        index[name]["versions"].append(version)

    # ترتيب الإصدارات
    index[name]["versions"].sort()
    index[name]["latest"] = index[name]["versions"][-1]
    index[name]["updated"] = datetime.now().isoformat()

    save_index(index, repo)

    print()
    print(f"✅ تم النشر بنجاح!")
    print()
    print(f"  📦 المستودع: {repo_path}")
    print(f"  📊 الإصدارات: {len(index[name]['versions'])}")
    print(f"  🆕 الأحدث: {index[name]['latest']}")

    return 0


def list_published(repo=None):
    """يعرض الحزم المنشورة"""
    index = load_index(repo)

    if not index:
        print("📦 لا توجد حزم منشورة.")
        return 0

    print("📦 الحزم المنشورة:")
    print()
    print(f"  {'الاسم':<20} {'الأحدث':<10} {'الإصدارات'}")
    print("  " + "-" * 55)

    for name, info in index.items():
        latest = info.get("latest", "?")
        versions = ", ".join(info.get("versions", []))
        print(f"  {name:<20} {latest:<10} {versions}")

    print()
    print(f"  الإجمالي: {len(index)} حزمة")
    return 0


# ═══════════════════════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════════════════════

def run(args):
    """تشغيل publish"""
    if not args:
        print("📤 qur publish — نشر الحزم")
        print()
        print("الاستخدام:")
        print("  qur publish <file.qur>              نشر حزمة")
        print("  qur publish <file.qur> --repo <dir> مستودع مخصص")
        print("  qur publish --list                  عرض المنشورة")
        return 0

    repo = None
    file_path = None
    list_flag = False

    i = 0
    while i < len(args):
        if args[i] == "--list":
            list_flag = True
        elif args[i] == "--repo" and i + 1 < len(args):
            repo = args[i + 1]
            i += 1
        elif not args[i].startswith("-"):
            file_path = args[i]
        i += 1

    if list_flag:
        return list_published(repo)

    if file_path:
        return publish_package(file_path, repo)

    print("❌ الاستخدام: qur publish <file.qur>")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
