"""
qur doc — مولّد الوثائق
=========================

يولّد وثائق من ملفات "لسان قريش".
"""

import re
from pathlib import Path
from datetime import datetime


def extract_metadata(source):
    metadata = {'name': '', 'author': '', 'date': '', 'description': ''}
    for line in source.splitlines():
        s = line.strip()
        m = re.match(r'^;\s*📄\s*(.+)$', s)
        if m: metadata['name'] = m.group(1).strip()
        m = re.match(r'^;\s*👤\s*(.+)$', s)
        if m: metadata['author'] = m.group(1).strip()
        m = re.match(r'^;\s*📅\s*(.+)$', s)
        if m: metadata['date'] = m.group(1).strip()
        m = re.match(r'^;\s*📝\s*(.+)$', s)
        if m: metadata['description'] = m.group(1).strip()
    return metadata


def extract_functions(source):
    functions = []
    pattern = re.compile(
        r'\(تعريف\s+(\S+)\s+\(لامدا\s+\(([^)]*)\)',
        re.DOTALL
    )
    for match in pattern.finditer(source):
        اسم = match.group(1)
        معاملات = match.group(2).strip()
        start = match.start()
        قبل = source[:start].splitlines()
        وصف = ''
        for line in reversed(قبل[-3:]):
            s = line.strip()
            if s.startswith(';') and not s.startswith(';═') and not s.startswith(';─'):
                وصف = s.lstrip('; ').strip()
                break
        functions.append({'name': اسم, 'params': معاملات, 'description': وصف})
    return functions


def generate_doc(path):
    ملف = Path(path)
    source = ملف.read_text(encoding="utf-8")
    metadata = extract_metadata(source)
    functions = extract_functions(source)

    lines = []
    lines.append(f"# 📄 {metadata['name'] or ملف.stem}")
    lines.append("")
    lines.append(f"> **الملف:** `{ملف}`")
    if metadata['author']:
        lines.append(f"> **المطور:** {metadata['author']}")
    if metadata['date']:
        lines.append(f"> **التاريخ:** {metadata['date']}")
    lines.append("")

    if metadata['description']:
        lines.append("## 📝 الوصف")
        lines.append("")
        lines.append(metadata['description'])
        lines.append("")

    if functions:
        lines.append("## 📚 الدوال")
        lines.append("")
        lines.append(f"عدد الدوال: **{len(functions)}**")
        lines.append("")
        for f in functions:
            lines.append(f"### `{f['name']}`")
            lines.append("")
            if f['params']:
                lines.append(f"**المعاملات:** `{f['params']}`")
                lines.append("")
            if f['description']:
                lines.append(f"**الوصف:** {f['description']}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*تم التوليد بواسطة qur doc — {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")
    lines.append("💙 صُنع بـ 💙 في العالم العربي")
    return "\n".join(lines)


def generate_all(directory=".", output_dir=None):
    مسار = Path(directory)
    ملفات = sorted(
        f for f in مسار.glob("**/*.lisp")
        if not any(p in f.parts for p in ("build", "__pycache__", ".git", "dist"))
    )

    if not ملفات:
        print(f"❌ لا توجد ملفات .lisp في: {directory}")
        return 1

    if output_dir is None:
        output_dir = مسار / "docs"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📚 جاري توليد الوثائق...")
    print()

    seen = set()
    عداد = 0
    الفهرس = []

    for ملف in ملفات:
        try:
            اسم_فريد = ملف.stem
            if اسم_فريد in seen:
                rel = ملف.relative_to(مسار)
                اسم_فريد = str(rel.with_suffix("")).replace("/", "_").replace("\\", "_")
            seen.add(اسم_فريد)

            محتوى = generate_doc(ملف)
            out_file = output_dir / (اسم_فريد + ".md")
            out_file.write_text(محتوى, encoding="utf-8")
            print(f"  ✓ {ملف.name} → {out_file.name}")
            الفهرس.append((اسم_فريد, ملف))
            عداد += 1
        except Exception as e:
            print(f"  ❌ {ملف.name}: {e}")

    index = ["# 📚 فهرس الوثائق", ""]
    index.append(f"عدد الملفات: **{عداد}**")
    index.append("")
    for اسم_فريد, ملف in الفهرس:
        index.append(f"- [{اسم_فريد}]({اسم_فريد}.md)  —  `{ملف.name}`")
    index.append("")
    index.append("---")
    index.append("")
    index.append("💙 صُنع بـ 💙 في العالم العربي")

    (output_dir / "README.md").write_text("\n".join(index), encoding="utf-8")

    print()
    print(f"✅ تم توليد {عداد} ملف وثائق")
    print(f"📁 المخرج: {output_dir}")
    return 0


def generate_single(path, output=None):
    ملف = Path(path)
    if not ملف.exists():
        print(f"❌ الملف غير موجود: {path}")
        return 1
    محتوى = generate_doc(ملف)
    if output:
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(محتوى, encoding="utf-8")
        print(f"✅ تم التوليد: {out}")
    else:
        print(محتوى)
    return 0


def run(args):
    if not args:
        print("📚 qur doc — مولّد الوثائق")
        print()
        print("الاستخدام:")
        print("  qur doc <file>              وثائق ملف")
        print("  qur doc --all               وثائق كل المشروع")
        print("  qur doc <file> -o out.md    حفظ في ملف")
        return 0

    output = None
    directory = "."
    all_flag = False
    file_path = None

    i = 0
    while i < len(args):
        if args[i] == "--all":
            all_flag = True
        elif args[i] == "-o" and i + 1 < len(args):
            output = args[i + 1]
            i += 1
        elif args[i] == "--dir" and i + 1 < len(args):
            directory = args[i + 1]
            i += 1
        elif not args[i].startswith("-"):
            file_path = args[i]
        i += 1

    if all_flag:
        return generate_all(directory, output)
    if file_path:
        return generate_single(file_path, output)
    print("❌ الاستخدام: qur doc <file> أو qur doc --all")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]))
