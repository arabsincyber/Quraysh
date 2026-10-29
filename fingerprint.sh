#!/data/data/com.termux/files/usr/bin/bash

echo "🔐 جاري إنشاء البصمة الرقمية للمشروع..."
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S %Z")

# بدء ملف البصمة
cat << HEADER > PROVENANCE.md
# 🏛️ إثبات الملكية والبصمة الرقمية (Provenance)
**المشروع:** لسان قريش (Quraysh)
**المطور:** محمد (arabsincyber)
**التاريخ:** $TIMESTAMP
**الوصف:** هذا الملف يحتوي على بصمة SHA256 لكل ملف في المشروع لإثبات سلامته وعدم تعديله.

---

## 🔑 البصمات (SHA256):
| الملف | البصمة (SHA256) |
| :--- | :--- |
HEADER

# البحث عن جميع الملفات النصية والبرمجية وحساب بصمتها
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.txt" \) -not -path "./.git/*" | sort | while read file; do
    HASH=$(sha256sum "$file" | awk '{print $1}')
    echo "| \`$file\` | \`$HASH\` |" >> PROVENANCE.md
done

echo "" >> PROVENANCE.md
echo "---" >> PROVENANCE.md
echo "*تم إنشاء هذا الملف تلقائياً بواسطة سكربت fingerprint.sh*" >> PROVENANCE.md

echo "✅ تم إنشاء البصمة الرقمية بنجاح!"
echo "💾 الملف: PROVENANCE.md"
