# 🕋 لسان قريش — حالة المشروع

## التاريخ
آخر تحديث: 2026-10-08

## آخر commit
065abda fix(playground): تحميل trained HBS-9

## البنية
- مكتبات: 11
- دوال: 108+
- اختبارات: 171
- نماذج AI: HBS-8, HBS-9

## ما أنجزناه
- ✅ 11 مكتبة عربية
- ✅ 171 اختبار ناجح
- ✅ HBS-8 (vocab 500)
- ✅ HBS-9 (vocab 1000)
- ✅ Playground (Pyodide)
- ✅ Netlify deployment
- ✅ CI على 3 إصدارات Python
- ✅ 8 منصات نشر (Twitter, TikTok, Reddit, dev.to...)

## قيد العمل
- HBS-10 (Backprop حقيقي — Transformer أقوى)

## المهمة القادمة
- HBS-10: Backprop حقيقي بدل Random Search
- إضافة HBS-10 للملعب
- تحديث README

## المسارات المهمة
- الريبو: ~/lugha/quraysh-v2
- Netlify: zingy-mochi-1a403f.netlify.app/playground
- GitHub: github.com/arabsincyber/Quraysh

## الملفات المهمة
- src/quraysh/ — 15 ملف (المكتبات + AI)
- models/habs/ — HBS-0 إلى HBS-9
- models/corpus/quran/quran.txt — القرآن
- playground/ — الملعب التفاعلي
- tests/ — 171 اختبار

## أوامر سريعة

اختبار:
    python3 -m pytest tests/ -q

تشغيل REPL:
    python3 -m src.quraysh.repl

HBS-9:
    cd models/habs && python3 habs_9.py

## ملاحظات
- أنا "محمد" (@Securityarabs) — صاحب المشروع
- البيئة: Termux على Android
- اللغة: العربية
- الأسلوب: أوامر جاهزة — بدون شرح طويل

## في محادثة جديدة
الصق هذا الملف كاملاً — وقل:
"استكمل من هنا"
