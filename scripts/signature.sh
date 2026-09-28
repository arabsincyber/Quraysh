#!/bin/bash
# بصمة المشروع — إثبات الملكية

echo "═══════════════════════════════════════════════════════════"
echo "  📜 بصمة مشروع: لسان قريش (Quraysh)"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "📅 التاريخ: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo "📱 الجهاز: $(getprop ro.product.brand) $(getprop ro.product.model 2>/dev/null || echo 'Unknown')"
echo ""

echo "🔐 بصمات SHA256:"
cd "$(dirname "$0")/.."
for file in src/quraysh/*.py; do
    if [ -f "$file" ]; then
        hash=$(sha256sum "$file" | cut -c1-16)
        echo "  $hash  $file"
    fi
done
echo ""

echo "📊 آخر commit:"
git log --oneline -1 2>/dev/null || echo "  (غير متوفر)"
echo ""

echo "💙 المطور: محمد (arabsincyber)"
echo "💙 GitHub: github.com/arabsincyber/Quraysh"
echo ""

echo "═══════════════════════════════════════════════════════════"
